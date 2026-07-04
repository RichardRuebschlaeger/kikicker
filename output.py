"""
output.py – Ball tracking output module.

Maintains inter-frame state (previous position, score, possession, timing)
and serialises all data into the I2C protocol packet defined in the project spec:

    Field               Size        Notes
    ──────────────────────────────────────────────────────────────
    X coordinate        2 bytes     int16, mm from left edge
    Y coordinate        2 bytes     int16, mm from top edge
    Prev X coordinate   2 bytes     int16
    Prev Y coordinate   2 bytes     int16
    Field length        2 bytes     int16, mm  (e.g. 1200)
    Field width         2 bytes     int16, mm  (e.g. 680)
    Ball speed          4 bytes     float32, mm/s
    Last possession     1 byte      0 = left team, 1 = right team, 0xFF = unknown
    Current score       1 byte      high nibble = left score, low nibble = right score
    ──────────────────────────────────────────────────────────────
    Total              18 bytes

Baud rate: 9600 (configured on the smbus / I2C peripheral, not here directly).

When the ball is not detected, (x, y) are sent as (0x7FFF, 0x7FFF) = INT16_MAX,
which serves as a sentinel value the receiver can check for.

"""

import struct
import time
import math

# Try to import smbus2 for real I2C; fall back gracefully on non-Pi hardware.
try:
    import smbus2
    _I2C_AVAILABLE = True
except ImportError:
    _I2C_AVAILABLE = False

# ── I2C configuration ──────────────────────────────────────────────────────────
I2C_BUS     = 1      # Raspberry Pi default I2C bus
I2C_ADDRESS = 0x42   # Target device address – adjust to match your receiver

# Sentinel value used when the ball position is unknown (None)
_NO_BALL_SENTINEL = 0x7FFF   # INT16_MAX

# ── Persistent state (module-level so it survives between calls) ───────────────
_state = {
    "prev_pos":        None,   # (x, y) in mm, or None
    "prev_time":       None,   # time.monotonic() of previous frame
    "speed_mmps":      0.0,    # mm/s
    "last_possession": 0xFF,   # 0 = left, 1 = right, 0xFF = unknown
    "score_left":      0,      # 0-15 (fits in a nibble)
    "score_right":     0,
    # Goal cooldown: ignore re-triggers for this many seconds after a goal
    "_goal_cooldown":  0.0,
}

_GOAL_COOLDOWN_S = 2.0   # seconds to suppress repeated goal detection
_GOAL_ZONE_MM    = 20    # ball must be within this many mm of the edge to score


def _detect_goal(x: int, fieldSize_mm: tuple) -> None:
    """
    Increment the score when the ball enters a goal zone.
    Coordinates are CENTER-RELATIVE: x ranges from -(length/2) to +(length/2).
    Left goal edge is at -(length/2), right goal edge is at +(length/2).
    Uses a cooldown to avoid counting the same goal multiple times.
    Modifies _state in-place.
    """
    now = time.monotonic()
    if now < _state["_goal_cooldown"]:
        return  # still in cooldown after last goal

    half_length = fieldSize_mm[0] / 2

    if x <= -half_length + _GOAL_ZONE_MM:
        # Ball at left edge → right team scored
        _state["score_right"] = min(_state["score_right"] + 1, 15)
        _state["_goal_cooldown"] = now + _GOAL_COOLDOWN_S
        print(f"[OUTPUT] GOAL – right team scores! Score: "
              f"{_state['score_left']}:{_state['score_right']}")

    elif x >= half_length - _GOAL_ZONE_MM:
        # Ball at right edge → left team scored
        _state["score_left"] = min(_state["score_left"] + 1, 15)
        _state["_goal_cooldown"] = now + _GOAL_COOLDOWN_S
        print(f"[OUTPUT] GOAL – left team scores! Score: "
              f"{_state['score_left']}:{_state['score_right']}")


def _update_possession(x: int, fieldSize_mm: tuple) -> None:
    """
    Simple possession heuristic: whichever half of the field the ball
    is in is considered to have possession.
    Coordinates are CENTER-RELATIVE so the split point is simply 0.
    Modifies _state in-place.
    """
    _state["last_possession"] = 0 if x < 0 else 1


