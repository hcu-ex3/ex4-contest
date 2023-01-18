# 開始時に実行
# 緑を検知し、距離センサも反応したら回転しスタートする

from rotation import rotation

import cv2
import r3pi
import time
import yaml
import numpy as np
import pass_baton as pb

# config.yamlの読み込み
with open('config.yml', 'r') as yml:
  config = yaml.load(yml)


def get_distance(criterion):
  distance = r3pi.pot_voltage()
  if distance < criterion:
    return True
  else:
    return False

def rotation(wait_time):
  r3pi.stop
  r3pi.left_motor(0.25)
  r3pi.right_motor(-0.25)
  time.sleep(wait_time)
  r3pi.stop
        
def check_start(cap):
  _, frame0 = cap.read()
  while not get_distance(550) or not pb.isPassBaton(frame0):
    _, frame0 = cap.read()
    time.sleep(0.1)
  rotation(config['baton']['rotation'])

