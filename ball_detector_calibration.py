#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 19:07:15 2026

Discoveries:
    -While working on the calibrator, I discovered that the silver colour of the rods holding the figures is nearly identical to the white colour of the playing field walls. This is very effective at throwing off greyscale-thresholding. I have yet to test HSV-based selections. -richard
    -In the cameras default orientation, it appears as if you could select a "sub-image" purely by pixel coordinates that fully contains the playing field, but not the space beyond the arms holding the camera, and use that to search for the field edges. Although this does reduce resilience towards other camera angles, it can be used to simplify code. Unfortunately, I can't think of a solution that automatically detects this "sub-image". -richard

TODOs:
    -There are - if I am not mistaken - 8 possible rotation cases for the kicker table, but this only handles one of them; see the resource pictures. In the future, better rotation handling might be a topic worth exploring.
    -Bounds checking in helper methods

Notes:
    -Access images as yx, but points are xy
    -xx,yy are in image coordinates, x,y are offsets from corner
    Variable names:
        Variables holding points follow this simple scheme: XXYY, where
            -XX is TL (top left), BL (bottom left), TR (top right) and BR (bottom right)
            -YY is FC (field corner), WC (wall corner) and SB (support beam) or simply C for corner and D for destination.
    -Since the calibration only runs before the first frame of the game and the game only starts after calibration, the performance of the calibration does not really matter, as long as it does not take too much time.

