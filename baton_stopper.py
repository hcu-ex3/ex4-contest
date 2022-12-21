import check_distance as cd
import pass_baton as pb
import cv2
import numpy as np
import r3pi

WIDTH = 320
HEIGHT = 240

LY2 = int(HEIGHT * 2 / 3)
LW2 = int(WIDTH / 4)
LX2 = int(WIDTH / 2 - LW2 / 2)
LH2 = int(HEIGHT/4)

KSIZE=int(WIDTH/53) # WIDTH=320->KSIZE=6,WIDTH=160->KSIZE=3
KERNEL = np.ones((KSIZE, KSIZE), np.uint8)

RED = (0,0,255) # in BGR, rather than RGB


def getMask(frame):
    #hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #mask = cv2.inRange(hsv, LOWER_WHITE, UPPER_WHITE)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mask = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 41, -15)
    return mask

def stopLine(image):
    frame = image[LY2:LY2+LH2, LX2:LX2+LW2]
    mask = getMask(frame)
    res = cv2.bitwise_and(frame, frame, mask = mask)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, KERNEL)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, KERNEL)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(frame, contours, -1, RED, 3)
    
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        #print("x={0}, y={1}, w={2}, h={3}, WW={4}".format(x, y, w, h, LW2))
        if w > int(LW2 * 0.7):
            #print('found stop line')
            r3pi.stop()
            return True
    
    return False
        
    

class BatonStopper:
    def __init__(self) -> None:
        self.green_flag = False
    
    def checkGreenStop(self, image):
        if pb.isPassBaton(image):
            self.green_flag = True

    def LineStop(self, image):
        if self.green_flag:
            return stopLine(image)
        return False