"""
Main entry point for ball tracking system.
"""

import cv2
import time
from camera_handler import CameraHandler
from ball_detector import detect_ball


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
    
    try:
        if choice == '1':
            print("\nCapturing single frame. Press any key to stop")
            rawframe_hsv = camera.capture()
            detect_ball(rawframe_hsv, True)
            # TODO pause here
            cv2.waitKey(0)
            
        elif choice == '2':
            print("\nCapturing continous frames. Press Ctrl+C to stop.")
            frame_number = 1
            lastResetFrames = 1
            lastResetTime_unix = time.time()
            while True:
                rawframe_hsv = camera.capture()
                detect_ball(rawframe_hsv, frame_number == 1)
                frame_number += 1
                
                # Calculate and print FPS:
                currentTime_unix = time.time()
                elapsedTime_unix = currentTime_unix - lastResetTime_unix
                if elapsedTime_unix > 1.0:
                    fps = (frame_number - lastResetFrames) / elapsedTime_unix
                    print(f"FPS: {fps:.2f}");
                    lastResetTime_unix = currentTime_unix
                    lastResetFrames = frame_number
                
        elif choice == '3':
            try:
                num_frames = int(input("Enter number of frames to capture: "))
                print(f"\nCapturing {num_frames} frames...")
            except ValueError:
                print("Invalid number, using default 100 frames")
                num_frames = 100
            lastResetFrames = 0
            lastResetTime_unix = time.time()
            for frame_number in range(num_frames):
                rawframe_hsv = camera.capture()
                detect_ball(rawframe_hsv, frame_number == 0)
                
                # Calculate and print FPS:
                currentTime_unix = time.time()
                elapsedTime_unix = currentTime_unix - lastResetTime_unix
                if elapsedTime_unix > 1.0:
                    fps = (frame_number - lastResetFrames) / elapsedTime_unix
                    print(f"FPS: {fps:.2f}");
                    lastResetTime_unix = currentTime_unix
                    lastResetFrames = frame_number
                    
        else:
            print("Invalid option")
    except KeyboardInterrupt:                                                  # Ctrl+C functionality
        print("Terminating program")
    
    # Cleanup
    camera.release()
    cv2.destroyAllWindows()
    print("Program terminated")


if __name__ == "__main__":
    main()