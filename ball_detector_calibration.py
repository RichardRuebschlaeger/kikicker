#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 19:07:15 2026

Discoveries:
-While working on the calibrator, I discovered that the silver colour of the rods holding the figures is nearly identical to the white colour of the playing field walls. This is very effective at throwing off greyscale-thresholding. I have yet to test HSV-based selections. -richard
-In the cameras default orientation, it appears as if you could select a "sub-image" purely by pixel coordinates that fully contains the playing field, but not the space beyond the arms holding the camera, and use that to search for the field edges. Although this does reduce resilience towards other camera angles, it can be used to simplify code. Unfortunately, I can't think of a solution that automatically detects this "sub-image". -richard

@author: richard
"""
import cv2
import numpy as np

def calculateProjectionMatrix(rawframe_bgr, fieldSize_mm=(1200, 680)):
    """
    

    Parameters
    ----------
    rawframe_bgr : numpy.ndarray
        The image from which the ball position is to be determined.
    fieldSize_mm : tuple(int, int), optional
        The size of the playing field measures in millimeters. The default is (1200, 680) or 120cm x 68cm.
        Used for calibration and to calculate the size of intermediate images.

    Returns
    -------
    None.
    
    Important Links
    ---------------
    
    
    https://docs.opencv.org/3.4.20/d4/d73/tutorial_py_contours_begin.html
    https://stackoverflow.com/questions/54164630/cv-findcontours-valueerror-not-enough-values-to-unpack-expected-3-got-2
    
    From IVC - segmenting:
        file:///media/richard/Daten/Uni/WS23-24%20Introduction%20to%20Visual%20Computing/2023-12-19%20Segmentierung.pdf
        1. grayscale
        2. threshold
        3. vertical closing
        4. horizontal closing
        5. fill holes
        6. additional opening to reduce structures
        7. select largest component
        8. Find corners
        -> select largest component before filling? Then search corners?
        
    Alternatives: (Built-in corner detection)
        https://stackoverflow.com/questions/7263621/how-to-find-corners-on-a-image-using-opencv
        https://www.iditect.com/programming/opencv/python-detect-corner-of-an-image-using-opencv.html
        https://www.geeksforgeeks.org/python/python-detect-corner-of-an-image-using-opencv/
        https://stackoverflow.com/questions/7263621/how-to-find-corners-on-a-image-using-opencv
    
    Idea: Use the figure bars to detect the rough length along the x-axis, then use the walls to detect the rough length along the y-axis. Find corners afterwards.
    
    
    
    Code from IVC 23/24 exercise 10 for Manhattan Distance to corners:
        # 5. die Ecken der Box finden:
        # Suche die Eckpunkte der Box, indem über alle Pixel iteriert wird. Dabei wird die Manhattan-Distanz des Pixels zu dem jeweiligen Eckpunkt berechnet, wenn dieses Pixel in der Box
        # liegt. Wenn diese kleiner als die bisher berechnete Distanz zu dem jeweiligen Eckpunkt ist, dann wird das Pixel und dessen Distanz gespeichert. Dabei stellt die dritte Koordinate
        # die Manhattan-Distanz zum jeweiligen Eckpunkt dar. Die gemerkten Punkte werden vor der Iteration mit den Werten der gegenüberliegenden Bildecke initialisiert, da diese die am wei-
        # testen entfernten Punkte sind.
        sh0 = imgshape[0] - 1
        sh1 = imgshape[1] - 1
        kol = (sh0, sh1, sh0 + sh1)
        kor = (sh0, 0,   sh0 + sh1)
        kul = (0,   sh1, sh0 + sh1)
        kur = (0,   0,   sh0 + sh1)
        for i in range(imgshape[0]):
            for j in range(imgshape[1]):
                if(kistenpixel[i,j]):
                    aw = i + j
                    if aw < kol[2]:
                        kol = (i, j, aw)
                    aw = i + (sh1-j)
                    if aw < kor[2]:
                        kor = (i, j, aw)
                    aw = (sh0-i) + j
                    if aw < kul[2]:
                        kul = (i, j, aw)
                    aw = (sh0-i) + (sh1-j)
                    if aw < kur[2]:
                        kur = (i, j, aw)
    Variable names:
        Variables holding points follow this simple scheme: XXYY, where
            -XX is TL (top left), BL (bottom left), TR (top right) and BR (bottom right)
            -YY is FC (field corner), WC (wall corner) and SB (support beam)
            
    Getting HSV-Values:
        https://phayuth.github.io/tools/image_hsv_segmenter.html
    
    Cropping:
        https://opencv.org/cropping-an-image-using-opencv/
    
    Projection Matrix:
        https://docs.opencv.org/4.13.0/da/d6e/tutorial_py_geometric_transformations.html
    
    NOTES TO SELF:
        Access images as yx, but points are xy
        xx,yy are in image coordinates, x,y are offsets from corner
    """
    
    
    rawframe_hsv = cv2.cvtColor(rawframe_bgr, cv2.COLOR_BGR2HSV)
    
    """ Calculate the edges of the support beams """
    imgray = cv2.cvtColor(rawframe_bgr, cv2.COLOR_BGR2GRAY)
    _, imgray = cv2.threshold(imgray, 110, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3)) # Benefits from morphological opening (tested)
    imgray = cv2.erode(imgray, kernel)
    imgray = cv2.dilate(imgray, kernel)
    cv2.imshow("imgray", imgray)
    
    # Detecting field corners by testing for minimum weighted Manhattan distance within a detectDistanceX x detectDistanceY px area from the frame corners towards the center
    detectDistanceX = 55
    detectDistanceY = 55
    
    #TLSB:
    shortestEuclidianDistance = 50000;
    for x in range(detectDistanceX):
        xx = x
        for y in range(detectDistanceY):
            yy = y
            currentMD = x + (1.5 * y)                                          # Biasing against y-direction, because the point should not be more towards y than field corner
            yy = y
            #rawframe_bgr[yy, xx] = [255,0,0]
            if imgray[yy, xx] and currentMD < shortestEuclidianDistance:
                tlsb = (xx, yy)
                shortestEuclidianDistance = currentMD
                #print(f"xx={xx} yy={yy} x={x} y={y} MD={currentMD}")
                
    # TODO BLSB:
    # TODO TRSB:
    # TODO BRSB:
    
    
    """ Calculate the corners of the playing field walls: """
    # Jump to the center by 10 px on the x-axis only, so that we are past the support beams:
    tlsb = (tlsb[0] + 15, tlsb[1])
    #blsb = (blsb[0] + 15, blsb[1])
    #trsb = (trsb[0] - 15, trsb[1])
    #brsb = (brsb[0] - 15, brsb[1])
    
    # Detecting field corners by testing for minimum Manhattan distance within a detectDistanceX x detectDistanceY px area from the field wall corners towards the center
    detectDistanceX = 20
    detectDistanceY = 20
    
    # TLWC:
    shortestEuclidianDistance = 50000;
    for x in range(detectDistanceX):
        xx = x + tlsb[0]
        for y in range(detectDistanceY):
            yy = y + tlsb[1]
            currentMD = x + y
            #rawframe_bgr[yy, xx] = [255,0,0]
            if imgray[yy, xx] and currentMD < shortestEuclidianDistance:
                tlwc = (xx, yy)
                shortestEuclidianDistance = currentMD
                #print(f"xx={xx} yy={yy} x={x} y={y} MD={currentMD}")
    
    # TODO BLWC:
    # TODO TRWC:
    # TODO BRWC:
    
    # TODO jump towards center, because otherwise the surrounding area may be detected as a part of the field
    
    
    """ Calculate the corners of the playing field: """
    # Detecting field corners by testing for minimum Manhattan distance within a detectDistanceX x detectDistanceY px area from the field wall corners towards the center
    detectDistanceX = 20
    detectDistanceY = 20
    
    # Use these as placeholders for the wall corners during development:
    tlwc = (75, 52)
    blwc = (67, 184)
    trwc = (306, 64)
    brwc = (305, 198)
    
    # Selection based on color:
    imselect = cv2.inRange(rawframe_hsv, np.array([35,0,57]), np.array([120,115,147]))
    #kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3)) #No benefit from morphological closing (tested)
    #imselect = cv2.erode(imselect, kernel)
    #imselect = cv2.dilate(imselect, kernel)
    cv2.imshow("imselect", imselect)
    
    # Selection based on brightness:
    """ KNOWN GOOD CODE, use instead of above section
    imselect = cv2.cvtColor(rawframe_bgr, cv2.COLOR_BGR2GRAY)
    _, imselect = cv2.threshold(imselect, 110, 255, cv2.THRESH_BINARY_INV)
    #kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3)) #No benefit from morphological closing (tested)
    #imselect = cv2.dilate(imselect, kernel)
    #imselect = cv2.erode(imselect, kernel)
    #cv2.imshow("imselect", imselect)"""
    
    # TLFC:
    #cropped = imselect[tlw[1]:, tlw[0]:]
    shortestManhattanDistance = 50000
    for x in range(detectDistanceX):
        xx = x + tlwc[0]
        for y in range(detectDistanceY):
            currentMD = x + y
            yy = y + tlwc[1]
            #rawframe_bgr[yy, xx] = [255,0,0]
            if imselect[yy, xx] and currentMD < shortestManhattanDistance:
                tlfc = (xx, yy)
                shortestManhattanDistance = currentMD
                #print(f"xx={xx} yy={yy} x={x} y={y} MD={currentMD}")
    
    # BLFC:
    #cropped = imselect[:blw[1], blw[0]:]
    shortestManhattanDistance = 50000
    for x in range(detectDistanceX):
        xx = x + blwc[0]
        for y in range(-detectDistanceY+1, 1):
            currentMD = x - y
            yy = y + blwc[1]
            #rawframe_bgr[yy, xx] = [0,255,0]
            if imselect[yy, xx] and currentMD < shortestManhattanDistance:
                blfc = (xx, yy)
                shortestManhattanDistance = currentMD
                #print(f"xx={xx} yy={yy} x={x} y={y} MD={currentMD}")
    
    # TRFC:
    #cropped = imselect[trw[1]:, :trw[0]]
    shortestManhattanDistance = 50000
    for x in range(-detectDistanceX+1, 1):
        xx = x + trwc[0]
        for y in range(detectDistanceY):
            currentMD = y - x
            yy = y + trwc[1]
            #rawframe_bgr[yy, xx] = [0,0,255]
            if imselect[yy, xx] and currentMD < shortestManhattanDistance:
                trfc = (xx, yy)
                shortestManhattanDistance = currentMD
                #print(f"xx={xx} yy={yy} x={x} y={y} MD={currentMD}")
    
    # BRFC:
    #cropped = imselect[:brw[1], :brw[0]]
    shortestManhattanDistance = 50000
    for x in range(-detectDistanceX+1, 1):
        xx = x + brwc[0]
        for y in range(-detectDistanceY+1, 1):
            currentMD = -x - y
            yy = y + brwc[1]
            #rawframe_bgr[yy, xx] = [255,255,0]
            if imselect[yy, xx] and currentMD < shortestManhattanDistance:
                brfc = (xx, yy)
                shortestManhattanDistance = currentMD
                #print(f"xx={xx} yy={yy} x={x} y={y} MD={currentMD}")
    
    #cv2.imshow("cropped", cropped)
    #return np.eye(3)


    """ Calculating the projection matrix: """
    # Use these as placeholders for the field corners during development:
    #tlfc = tlwc
    #blfc = blwc
    #trfc = trwc
    #brfc = brwc
    
    # Generate field corner source list:
    src = np.array([tlfc, blfc, trfc, brfc], np.float32)

    # Generate corner destination list:
    dst = np.array([(0,               0),                                      #TLD (white)
                    (0,               fieldSize_mm[1]),                        #BLD (white)
                    (fieldSize_mm[0], 0),                                      #TRD (black)
                    (fieldSize_mm[0], fieldSize_mm[1])],np.float32)            #BRD (black)
                
    # Calculate perspective transformation matrix:
    P = cv2.getPerspectiveTransform(src, dst)
    return P
