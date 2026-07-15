"""
Camera handler for USB, PiCamera, or test image.
"""

import cv2

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
        self.test_image_bgr = None
        self.test_image_hsv = None
        self.cap = None
        self.picam2 = None
        
    def initialize(self):
        """Initialize camera based on type."""
        
        # Image mode
        if self.camera_type == 'image':
            self.test_image_bgr = cv2.imread(self.image_path)
            if self.test_image_bgr is not None:
                self.test_image_bgr = cv2.resize(self.test_image_bgr, (self.frame_width, self.frame_height))
                self.test_image_hsv = cv2.cvtColor(self.test_image_bgr, cv2.COLOR_BGR2HSV)
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
                print("USB Camera initialized")
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
                print("PiCamera initialized")
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
    
    def captureBGR(self):
        """Capture a single frame."""
        if self.test_image_bgr is not None:
            return self.test_image_bgr.copy()
        
        if self.cap is not None:
            ret, frame = self.cap.read()
            return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) if ret else None     # Assunimg RGB color for USB-cam
        
        if self.picam2 is not None:
            rgb = self.picam2.capture_array()
            return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    
        
    def captureHSV(self):
        """Capture a single frame."""
        if self.test_image_hsv is not None:
            return self.test_image_hsv.copy()
        
        if self.cap is not None:
            ret, frame = self.cap.read()
            return cv2.cvtColor(frame, cv2.COLOR_RGB2HSV) if ret else None     # Assunimg RGB color for USB-cam
        
        if self.picam2 is not None:
            rgb = self.picam2.capture_array()
            return cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        

    def release(self):
        if self.cap:
            self.cap.release()
        if self.picam2:
            self.picam2.stop()