#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for ball tracking system.
"""

import cv2
from camera_handler import CameraHandler
from ball_detector import detect_ball


def process_frame(frame, frame_number):
    """
    Process a single frame for ball detection.
    
    Parameters
    ----------
    frame : numpy.ndarray
        The image frame to process
    frame_number : int
        Frame number (0-indexed)
    """
    # Must be true for first/only frame, can be false afterwards
    if frame_number == 0:
        print("Calibrating on first frame...")
        detect_ball(frame, calibrate=True)
    else:
        detect_ball(frame, calibrate=False)


def main():
    """Main program loop."""
    # Auto-detect camera type (switch case style)
    camera_type = None
    
    # Try USB first
    test_usb = cv2.VideoCapture(1, cv2.CAP_V4L2)
    if test_usb.isOpened():
        camera_type = 'usb'
        test_usb.release()
        print("USB camera detected")
    else:
        camera_type = 'picam'
        print("PiCamera detected")
    
    # Initialize camera
    camera = CameraHandler(camera_type=camera_type, frame_width=320, frame_height=240)
    
    if not camera.initialize():
        print("Failed to initialize camera")
        return
    
    print("\nOptions:")
    print("  1. Capture single frame only")
    print("  2. Capture continuous frames")
    print("  3. Capture limited frames (e.g., 100 frames)")
    
    choice = input("\nSelect option (1/2/3): ").strip()
    
    if choice == '1':
        # Capture single frame only
        print("\nCapturing single frame...")
        frame = camera.capture_single()
        if frame is not None:
            process_frame(frame, 0)
        else:
            print("Failed to capture frame")
            
    elif choice == '2':
        # Capture continuous frames
        print("\nCapturing continuous frames. Press Ctrl+C to stop.")
        camera.capture_continuous(process_frame, max_frames=None)
        
    elif choice == '3':
        # Capture limited frames
        try:
            num_frames = int(input("Enter number of frames to capture: "))
            print(f"\nCapturing {num_frames} frames...")
            camera.capture_continuous(process_frame, max_frames=num_frames)
        except ValueError:
            print("Invalid number, using default 100 frames")
            camera.capture_continuous(process_frame, max_frames=100)
    
    else:
        print("Invalid option")
    
    # Cleanup
    camera.release()
    cv2.destroyAllWindows()
    print("Program terminated")


if __name__ == "__main__":
    main()