def _build_packet(x, y, fieldSize_mm: tuple) -> bytes:
    """
    Serialise all fields into an 18-byte packet.

        x, y          – int or None (None → sentinel 0x7FFF)
        fieldSize_mm  – (length_mm, width_mm)

    Packet layout (all little-endian):
        [0:2]   X              int16
        [2:4]   Y              int16
        [4:6]   Prev X         int16
        [6:8]   Prev Y         int16
        [8:10]  Field length   int16
        [10:12] Field width    int16
        [12:16] Ball speed     float32
        [16]    Last poss.     uint8  (0/1/0xFF)
        [17]    Score          uint8  high nibble=left, low nibble=right
    """
    # Current position
    if x is None or y is None:
        px, py = _NO_BALL_SENTINEL, _NO_BALL_SENTINEL
    else:
        px, py = int(x), int(y)

    # Previous position
    if _state["prev_pos"] is None:
        ppx, ppy = _NO_BALL_SENTINEL, _NO_BALL_SENTINEL
    else:
        ppx, ppy = int(_state["prev_pos"][0]), int(_state["prev_pos"][1])

    fl, fw   = int(fieldSize_mm[0]), int(fieldSize_mm[1])
    speed    = float(_state["speed_mmps"])
    poss     = _state["last_possession"] & 0xFF
    score    = ((_state["score_left"] & 0x0F) << 4) | (_state["score_right"] & 0x0F)

    packet = struct.pack(
        "<hhhhhh f BB",   # little-endian: 6×int16, 1×float32, 2×uint8
        px, py,
        ppx, ppy,
        fl, fw,
        speed,
        poss,
        score,
    )
    return packet   # 18 bytes


def _send_i2c(packet: bytes) -> None:
    """Write the packet to the I2C bus, or print a warning if unavailable."""
    if not _I2C_AVAILABLE:
        # Non-Pi environment – just print the hex for debugging
        print(f"[OUTPUT] I2C unavailable. Packet ({len(packet)}B): "
              f"{packet.hex(' ').upper()}")
        return

    try:
        with smbus2.SMBus(I2C_BUS) as bus:
            bus.write_i2c_block_data(I2C_ADDRESS, 0, list(packet))
    except OSError as e:
        print(f"[OUTPUT] I2C write error: {e}")


# ── Public API ─────────────────────────────────────────────────────────────────

def output_position(ballpos_mm, fieldSize_mm) -> None:
    """
    Process one frame of ball tracking data, update state, and transmit
    the I2C packet.

    Parameters
    ----------
    ballpos_mm : tuple(int, int) or None
        Current ball position in millimetres from the top-left corner of
        the playing field, or None when the ball is not detected.
    fieldSize_mm : tuple(int, int)
        (length_mm, width_mm) of the playing field. Default field is
        1200 × 680 mm.
    """
    now = time.monotonic()

    # ── Unpack position (may be None) ──────────────────────────────────────
    if ballpos_mm is not None:
        x, y = ballpos_mm
    else:
        x, y = None, None

    # ── Speed calculation ──────────────────────────────────────────────────
    if (x is not None and _state["prev_pos"] is not None
            and _state["prev_time"] is not None):
        dt = now - _state["prev_time"]
        if dt > 0:
            dx = x - _state["prev_pos"][0]
            dy = y - _state["prev_pos"][1]
            _state["speed_mmps"] = math.sqrt(dx*dx + dy*dy) / dt
        # else keep previous speed to avoid division by zero
    else:
        # No previous position or ball lost → speed unknown, keep last value
        pass

    # ── Possession & goal detection (only when ball is visible) ───────────
    if x is not None:
        _update_possession(x, fieldSize_mm)
        _detect_goal(x, fieldSize_mm)

    # ── Console debug output ───────────────────────────────────────────────
    pos_str = f"x={x} y={y}" if x is not None else "x=None y=None (ball not detected)"
    print(f"[OUTPUT] Ball: {pos_str} | "
          f"Speed: {_state['speed_mmps']:.1f} mm/s | "
          f"Poss: {'left' if _state['last_possession']==0 else 'right' if _state['last_possession']==1 else 'unknown'} | "
          f"Score L:R = {_state['score_left']}:{_state['score_right']}")

    # ── Build and transmit packet ──────────────────────────────────────────
    packet = _build_packet(x, y, fieldSize_mm)
    _send_i2c(packet)

    # ── Update state for next frame ────────────────────────────────────────
    if x is not None:
        _state["prev_pos"]  = (x, y)
        _state["prev_time"] = now
    # If ball is None we intentionally do NOT update prev_pos/prev_time so
    # that speed is recalculated correctly once the ball reappears.


def reset_score() -> None:
    """Reset the score to 0:0. Call at the start of a new game."""
    _state["score_left"]  = 0
    _state["score_right"] = 0
    print("[OUTPUT] Score reset to 0:0")


def reset_state() -> None:
    """Full state reset (new game or re-calibration)."""
    _state["prev_pos"]        = None
    _state["prev_time"]       = None
    _state["speed_mmps"]      = 0.0
    _state["last_possession"] = 0xFF
    _state["score_left"]      = 0
    _state["score_right"]     = 0
    _state["_goal_cooldown"]  = 0.0
    print("[OUTPUT] State fully reset.")