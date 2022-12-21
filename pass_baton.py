import cv2
import numpy as np

RED = (255, 0, 0)

WIDTH = 320
HEIGHT = 240
WX = int(WIDTH / 3)
WY = int(HEIGHT / 5)
WW = int(WIDTH / 3)
WH = int(HEIGHT / 4)

KSIZE=int(WIDTH/53) # WIDTH=320->KSIZE=6,WIDTH=160->KSIZE=3
KERNEL = np.ones((KSIZE, KSIZE), np.uint8)

LOWER_GREEN = np.array([40, 64, 64])
UPPER_GREEN = np.array([70, 255, 255])

def isPassBaton(image):
    #切り抜き
    frame = image[WY : WY + WH, WX : WX + WW]
    

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image to only detect black colors
    mask = cv2.inRange(hsv, LOWER_GREEN, UPPER_GREEN)

    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame, frame, mask = mask)

    # Eliminate holes and dots 
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, KERNEL)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, KERNEL)

    cv2.rectangle(frame,(0,0),(WW-1,WH-1),(0,255,0),1)
    
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(frame, contours, -1, RED, 3)
    if len(contours) >= 1:
        #if any contours

        #get area of biggest contours
        area = cv2.moments(contours[-1])["m00"]

        if area > 200:
            return True
    

    return False