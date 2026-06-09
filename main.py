"""
Main entry point for ball tracking system.
"""

import cv2
import sys
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
        detect_ball(frame, calibration=True)
    else:
        detect_ball(frame, calibration=False)


def main():
    """Main program loop."""
    print("=" * 50)
    print("Ball Tracking System")
    print("=" * 50)
    print("\nSelect camera type:")
    print("  1. USB Camera")
    print("  2. PiCamera (Raspberry Pi)")
    print("  3. Test Image (for Mac/development)")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    camera = None
    
    if choice == '1':
        print("\nInitializing USB Camera...")
        camera = CameraHandler(camera_type='usb', frame_width=384, frame_height=216)
        
    elif choice == '2':
        print("\nInitializing PiCamera...")
        camera = CameraHandler(camera_type='picam', frame_width=384, frame_height=216)
        
    elif choice == '3':
        print("\nTest Image Mode")
        image_path = input("Enter image path (default: Resources/2026-06-08_384x216_rawframe_only_ball.png): ").strip()
        if not image_path:
            image_path = "Resources/2026-06-08_384x216_rawframe_only_ball.png"
        camera = CameraHandler(camera_type='image', frame_width=384, frame_height=216, image_path=image_path)
    else:
        print("Invalid choice. Exiting.")
        return
    
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