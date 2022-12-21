# 開始時に実行し、180度回転する
# 引数は回転する時間
# 推奨回転時間 0.7

import r3pi
import time

def rotation(wait_time):
  r3pi.stop
  r3pi.left_motor(0.25)
  r3pi.right_motor(-0.25)
  time.sleep(wait_time)
  r3pi.stop