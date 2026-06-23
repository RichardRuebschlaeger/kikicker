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

def detect_ball(rawframe_bgr, calibration, fieldSize_mm=(1200,680)):
    """
    TODO: Case where no ball is detected
    TODO: Offset is still from TL corner, should be center

    Parameters
    ----------
    rawframe_bgr : numpy.ndarray
        The image from which the ball position is to be determined.
        NOTE: Operating under the assumption that there is only one ball (orange object).
    calibration : TYPE
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
    if type(calibration)==bool:
        global cameraCalibrationMatrix
        if calibration:
            cameraCalibrationMatrix = calculateProjectionMatrix(rawframe_bgr, fieldSize_mm)
    elif type(calibration)==np.ndarray:
        cameraCalibrationMatrix = calibration
    
    # Display raw frame and the selection mask from the raw frame:
    rawSelectionMask = cv2.inRange(cv2.cvtColor(rawframe_bgr,cv2.COLOR_BGR2HSV),np.array([10,120,129]),np.array([40,255,255]))
    cv2.imshow("raw frame", rawframe_bgr)
    cv2.imshow("raw frame selection", rawSelectionMask)
    
    # Project and resize image:
    projectedFrame_bgr = cv2.warpPerspective(rawframe_bgr, cameraCalibrationMatrix, fieldSize_mm);
    cv2.imshow("projected frame", projectedFrame_bgr)
    
    # Get ball position from projected image:
    projectedSelectionMask = cv2.inRange(cv2.cvtColor(projectedFrame_bgr,cv2.COLOR_BGR2HSV),np.array([10,120,129]),np.array([40,255,255]))
    cv2.imshow("projected frame selection", projectedSelectionMask)
    M = cv2.moments(projectedSelectionMask)
    x = int(M["m10"] / M["m00"])
    y = int(M["m01"] / M["m00"])
    
    # Send ball position via output function:
    output_position((x, y), fieldSize_mm)
    cv2.waitKey(0)
    cv2.destroyAllWindows()