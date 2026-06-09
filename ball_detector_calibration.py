#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 19:07:15 2026

@author: richard
"""
import cv2

def calculateProjectionMatrix(rawframe_bgr, fieldSize_mm=(1200, 680)):
    """
    

    Parameters
    ----------
    rawframe_bgr : TYPE
        The image from which the ball position is to be determined.
    fieldSize_mm : tuple(int, int), optional
        The size of the playing field measures in millimeters. The default is (1200, 680) or 120cm x 68cm.
        Used for calibration and to calculate the size of intermediate images.

    Returns
    -------
    None.
    
    Important Links
    ---------------
    https://docs.opencv.org/4.13.0/da/d6e/tutorial_py_geometric_transformations.html
    https://docs.opencv.org/3.4.20/d4/d73/tutorial_py_contours_begin.html
    """
    # Calculate corners in the raw frame:
    # NOTE: No guarantee for exactly 4 results, but should be (unless camera excessively tilted)
    grey = cv2.cvtColor(rawframe_bgr, cv2.BGR2GREY)
    _, gray = cv2.threshold(grey, 127, 255, 0)
    im2, src, _ = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    assert len(src) == 4, f"Got {len(src)} field corners, but should be exactly 4"
    cv2.imshow("corners", im2)
    
    # Automatically determine corner destination based on corner source quadrant:
    # NOTE: +x rightwards, +y downwards
    dst=[]
    shape = rawframe_bgr.shape
    for corner in src:
        if corner[0] < (shape[0] / 2.0):
            if corner[1] < (shape[1] / 2.0):
                dst += (0,        0)                                           #TL(white)
            else:
                dst += (0,        shape[1])                                    #BL(white)
        else:
            if corner[1] < (shape[1] / 2.0):
                dst += (shape[0], 0)                                           #TR(black)
            else:
                dst += (shape[0], shape[1])                                    #BR(black)
                
    # Calculate perspective transformation matrix:
    P = cv2.getPerspectiveTransform(src, dst)
    return P