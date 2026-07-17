#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 17:39:50 2026

Discoveries:
    -print() costs a lot of performance apparently

@author: richard
"""
import cv2
import numpy as np

def detect_ball(rawframe_hsv, projection, fieldSize_mm=(1200,680)):
    """
    Calculates the position of at most one orange ball on the playing field. The position relative to the center of the playing field.
    White/left is negative x and black/right is positive x. Top half is negative y and bottom half is positive y, when looking at the field
    so that white is left and black is right.
    
    Parameters
    ----------
    rawframe_hsv : numpy.ndarray
        The image from which the ball position is to be determined in HSV.
        NOTE: Operating under the assumption that there is only one ball (orange object) or none.
    projection : numpy.ndarray
        The projection matrix used to convert coordinates from pixel coordiate space to field coordinate space.
    fieldSize_mm : tuple(int, int), optional
        The size of the playing field measures in millimeters. The default is (1200, 680) or 120cm x 68cm.

    Returns
    -------
    tuple(int, int) or None
        x and y coordinates of of the balls center, if a ball is detected, None otherwise
    
    Important Links
    ---------------
    https://docs.opencv.org/4.13.0/da/d6e/tutorial_py_geometric_transformations.html
    https://learnopencv.com/find-center-of-blob-centroid-using-opencv-cpp-python/
    https://stackoverflow.com/questions/45817325/opencv-python-cv2-perspectivetransform
    """
    # Display raw frame and the selection mask from the raw frame:
    rawSelectionMask = cv2.inRange(rawframe_hsv, np.array([10,85,129]), np.array([40,255,255]))
    #cv2.imshow("raw frame", cv2.cvtColor(rawframe_hsv, cv2.COLOR_HSV2BGR))
    cv2.imshow("raw frame selection", rawSelectionMask)
    
    # Project and resize image:
    #projectedFrame_hsv = cv2.warpPerspective(rawframe_hsv, projection, fieldSize_mm);
    #cv2.imshow("projected frame", cv2.cvtColor(projectedFrame_hsv, cv2.COLOR_HSV2BGR))
    
    # Get ball position from projected image:
    #projectedSelectionMask = cv2.inRange(projectedFrame_hsv, np.array([10,85,129]), np.array([40,255,255]))
    projectedSelectionMask = cv2.warpPerspective(rawSelectionMask, projection, fieldSize_mm)
    cv2.imshow("projected frame selection", projectedSelectionMask)
    M = cv2.moments(rawSelectionMask)
    Mm00 = M["m00"]
    #print(Mm00)
    if Mm00 == 0.0:
        # No orange pixels found -> ball not detected
        ballpos_mm = None
    elif Mm00 > 1000000:
        # Lots of orange pixels -> hands over the field, can't find ball:
        ballpos_mm = None
    else:
        # Calculate ball position in pixel coordinates (Mm00 normally around 330k):
        x = int(M["m10"] / Mm00)
        y = int(M["m01"] / Mm00)
        #print(f"x={x} y={y}")
        px,py,pz = projection @ [x,y,1]
        x = px / pz
        y = py / pz
        #print(f"x={x} y={y}")
        
        # Convert pixel coordinates to field coordinates:
        ballpos_mm = (x - (fieldSize_mm[0] / 2.0), y - (fieldSize_mm[1] / 2.0))
 
    # Return ball position (None if not detected):
    return ballpos_mm