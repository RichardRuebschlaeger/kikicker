#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 17:39:50 2026

@author: richard
"""
import cv2
import numpy as np
from output import output_position
from ball_detector_calibration import calculateProjectionMatrix

def detect_ball(rawframe_hsv, calibration, fieldSize_mm=(1200,680)):
    """
    Calculates the position of at most one orange ball on the playing field. The position relative to the center of the playing field.
    White/left is negative x and black/right is positive x. Top half is negative y and bottom half is positive y, when looking at the field
    so that white is left and black is right.
    
    This function calls the output_position-function and transfers relevant values. Passes None as the ball position if hands or arms or no
    ball is detected.

    Parameters
    ----------
    rawframe_hsv : numpy.ndarray
        The image from which the ball position is to be determined in HSV.
        NOTE: Operating under the assumption that there is only one ball (orange object) or none.
    calibration : bool or numpy.ndarray
        Calibration refers to the (re-) calculation of the projection matrix used to level the playing field image.
        Set to true to (re-) calculate; set to false to use a previously calculated one (if it exists); or set to matrix to be used instead.
    fieldSize_mm : tuple(int, int), optional
        The size of the playing field measures in millimeters. The default is (1200, 680) or 120cm x 68cm.
        Used for calibration and to calculate the size of intermediate images.

    Returns
    -------
    None.
    
    Important Links
    ---------------
    https://docs.opencv.org/4.13.0/da/d6e/tutorial_py_geometric_transformations.html
    https://learnopencv.com/find-center-of-blob-centroid-using-opencv-cpp-python/
    """
    # What to do?
    if type(calibration) == bool:
        global cameraCalibrationMatrix
        if calibration:
            cameraCalibrationMatrix = calculateProjectionMatrix(rawframe_hsv, fieldSize_mm)
    elif type(calibration) == np.ndarray:
        cameraCalibrationMatrix = calibration
    
    # Display raw frame and the selection mask from the raw frame:
    #rawSelectionMask = cv2.inRange(rawframe_hsv, np.array([10,120,129]), np.array([40,255,255]))
    cv2.imshow("raw frame", cv2.cvtColor(rawframe_hsv, cv2.COLOR_HSV2BGR))
    #cv2.imshow("raw frame selection", rawSelectionMask)
    
    # Project and resize image:
    projectedFrame_hsv = cv2.warpPerspective(rawframe_hsv, cameraCalibrationMatrix, fieldSize_mm);
    cv2.imshow("projected frame", cv2.cvtColor(projectedFrame_hsv, cv2.COLOR_HSV2BGR))
    
    # Get ball position from projected image:
    projectedSelectionMask = cv2.inRange(projectedFrame_hsv, np.array([10,85,129]), np.array([40,255,255]))
    cv2.imshow("projected frame selection", projectedSelectionMask)
    M = cv2.moments(projectedSelectionMask)
    Mm00 = M["m00"]
    print(Mm00)
    if Mm00 == 0.0:
        # No orange pixels found -> ball not detected
        ballpos = None
    elif Mm00 > 1000000:
        # Lots of orange pixels -> hands over the field, can't find ball:
        ballpos = None
    else:
        # Calculate ball position in pixel coordinates (Mm00 normally around 330k):
        x = int(M["m10"] / Mm00)
        y = int(M["m01"] / Mm00)
        print(f"x={x} y={y}")
        
        # Convert pixel coordinates to field coordinates:
        ballpos = (x - (fieldSize_mm[0] / 2.0), y - (fieldSize_mm[1] / 2.0))
 
    # Send ball position via output function (None if not detected):
    output_position(ballpos, fieldSize_mm)