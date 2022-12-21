# 開始時に実行し、180度回転する
# 引数は回転する時間

import r3pi
import time

def rotation(wait_time):
  r3pi.stop
  r3pi.left_motor(0.2)
  r3pi.right_motor(-0.2)
  time.sleep(wait_time)
  r3pi.stop
  r3pi.forward(0.1)