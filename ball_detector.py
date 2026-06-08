#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 17:39:50 2026

@author: richard
"""
import cv2
import numpy as np
from output import output_position

def detect_ball(rawframe_bgr, calibrate):
    """
    

    Parameters
    ----------
    rawframe_bgr : TYPE
        The image from which the ball position is to be determined.
    calibrate : TYPE
        Calibration refers to the (re-) calculation of the projection matrix used to level the playing field image.
        Set to true to (re-) calculate; set to false to use a previously calculated one (if it exists) or set matrix to be used.

    Returns
    -------
    None.

    """
    global cameraCalibrationMatrix
    if calibrate:
        #TODO: Calculate projection matrix:
        cameraCalibrationMatrix = None #Set to real value later
    selectionMask = cv2.inRange(cv2.cvtColor(rawframe_bgr,cv2.COLOR_BGR2HSV),np.array([10,120,129]),np.array([40,255,255]))
    cv2.imshow("raw frame", rawframe_bgr)
    cv2.imshow("raw frame selection", selectionMask)
    
    # TODO project and crop image
    # TODO get ball position from projected image
    # TODO send ball position via output function
    #output_position(x, y)