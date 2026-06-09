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
    fieldSize_100µm : tuple(int, int), optional
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
    grey = cv2.cvtColor(rawframe_bgr, cv2.BGR2GRAY)
    _, gray = cv2.threshold(grey, 127, 255, 0)
    _, src, _ = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # TODO Calculate the corner destinations:
    dst = [[0,                  0],               #TL
           [fieldSize_mm[0],    0],               #TR
           [0,                  fieldSize_mm[1]], #BL
           [fieldSize_mm[0],    fieldSize_mm[1]]] #BR
    
    
    # Calculate perspective transformation matrix:
    P = cv2.getPerspectiveTransform(src, dst)
    return P