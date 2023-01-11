import time
import math
import r3pi
import cv2
import numpy as np

# 320x240
WIDTH = 320
HEIGHT = 240

LOWER_RED= np.array([150,64,0]) # in HSV
UPPER_RED= np.array([179,255,255])

#障害物検知用窓のサイズ，位置
WH=int(HEIGHT/6)
WW=int(WIDTH/6)
WY=int(HEIGHT*5/9)
WX=int(WIDTH*2/5)

KSIZE=int(WIDTH/53)
KERNEL = np.ones((KSIZE, KSIZE), np.uint8)

RED   = (0,0,255) # in BGR, rather than RGB

def colorcone(image):

    #検出窓
    frame = image[WY:WY+WH, WX:WX+WW]

    #BGR 空間から HSV 空間に変換
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    #赤色のみを検出するように HSV 画像をしきい値化
    mask = cv2.inRange(hsv, LOWER_RED, UPPER_RED)
    
    # ビットごとの AND 演算で元画像をマスク
    res = cv2.bitwise_and(frame, frame, mask = mask)

    #モルフォロジー演算で 穴や点をなくす
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, KERNEL)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, KERNEL)


    # マスクされた領域を見つける
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(frame, contours, -1, RED, 3)
    
    cv2.rectangle(frame,(0,0),(WW-1,WH-1),(0,255,0),1)


    if len(contours) >= 1:
        find_red = True
        
        """for cnt in contours:
            x,y,w,h, = cv2.boundingRect(cnt)
            print("x={0}, y={1}, w={2}, h={3}, WW={4}, WH={5}".format(x,y,w,h,WW,WH))
            if w > int(WW*0.5):
                print('found red.')
                find_red = True"""
        
        
        if find_red:
            r3pi.left_motor(0.2)
            r3pi.right_motor(0.1)
            time.sleep(1.5)
            r3pi.left_motor(0.1)
            r3pi.right_motor(0.22)
            time.sleep(1.5)
            r3pi.left_motor(0.12)
            r3pi.right_motor(0.2)
            time.sleep(1.5)
            find_red = False
