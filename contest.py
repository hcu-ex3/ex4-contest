#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# line_follower.py -- PID line follower
# carp-lover.py -- search and chase a red object
# Released under the MIT License
# Copyright (c) 2017 Hiroshima City University
#
import time
import math
import r3pi
import cv2
import numpy as np
import sys
import RPi.GPIO as GPIO

import baton_stopper as bs

################################

print('Python {0}.{1}.{2}'.format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro))
print('OpenCV {0}'.format(cv2.__version__))

################################

# Global parameters
MJPGSTREAMER = False # True # False if you use webcam
GUI = True # False if you use CUI
MJPGURI = "http://localhost:8081/?action=stream"
# Image Size
# 160x120
#WIDTH = 160
#HEIGHT = 120
# 320x240
WIDTH = 320
HEIGHT = 240
# 640x480
#WIDTH = 640
#HEIGHT = 480
BARSIZE = 60
RED   = (0,0,255) # in BGR, rather than RGB
GREEN = (0,255,0) # in BGR, rather than RGB
BLUE  = (255,0,0) # in BGR, rather than RGB
LOWER_BLACK= np.array([0,0,0]) # in HSV
UPPER_BLACK= np.array([180,255,50])
LOWER_WHITE= np.array([0,0,180]) # in HSV
UPPER_WHITE= np.array([180,255,255])
# black line detection window
LY = HEIGHT-int(HEIGHT/10)
LX = int(WIDTH / 8)
LH = int(HEIGHT/10)
LW = int(WIDTH / 4)
# left white line detection window
#LH=int(HEIGHT*0.?)
#LW=int(WIDTH*0.?)        
#LX=int(WIDTH*0.?)
#LY=int(HEIGHT-LH)

#KERNEL = np.ones((5, 5), np.uint8) # 320x240,640x480
#KERNEL = np.ones((3, 3), np.uint8) # 160x120
KSIZE=int(WIDTH/53) # WIDTH=320->KSIZE=6,WIDTH=160->KSIZE=3
KERNEL = np.ones((KSIZE, KSIZE), np.uint8)

# not use
FF = 0.0 # Forgetting factor

#MAX = 0.3
#MAX = 0.4
MAX = 0.5
MIN = 0.0
#P_TERM = 0.2
#I_TERM = 0.0
#D_TERM = 1.0
P_TERM = 0.1
I_TERM = 0.0
D_TERM = 0.5
right = 0.0
left = 0.0
cur_pos = 0.0
prev_pos = 0.0
deriv = 0.0
prop = 0.0
intg = 0.0
power = 0.0
speed = 0.2
#speed = 0.3
#speed = 0.35
#speed = 0.4 # OK

#固体差で車体ごとに、多少はカメラの中心が違うので、調整する
CENTER=0.5

# Relative target direction, which ranges in [0,1]
gcx = CENTER

cap = None
frame = None
frame0 = None

# Utility functions
def getMomentX(c):
    m = cv2.moments(c)
    x = float(m['m10'] / m['m00'])
    return x

def printBar(value):
    i = int(value * BARSIZE + 0.5)
    bar = "|" + "-" * i + "*" + "-" * (BARSIZE-i) + "|"
    print(bar)

#フレーム数を指定し、カメラの読み出し＆表示をしながら待つ 30frame=1sec.
def cap_sleep(n):
    for i in range(n):
        _, frame0 = cap.read()
        cv2.imshow('frame0', frame0)
        k = cv2.waitKey(1) & 0xFF

# Setup r3pi
r3pi.init()
r3pi.cls()
r3pi.play("O5 T120 L16 ceg>crg>c8")
################

GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("白いボタンを押すとスタートします\n（オレンジ色のシャットダウンボタンの右にあります）")
while (GPIO.input(12) == 1): # 押されるまで待機
    time.sleep(0.1)
r3pi.play("c")
while (GPIO.input(12) == 0): # 離されるまで待機（チャタリング対策） 
    time.sleep(0.1)
r3pi.play("g")
print("白いボタンが押されました")

time.sleep(1.0)

################

#オブジェクトの宣言
green_stopper = bs.BatonStopper()

if MJPGSTREAMER == False:
    # Use webcam
    cap = cv2.VideoCapture(0)
    cap.set(3, WIDTH)
    cap.set(4, HEIGHT)
else:
    cap = cv2.VideoCapture(MJPGURI)

# dummy read 30frames=1sec. for OpenCV3
cap_sleep(30)

f = 0
start = time1 = time.time()

while(1):
    # Take a frame
    _, frame0 = cap.read()
    
    # trim low part only
    frame = frame0[LY:LY+LH, LX:LX+LW]

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image to only detect black colors
    mask = cv2.inRange(hsv, LOWER_WHITE, UPPER_WHITE)

    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame, frame, mask = mask)

    # Eliminate holes and dots 
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, KERNEL)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, KERNEL)

    # Find the masked area
    # opencv3
    #image, contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # opencv4
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(frame, contours, -1, RED, 3)
    
    if len(contours) >= 1:
        # Black object(s) detected
        # focus on the first one
        cx = getMomentX(contours[0]) / LW # normalization

        clen = len(contours)
        while clen > 1:
            # find most center cx
            clen -= 1
            ccx = getMomentX(contours[clen]) / LW # normalization
            if abs(cx - CENTER) > abs(ccx - CENTER):
                cx = ccx
        
        # Forgetting-factor-based smoothing
        gcx = (1.0 - FF) * cx + FF * gcx
        printBar(gcx)

        # gcx -> line position [-1.0,1.0]
        cur_pos = (gcx - CENTER) * 2.0

        prop = cur_pos
        deriv = cur_pos - prev_pos
        intg += prop
        prev_pos = cur_pos

        power = P_TERM * prop + I_TERM * intg + D_TERM * deriv

        left = speed + power
        right = speed - power

        if left < MIN :
            left = MIN
        elif left > MAX:
            left = MAX

        if right < MIN :
            right = MIN
        elif right > MAX:
            right = MAX

        r3pi.left_motor(left)
        r3pi.right_motor(right)

        #print(cur_pos, power, speed, intg, deriv, left, right)

    else:
        print('len(contours) < 1')
        
    green_stopper.checkGreenStop(frame0)
    run_end = green_stopper.LineStop(frame0)
    if run_end:
        break

    if GUI:
        cv2.rectangle(frame,(0,0),(LW-1,LH-1),(0,255,0),1)
        cv2.imshow('frame0', frame0)

    # Press ESC key to exit
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break

    f += 1
    time2 = time.time()
    av_fps = f / (time2 - start)
    fps = 1 / (time2 - time1)
    time1 = time2
    print ("{0} : fps={1:.4}, av_fps={2:.4}".format(f, fps, av_fps))

cv2.destroyAllWindows()
r3pi.stop()