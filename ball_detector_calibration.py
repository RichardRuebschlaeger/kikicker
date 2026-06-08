#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 19:07:15 2026

@author: richard
"""
import cv2

def calculateProjectionMatrix(rawframe_bgr, fieldSize_100µm=(12000, 6800)):
    """
    

    Parameters
    ----------
    rawframe_bgr : TYPE
        The image from which the ball position is to be determined.
    fieldSize_100µm : tuple(int, int), optional
        The size of the playing field measures in steps of 100 micrometers. The default is (12000, 6800) or 120cm x 68cm.
        Used for calibration and to calculate the size of intermediate images.

    Returns
    -------
    None.
    
    Important Links
    ---------------
    https://docs.opencv.org/4.13.0/da/d6e/tutorial_py_geometric_transformations.html

    """
    # TODO Calculate corners in the raw frame:
    src = None
    
    # TODO Calculate the corner destinations:
    dst = [[],
           [],
           [],
           []]
    
    
    # Calculate perspective transformation matrix:
    P = cv2.getPerspectiveTransform(src, dst)
    return P