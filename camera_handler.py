"""
Camera handler for USB, PiCamera, or test image.
"""

import cv2
import time

# Try to import picamera2 (only works on Raspberry Pi)
try:
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False


class CameraHandler:
    def __init__(self, camera_type=None, frame_width=384, frame_height=216, image_path=None):
        self.camera_type = camera_type
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.image_path = image_path
        self.test_image = None
        self.cap = None
        self.picam2 = None
        
        # FPS tracking
        self.frame_count = 0
        self.last_reset_time = time.time()
        self.last_reset_frames = 0
        self.current_fps = 0.0
        
    def initialize(self):
        """Initialize camera based on type."""
        
        # Image mode
        if self.camera_type == 'image':
            self.test_image = cv2.imread(self.image_path)
            if self.test_image is not None:
                self.test_image = cv2.resize(self.test_image, (self.frame_width, self.frame_height))
                print(f"Image loaded: {self.image_path}")
                return True
            print(f"Failed to load image: {self.image_path}")
            return False
        
        # USB camera
        if self.camera_type == 'usb':
            self.cap = cv2.VideoCapture(1, cv2.CAP_V4L2)
            if self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
                print(f"USB Camera initialized")
                return True
            print("USB Camera failed")
            return False
        
        # PiCamera
        if self.camera_type == 'picam':
            if PICAMERA_AVAILABLE:
                self.picam2 = Picamera2()
                config = self.picam2.create_preview_configuration(
                    main={"size": (self.frame_width, self.frame_height)}
                )
                self.picam2.configure(config)
                self.picam2.start()
                print(f"PiCamera initialized")
                return True
            print("PiCamera not available")
            return False
        
        # Auto-detect
        if self.camera_type is None:
            # Try USB first
            test_cap = cv2.VideoCapture(1, cv2.CAP_V4L2)
            if test_cap.isOpened():
                test_cap.release()
                return self.initialize(camera_type='usb')
            # Then PiCamera
            if PICAMERA_AVAILABLE:
                return self.initialize(camera_type='picam')
            print("No camera found")
            return False
    
    def capture(self):
        """Capture a single frame."""
        if self.test_image is not None:
            return self.test_image.copy()
        
        if self.cap is not None:
            ret, frame = self.cap.read()
            return frame if ret else None
        
        if self.picam2 is not None:
            rgb = self.picam2.capture_array()
            return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        
        return None
    
    def capture_single(self):
        return self.capture()

    def _update_fps(self):
        """Update the FPS counter."""
        self.frame_count += 1
        now = time.time()
        elapsed = now - self.last_reset_time
        if elapsed >= 1.0:
            self.current_fps = (self.frame_count - self.last_reset_frames) / elapsed
            self.last_reset_time = now
            self.last_reset_frames = self.frame_count

    def capture_continuous(self, callback, max_frames=None):
        """
        Capture frames continuously and call callback for each one.

        Parameters
        ----------
        callback : callable
            Function called with (frame, frame_number) for each captured frame.
            Return False from the callback to stop early.
        max_frames : int or None
            Maximum number of frames to capture. None means run until
            Ctrl+C or the callback returns False.
        """
        frame_number = 0
        print("Starting continuous capture. Press Ctrl+C to stop.")

        try:
            while True:
                if max_frames is not None and frame_number >= max_frames:
                    print(f"Reached {max_frames} frames, stopping.")
                    break

                frame = self.capture()
                if frame is None:
                    print("Warning: failed to capture frame, skipping.")
                    continue

                self._update_fps()

                result = callback(frame, frame_number)
                frame_number += 1

                # Allow the callback to signal a stop by returning False
                if result is False:
                    print("Callback requested stop.")
                    break

        except KeyboardInterrupt:
            print(f"\nCapture stopped by user after {frame_number} frames "
                  f"(avg {self.current_fps:.1f} FPS).")

    def release(self):
        if self.cap:
            self.cap.release()
        if self.picam2:
            self.picam2.stop()