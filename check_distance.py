# 距離センサを用いて、前方のロボットカーとの距離を取得
# 一定以上になったら帰値を1に変更
# 
# 距離は230以上で停止

import r3pi

def check_distance(distance):
  sensor = r3pi.pot_voltage()
  #print("dis:%d" , sensor)
  if distance < sensor:
    return 1
  else:
    return 0