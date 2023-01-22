import cv2 as cv
import logging

#creating and configuring logger
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename = "filelogger.log", level = logging.DEBUG, format = LOG_FORMAT, filemode = 'w')
logger = logging.getLogger()

def area_check(x1:int, y1:int, x2:int, y2:int, index:list, contours:list) -> tuple:
    """
    Returns tuple after checking if the area of the previously found bounding rectangle is smaller than the other closed contours
    
    Parameters
    ----------
    x1 : int
        top-left x coordinate
    y1 : int
        top-left y coordinate
    x2 : int
        bottom-right x coordinate
    y2 : int
        bottom-right y coordinate
    index : list
        list containg the indexes of visited contours
    contours: list
        list containg the coordinates of the detected contours

    Returns
    -------
    out : tuple
        tuple of the updated coordinates, i.e. (x1, y1, x2, y2)
    """

    i = index[-1]
    len1 = len(index)
    area1 = (x2-x1)*(y2-y1)
    logger.debug("area : %s", area1)
    for idx, c in enumerate(contours):
        #Checking the index, area and also the position of the bounding rectangle
        if idx not in index and cv.contourArea(c) > area1 and not (y1 < 250 < y2 or y1 < 400 < y2):
            area1 = cv.contourArea(c)
            i = idx
            logger.debug("new_index : %s", i)

    if i not in index:
        index.append(i)
    len2 = len(index)

    #finding out the smallest x and y coordinates for x1 and y1 and largest x and y coordinates for x2 and y2 for next bounding rectangle
    if len2 > len1:
        x1, y1, x2, y2 = (1000, 1000, 0, 0)
        logger.debug(str(("index : ", index)))
        contour = contours[index[-1]]
        for a in contour:
            for b in a:
                if b[0] > x2:
                    x2 = b[0]
                elif b[0] < x1:
                    x1 = b[0]
                if b[1] > y2:
                    y2 = b[1]
                elif b[1] < y1:
                    y1 = b[1]

        logger.info("x1, y1 : %s, %s", x1, y1)
        logger.info("x2, y2 : %s, %s", x2, y2)
    return (x1, y1, x2, y2)


def compute_coordinates(input_file) -> tuple:
    """
    Returns the top-left and the bottom-right coordinates of the largest table in the image
    
    Parameters
    ----------
    input_file : Image object
        image file to be processed

    Returns
    -------
    out : tuple
        top-left and the bottom-right coordinates of the largest table in the image, i.e. (x1, y1, x2, y2)
    """

    x1, y1, x2, y2 = (1000, 1000, 0, 0)
    i = 0
    index = []
    contour = 0
    img = input_file
    image = img.copy()
    logger.info(str(("shape : ", img.shape)))

    resized_x = 1000
    resized_y = 700
    xscale = img.shape[1]/resized_x
    yscale = img.shape[0]/resized_y
    logger.info(str(("xscale, yscale :", xscale, yscale)))
    img = cv.resize(img, (resized_x, resized_y))

    logger.debug("OpenCV transformations")
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    ret, thresh = cv.threshold(gray, 245, 255, cv.THRESH_BINARY_INV)

    struct = cv.getStructuringElement(cv.MORPH_RECT, (8, 8))
    dilated = cv.dilate(thresh, struct, anchor=(-1, -1), iterations=1)

    contours, hierarchy = cv.findContours(dilated, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    logger.debug("Contours found")

    area = 0
    
    #finding out the index of the contour with the largest area
    for idx, c in enumerate(contours):
        p = cv.contourArea(c)
        logger.info("idx, area : %s, %s", idx, p)
        if p > area:
            area = p
            i = idx

    if i not in index:
        index.append(i)
    logger.debug("index : %s", index)

    contour = contours[index[-1]]
    logger.info(str(("contour", contour)))

    #finding out the top-right and the bottom-left co-ordinates of the largest contour
    for a in contour:
        for b in a:
            if b[0] <= x1:
                x1 = b[0]
                if b[1] > y2:
                    y2 = b[1]

            if b[0] >= x2:
                x2 = b[0]
                if b[1] < y1:
                    y1 = b[1]

    logger.info("x1, y1 : %s, %s", x1, y1)
    logger.info("x2, y2 : %s, %s", x2, y2)

    logger.debug("starting a while loop")
    while(True):
        x1_old, y1_old, x2_old, y2_old = (x1, y1, x2, y2) 
        x1, y1, x2, y2 = area_check(x1, y1, x2, y2, index, contours)
        if (x1_old, y1_old, x2_old, y2_old) == (x1, y1, x2, y2):
            break
    logger.debug("while loop completed")

    x1 = int(x1 * xscale)    
    y1 = int(y1 * yscale)
    x2 = int(x2 * xscale)
    y2 = int(y2 * yscale)

    logger.info("x1, y1, x2, y2 : %s, %s, %s, %s", x1, y1, x2, y2)

    # cv.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
    # image = cv.resize(image, (int(image.shape[1]/image.shape[0]*800), 800))
    # cv.imshow("Bounded", image)

    cv.waitKey(0)
    cv.destroyAllWindows()

    return (x1, y1, x2, y2)