@author: richard
"""
import cv2
import numpy as np





def calculateCornerFromTL(img_bin, startAt, detectDistance, bias=(1.0, 1.0)):
    """
    A helper-function that calculates out the nearest point (corner) of an object in a binary image starting from the top-left using Manhattan distance.

    Parameters
    ----------
    img_bin : numpy.ndarray
        The binary image to search in.
    startAt : tuple(int, int)
        The point at which to start searching at, represented as (x, y). Shall not be outside the image.
    detectDistance : tuple(int, int)
        The area from the starting point to search in, represented as (x, y). Results not guaranteed for values < 1.
    bias : tuple(double, double), optional, represented as (wx, wy)
        A weight that can be applied to the axes during the search. The default is (1.0, 1.0), which represents no bias at all. Results not guaranteed for values <= 0.

    Returns
    -------
    tuple(int, int) or None
        The coordinates of the corner or None if none was found.
    """
    shortestMD = float("inf")
    tlc = None
    for x in range(detectDistance[0]):
        xx = x + startAt[0]
        if xx < 0:
            continue
        if xx >= img_bin.shape[1]:
            break;
        for y in range(detectDistance[1]):
            yy = y + startAt[1]
            if yy < 0:
                continue
            if yy >= img_bin.shape[0]:
                break
            currentMD = (bias[0] * x) + (bias[1] * y)
            if img_bin[yy, xx] and currentMD < shortestMD:
                tlc = (xx, yy)
                shortestMD = currentMD
                #print(f"xx={xx} yy={yy} x={x} y={y} MD={currentMD}")
    return tlc


def calculateCornerFromBL(img_bin, startAt, detectDistance, bias=(1.0, 1.0)):
    """
    A helper-function that calculates out the nearest point (corner) of an object in a binary image starting from the bottom-left using Manhattan distance.

    Parameters
    ----------
    img_bin : numpy.ndarray
        The binary image to search in.
    startAt : tuple(int, int)
        The point at which to start searching at, represented as (x, y). Shall not be outside the image.
    detectDistance : tuple(int, int)
        The area from the starting point to search in, represented as (x, y). Results not guaranteed for values < 1.
    bias : tuple(double, double), optional, represented as (wx, wy)
        A weight that can be applied to the axes during the search. The default is (1.0, 1.0), which represents no bias at all. Results not guaranteed for values <= 0.

    Returns
    -------
    tuple(int, int) or None
        The coordinates of the corner or None if none was found.
    """
    shortestMD = float("inf")
    blc = None
    for x in range(detectDistance[0]):
        xx = x + startAt[0]
        if xx < 0:
            continue
        if xx >= img_bin.shape[1]:
            break;
        for y in range(-detectDistance[1] +1, 1):
            yy = y + startAt[1]
            if yy < 0:
                continue
            if yy >= img_bin.shape[0]:
                break
            currentMD = x - y
            if img_bin[yy, xx] and currentMD < shortestMD:
                blc = (xx, yy)
                shortestMD = currentMD
                #print(f"xx={xx} yy={yy} x={x} y={y} MD={currentMD}")
    return blc


def calculateCornerFromTR(img_bin, startAt, detectDistance, bias=(1.0, 1.0)):
    """
    A helper-function that calculates out the nearest point (corner) of an object in a binary image starting from the top-right using Manhattan distance.

    Parameters
    ----------
    img_bin : numpy.ndarray
        The binary image to search in.
    startAt : tuple(int, int)
        The point at which to start searching at, represented as (x, y). Shall not be outside the image.
    detectDistance : tuple(int, int)
        The area from the starting point to search in, represented as (x, y). Results not guaranteed for values < 1.
    bias : tuple(double, double), optional, represented as (wx, wy)
        A weight that can be applied to the axes during the search. The default is (1.0, 1.0), which represents no bias at all. Results not guaranteed for values <= 0.

    Returns
    -------
    tuple(int, int) or None
        The coordinates of the corner or None if none was found.
    """
    shortestMD = float("inf")
    trc = None
    for x in range(-detectDistance[0] +1, 1):
        xx = x + startAt[0]
        if xx < 0:
            continue
        if xx >= img_bin.shape[1]:
            break
        for y in range(detectDistance[1]):
            yy = y + startAt[1]
            if yy < 0:
                continue
            if yy >= img_bin.shape[0]:
                break
            currentMD = (bias[0] * -x) + (bias[1] * y)
            if img_bin[yy, xx] and currentMD < shortestMD:
                trc = (xx, yy)
                shortestMD = currentMD
                #print(f"xx={xx} yy={yy} x={x} y={y} MD={currentMD}")
    return trc


def calculateCornerFromBR(img_bin, startAt, detectDistance, bias=(1.0, 1.0)):
    """
    A helper-function that calculates out the nearest point (corner) of an object in a binary image starting from the bottom-right using Manhattan distance.

    Parameters
    ----------
    img_bin : numpy.ndarray
        The binary image to search in.
    startAt : tuple(int, int)
        The point at which to start searching at, represented as (x, y). Shall not be outside the image.
    detectDistance : tuple(int, int)
        The area from the starting point to search in, represented as (x, y). Results not guaranteed for values < 1.
    bias : tuple(double, double), optional, represented as (wx, wy)
        A weight that can be applied to the axes during the search. The default is (1.0, 1.0), which represents no bias at all. Results not guaranteed for values <= 0.

    Returns
    -------
    tuple(int, int) or None
        The coordinates of the corner or None if none was found.
    """
    shortestMD = float("inf")
    brc = None
    for x in range(-detectDistance[0] +1, 1):
        xx = x + startAt[0]
        if xx < 0:
            continue
        if xx >= img_bin.shape[1]:
            break
        for y in range(-detectDistance[1] +1, 1):
            yy = y + startAt[1]
            if yy < 0:
                continue
            if yy >= img_bin.shape[0]:
                break
            currentMD = -(bias[0] * x) - (bias[1] * y)
            if img_bin[yy, xx] and currentMD < shortestMD:
                brc = (xx, yy)
                shortestMD = currentMD
                #print(f"xx={xx} yy={yy} x={x} y={y} MD={currentMD}")
    return brc




def manualCornerCorrection(rawframe_bgr, detectedCorner, corner):
    """
    Used for manual corner correction.

    Parameters
    ----------
    rawframe_bgr : numpy.ndarray
        The image in which the corner is to be selected.
    detectedCorner : tuple(int, int) or None
        The automatically detected corner used as a hint. None if none was detected. Used to determine the displayed text.
    corner : str
        The proper name of corner to be selected. Used to determine the displayed text.

    Returns
    -------
    tuple(int, int)
        The new field corner coordinates. The same as detectedCorner if no correction was deemed necessary.
    """
    def drawCross(img, colour, center)->None:
        """
        Helper function to draw a cross. Has some out-of-bounds handling.

        Parameters
        ----------
        img : numpy.ndarray
            The picture to draw in.
        colour : numpy.ndarray
            The colour to draw with.
        center : tuple(int, int) or None
            The center of the cross. Shall not be outside the image. Only draws when not None.

        Returns
        -------
        None
        """
        if center is not None:
            sy, sx, _ = img.shape
            x, y = center
        
            xmin = max(0, center[0] - 3)
            xmax = min(sx -1, center[0] +3)
            cv2.line(img, (xmin,y), (xmax,y), colour, 1)
        
            ymin = max(0, center[1] -3)
            ymax = min(sy -1, center[1] +3)
            cv2.line(img, (x,ymin), (x,ymax), colour, 1)
    
    def click_event(event, x, y, flags, param)->None:
        """
        Helper function for handling mouse click events. Overwrites the detected corner coordinates.

        Parameters
        ----------
        event : int
            The key-event.
        x : int
            The x-coordinate of the click in the image.
        y : int
            The y-coordinate of the click in the image.
        flags : TYPE
            DESCRIPTION.
        param : TYPE
            DESCRIPTION.

        Returns
        -------
        None
        
        Point selection from displayed image:
            https://blog.finxter.com/5-best-ways-to-display-the-coordinates-of-points-clicked-on-an-image-in-opencv-python/

        """
        if event == cv2.EVENT_LBUTTONDOWN:
            nonlocal detectedCorner
            drawCross(rawframe_bgr, [0,0,255], detectedCorner)
            detectedCorner = (x, y)
            drawCross(rawframe_bgr, [0,255,0], detectedCorner)
            cv2.imshow("Manual corner correction", rawframe_bgr)
    
    print(f"Manually correct {corner} corner using left-click, confirm by pressing 'q'. If the corner is already correct, just press 'q'")
    drawCross(rawframe_bgr, [0,255,0], detectedCorner)
    cv2.imshow("Manual corner correction", rawframe_bgr)
    cv2.setMouseCallback("Manual corner correction", click_event)
    cv2.waitKey(0);
    cv2.destroyWindow("Manual corner correction")
    
    return detectedCorner




def calculateProjectionMatrix(rawframe_hsv, rawframe_bgr, fieldSize_mm=(1200, 680)):
    """
    Calculates the projection matrix required to project the passed image, so that the field corners are the new image corners. Asks for manual confirmation of the detected corners.

    Parameters
    ----------
    rawframe_hsv : numpy.ndarray
        The image in HSV from which the ball position is to be determined.
    rawframe_bgr : numpy.ndarray
        The image in BGR used for manual correction
    fieldSize_mm : tuple(int, int), optional
        The size of the playing field measures in millimeters. The default is (1200, 680) or 120cm x 68cm.
        Used for calibration and to calculate the size of intermediate images.

    Returns
    -------
    numpy.ndarray
        The projective transformation matrix.
    
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
            
    Getting HSV-Values:
        https://phayuth.github.io/tools/image_hsv_segmenter.html
    
    Cropping:
        https://opencv.org/cropping-an-image-using-opencv/
    
    Projection Matrix:
        https://docs.opencv.org/4.13.0/da/d6e/tutorial_py_geometric_transformations.html
    """
    
    
    """ Preparation: """
    # Grayscale image for wall detection:
    _, _, imgray = cv2.split(rawframe_hsv)                                     # V-channel effectively is grayscale image -> grayscale conversion should be cheap # Just found out: Appears to be not. try rawframe[:,:,2]
    _, imgray = cv2.threshold(imgray, 120, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))                  # Benefits from morphological opening (tested)
    imgray = cv2.erode(imgray, kernel)
    imgray = cv2.dilate(imgray, kernel)
    #cv2.imshow("imgray", imgray)
    
    # Field selection image based on color:                                    # No benefit from morphological closing (tested)
    imselect = cv2.inRange(rawframe_hsv, np.array([35,0,45]), np.array([120,115,147]))
    #cv2.imshow("imselect", imselect)
    
    # Field selection image based on brightness:
    # KNOWN GOOD CODE, may be used instead of section above
    #imselect = cv2.cvtColor(rawframe_bgr, cv2.COLOR_BGR2GRAY)
    #_, imselect = cv2.threshold(imselect, 110, 255, cv2.THRESH_BINARY_INV)     #No benefit from morphological closing (tested)
    #cv2.imshow("imselect", imselect)"""
    
    
    """ TLFC: """
    # TLSB:
    tlfc = None
    try:
        detectDistance = (70, 70)
        tlsb = calculateCornerFromTL(imgray, (0, 0), detectDistance, (1.0,1.5))
        # Placeholder during development:
        #tlsb = ( 33, 53)        # 33, 53     41, 45                            # After someone moved the camera / before someone moved the camera
    
        # TLWC:
        # Jump to the center by 25px on the x-axis only, so that we are past the support beams:
        tlsb = (tlsb[0] + 25, tlsb[1])
        detectDistance = (25, 25)
        tlwc = calculateCornerFromTL(imgray, tlsb, detectDistance)
        # Placeholder during development:
        #tlwc = ( 71,  51)       # 69,  51    71,  47                           # After someone moved the camera / before someone moved the camera

        # TLFC
        # Jump towards center, because otherwise the surrounding area may be detected as a part of the field:
        tlwc = (tlwc[0] + 5, tlwc[1] + 5)
        detectDistance = (20, 20)
        tlfc = calculateCornerFromTL(imselect, tlwc, detectDistance)
    except:
        print("oops at TLFC")
    finally:
        # Manual correction:
        tlfc = manualCornerCorrection(rawframe_bgr, tlfc, "top left")


    """ BLFC: """
    try:
        # BLSB:
        detectDistance = (70, 70)
        blsb = calculateCornerFromBL(imgray, (0, imgray.shape[0] -1), detectDistance, (1.0,1.5)) # Actually top left of wall corner
        # Placeholder during development:
        #blsb = ( 20,181)        # 21,188     20,181                            # After someone moved the camera / before someone moved the camera

        # BLWC:
        # Jump to the center by 25px on the x-axis only, so that we are past the support beams:
        blsb = (blsb[0] + 25, blsb[1])
        detectDistance = (25, 25)
        blwc = calculateCornerFromTL(imgray, blsb, detectDistance)
        # Placeholder during development:
        #blwc = ( 58, 192)       # 58, 192    59, 188                           # After someone moved the camera / before someone moved the camera
    
        # BLFC:
        # Jump towards center, because otherwise the surrounding area may be detected as a part of the field:
        blwc = (blwc[0] + 5, blwc[1])                                          # upwards offset causes the field corner to move as well (little height difference)
        detectDistance = (20, 20)
        blfc = calculateCornerFromBL(imselect, blwc, detectDistance)
    except:
        print("oops at BLFC")
    finally:
        # Manual correction:
        blfc = manualCornerCorrection(rawframe_bgr, blfc, "bottom left")
    
    
    """ TRFC: """
    try:
        # TRSB:
        detectDistance = (70, 70)
        trsb = calculateCornerFromTR(imgray, (imgray.shape[1] -16, 0), detectDistance) # Needs to start 15px left from the right corner, because otherwise it will detect the cable conduit underneath the window
        # Placeholder during development:
        #trsb = (339, 62)        #339, 62    338, 58                            # After someone moved the camera / before someone moved the camera
    
        # TRWC:
        # Jump to the center by 25px on the x-axis only, so that we are past the support beams:
        trsb = (trsb[0] - 25, trsb[1])
        detectDistance = (25, 25)
        trwc = calculateCornerFromTR(imgray, trsb, detectDistance)
        if trwc is None:
            trwc = calculateCornerFromBR(imgray, trsb, detectDistance)
        # Placeholder during development:
        #trwc = (309,  62)       #309,  61   312,  60                           # After someone moved the camera / before someone moved the camera
    
        # TRFC:
        # Jump towards center, because otherwise the surrounding area may be detected as a part of the field:
        trwc = (trwc[0] - 5, trwc[1] + 5)
        detectDistance = (20, 20)
        trfc = calculateCornerFromTR(imselect, trwc, detectDistance)
    except:
        print("oops at TRFC")
    finally:
        # Manual correction:
        trfc = manualCornerCorrection(rawframe_bgr, trfc, "top right")
    
    
    """ BRFC: """
    try:
        # BRSB:
        detectDistance = (70, 70)
        brsb = calculateCornerFromBR(imgray, (imgray.shape[1] -16, imgray.shape[0] -1), detectDistance)
        # Use these as placeholders for the wall corners during development:
        #brsb = (335,210)        #335,210    338,206                            # After someone moved the camera / before someone moved the camera
    
        # BRWC:
        # Jump to the center by 25px on the x-axis only, so that we are past the support beams:
        brsb = (brsb[0] - 25, brsb[1])
        detectDistance = (25, 25)
        brwc = calculateCornerFromBR(imgray, brsb, detectDistance)
        # Use these as placeholders for the wall corners during development:
        #brwc = (307, 202)       #307, 203   307, 202                           # After someone moved the camera / before someone moved the camera
    
        # BRFC:
        # Jump towards center, because otherwise the surrounding area may be detected as a part of the field:
        brwc = (brwc[0] - 5, brwc[1] - 6)
        detectDistance = (20, 20)
        brfc = calculateCornerFromBR(imselect, brwc, detectDistance)
    except:
        print("oops at BRFC")
    finally:
        # Manual correction:
        brfc = manualCornerCorrection(rawframe_bgr, brfc, "bottom right")
    
    
    """ Calculating the projection matrix: """
    # Use these as placeholders for the field corners during development:
    #tlfc = ( 74,  53)      # 78,  57    80,  54                                # After someone moved the camera / before someone moved the camera
    #blfc = ( 65, 187)      # 68, 186    69, 182
    #trfc = (305,  65)      #301,  68   303,  67
    #brfc = (303, 197)      #299, 196   300, 195
    print(tlfc, blfc, trfc, brfc)
    
    # Generate field corner source list (assuming the corners are found):
    #print(tlfc, blfc, trfc, brfc)
    src = np.array([tlfc, blfc, trfc, brfc], dtype=np.float32)

    # Generate corner destination list:
    dst = np.array([(0,               0),                                      #TLD (white)
                    (0,               fieldSize_mm[1]),                        #BLD (white)
                    (fieldSize_mm[0], 0),                                      #TRD (black)
                    (fieldSize_mm[0], fieldSize_mm[1])],                       #BRD (black)
                   dtype = np.float32)
                
    # Calculate perspective transformation matrix:
    #P = np.eye(3)
    P = cv2.getPerspectiveTransform(src, dst)
    return P
