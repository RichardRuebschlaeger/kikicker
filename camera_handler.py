"""
Camera handler for USB and PiCamera with FPS tracking.
"""

import cv2
import time
from picamera2 import Picamera2


class CameraHandler:
    def __init__(self, camera_type=None, frame_width=384, frame_height=216):
        """
        Initialize camera handler.
        
        Parameters
        ----------
        camera_type : str or None
            'usb', 'picam', or None for auto-detection
        frame_width : int
            Frame width (default 384 for PiCam compatibility)
        frame_height : int
            Frame height (default 216 for PiCam compatibility)
        """
        self.camera_type = camera_type
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.cap = None
        self.picam2 = None
        
        # FPS tracking variables
        self.frame_count = 0
        self.last_reset_time = time.time()
        self.last_reset_frames = 0
        self.current_fps = 0.0
        
    def _detect_camera_type(self):
        """Auto-detect available camera without releasing."""
        # Try USB camera first
        cap = cv2.VideoCapture(1, cv2.CAP_V4L2)
        if cap.isOpened():
            # Test read to ensure it's working
            ret, _ = cap.read()
            cap.release()
            if ret:
                return 'usb'
        return 'picam'
    
    def initialize(self):
        """Initialize camera based on type."""
        # Auto-detect if not specified
        if self.camera_type is None:
            self.camera_type = self._detect_camera_type()
            print(f"Auto-detected camera: {self.camera_type}")
        
        if self.camera_type == 'usb':
            self.cap = cv2.VideoCapture(1, cv2.CAP_V4L2)
            if not self.cap.isOpened():
                return False
            
            # Set frame size
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            
            # Verify actual frame size
            actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            
            print(f"USB Camera initialized: requested {self.frame_width}x{self.frame_height}")
            print(f"Actual: {actual_width}x{actual_height}")
            
            # Update dimensions to actual values
            self.frame_width = int(actual_width)
            self.frame_height = int(actual_height)
            return True
            
        elif self.camera_type == 'picam':
            self.picam2 = Picamera2()
            print(self.picam2.sensor_modes)
            
            # Use original dimensions for PiCam
            config = self.picam2.create_preview_configuration(
                raw=self.picam2.sensor_modes[0],
                main={"size": (self.frame_width, self.frame_height)},
                controls={"FrameRate": 120.13}
            )
            self.picam2.configure(config)
            self.picam2.start()
            print(f"PiCamera initialized: {self.frame_width}x{self.frame_height}")
            return True
            
        return False
    
    def capture(self):
        """Capture a single frame."""
        if self.camera_type == 'usb':
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to capture from USB camera")
                return None
            return frame
        else:
            rgb = self.picam2.capture_array()
            return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    
    def capture_continuous(self, callback, max_frames=None):
        """
        Capture continuous frames and process with callback.
        
        Parameters
        ----------
        callback : function
            Function to call with each frame (receives frame and frame_number)
        max_frames : int or None
            Maximum number of frames to capture (None for infinite)
        """
        frame_number = 0
        self.frame_count = 0
        self.last_reset_time = time.time()
        self.last_reset_frames = 0
        
        try:
            while True:
                frame = self.capture()
                if frame is None:
                    break
                
                # Call callback with frame
                callback(frame, frame_number)
                
                # Update FPS
                self.update_fps()
                
                frame_number += 1
                
                # Check if we've reached max frames
                if max_frames and frame_number >= max_frames:
                    print(f"Captured {max_frames} frames, stopping")
                    break
                    
        except KeyboardInterrupt:
            print("\nCapture interrupted by user")
    
    def capture_single(self):
        """Capture and return a single frame."""
        return self.capture()
    
    def update_fps(self):
        """Update FPS calculation and print if 1 second has passed."""
        self.frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - self.last_reset_time
        
        if elapsed_time > 1.0:
            self.current_fps = (self.frame_count - self.last_reset_frames) / elapsed_time
            print(f"FPS: {self.current_fps:.2f}")
            self.last_reset_time = current_time
            self.last_reset_frames = self.frame_count
        
        return self.current_fps
    
    def get_fps(self):
        """Get current FPS value."""
        return self.current_fps
    
    def release(self):
        """Release camera resources."""
        if self.cap:
            self.cap.release()
        if self.picam2:
            self.picam2.stop()
        print("Camera released")