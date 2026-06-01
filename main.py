# Note to self: install through: sudo apt install python3-picamera2 python3-opencv
from picamera2 import Picamera2
import cv2
import time
import numpy as np
from output import output_position

USBCam = False

# Try USB-Camera first:
cap = cv2.VideoCapture(1, cv2.CAP_V4L2)
#if False:
if cap.isOpened():
    # MS LifeCam Camera via USB
    USBCam = True
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,240)
    #cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    #cap.set(cv2.CAP_PROP_FPS,60)
    print( cap.get( cv2.CAP_PROP_FRAME_WIDTH ) )
    print( cap.get( cv2.CAP_PROP_FRAME_HEIGHT ) )
else:
    #Internal PiCam:
    picam2 = Picamera2();  print(picam2.sensor_modes)
    # for Raspberry Pi Camera V2.1:
    #config = picam2.create_preview_configuration(
    #    raw=picam2.sensor_modes[5],
    #    main={"size": (320, 240)},
    #    controls={"FrameRate":104.0}  # Set desired frame rate
    #)
    # for Raspberry Pi Camera V3:
    config = picam2.create_preview_configuration(
        raw=picam2.sensor_modes[0],
        #main={"size": (1536, 864)},
        #main={"size": (768, 432)},
        main={"size": (384, 216)},
        controls={"FrameRate":120.13}
        )
    picam2.configure(config)
    picam2.start()

# Prepare FPS-counter:
frame_count = 0                                                                # Frame counter, 0 before first frame
lastResetTime_unix = time.time()                                               # The time when the counter was reset
lastResetFrames = 0                                                            # The value of the counter at the last reset
try:
    while True:
        frame_count += 1
        if USBCam:
            ret, rawframe_bgr = cap.read()
            if not ret:
                print("oops")
                break
        else:
            rawframe_rgb = picam2.capture_array()
            rawframe_bgr = cv2.cvtColor(rawframe_rgb, cv2.COLOR_RGB2BGR)
        selectionMask = cv2.inRange(cv2.cvtColor(rawframe_bgr,cv2.COLOR_BGR2HSV),np.array([10,120,129]),np.array([40,255,255]))
        cv2.imshow('input', rawframe_bgr)
        cv2.imshow("output", selectionMask)
        # TODO here
            
        # Calculate and print FPS:
        currentTime_unix = time.time()
        elapsedTime_unix = currentTime_unix - lastResetTime_unix
        if elapsedTime_unix > 1.0:
            fps = (frame_count - lastResetFrames) / elapsedTime_unix
            print(f"FPS: {fps:.2f}");
            lastResetTime_unix = currentTime_unix
            lastResetFrames = frame_count
        
        # Exit program loop:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    if USBCam:
        cap.release()
    else:
        picam2.stop()
    cv2.destroyAllWindows()
