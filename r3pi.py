#! /usr/bin/python3
# -*- coding: utf-8 -*-

# r3pi (python ライブラリ)モジュール A.Kojima 2022/8/2
# 広島市立大学　情報工学実験 Raspberry Pi + Pololu 3pi ロボットカー用

# m3pi(c++ライブラリ)の仕様を参考に作成してある
# https://os.mbed.com/users/chris/code/m3pi/

# タイプアノテーションを書いてあるが，Python3.9では実行への影響はない．
# Cython0.27以降では，タイプアノテーションが(多少)効果のあるコンパイルができる

import serial
import traceback
import time

# 3pi slave serial command
# https://www.pololu.com/docs/0J21/10.a

SEND_SIGNATURE=b'\x81'
SEND_RAW_SENSOR_VALUES=b'\x86'
SEND_TRIMPOT=b'\xB0'
SEND_BATTERY_MILLIVOLTS=b'\xB1'
DO_PLAY=b'\xB3'
PI_CALIBRATE=b'\xB4'
DO_CLEAR=b'\xB7'
DO_PRINT=b'\xB8'
DO_LCD_GOTO_XY=b'\xB9'
LINE_SENSORS_RESET_CALIBRATION=b'\xB5'
SEND_LINE_POSITION=b'\xB6'
AUTO_CALIBRATE=b'\xBA'
START_PID=b'\xBB'
STOP_PID=b'\xBC'
M1_FORWARD=b'\xC1'
M1_BACKWARD=b'\xC2'
M2_FORWARD=b'\xC5'
M2_BACKWARD=b'\xC6'

#uart = serial.Serial('/dev/serial0', 115200)

try:
    uart = serial.Serial(
        port="/dev/serial0",
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=None,
    )
except serial.SerialException:
    print(traceback.format_exc())
uart.reset_input_buffer()
uart.reset_output_buffer()

# 再初期化
def init()->None:
    uart.reset_input_buffer()
    uart.reset_output_buffer()
    stop()

def reset()->None:
    uart.reset_input_buffer()
    uart.reset_output_buffer()
    stop()
        
# m3piと左右が逆(e3pi 2022年度と同じ)
def left_motor(speed: float)->None:
    motor(1, speed)

# m3piと左右が逆(e3pi 2022年度と同じ)
def right_motor(speed: float)->None:
    motor(0, speed)

def forward(speed: float)->None:
    motor(0, speed)
    motor(1, speed)

def backward(speed: float)->None:
    motor(0, -speed)
    motor(1, -speed)

def left(speed: float)->None:
    motor(0, speed)
    motor(1, -speed)

def right(speed: float)->None:
    motor(0, -speed)
    motor(1, speed)

def stop()->None:
    motor(0, 0.0)
    motor(1, 0.0)

def motor(motor: int, speed: float)->None:
    if speed > 0.0:
        if motor==1:
            opcode = M1_FORWARD
        else:
            opcode = M2_FORWARD
    else:
        if motor==1:
            opcode = M1_BACKWARD
        else:
            opcode = M2_BACKWARD
            
    arg = int(0x7f * abs(speed))
    uart.write(opcode)
    uart.write(bytes([arg]))

def pot_voltage()->int:
    uart.write(SEND_TRIMPOT)
    return int.from_bytes(uart.read(2), 'little')

def battery()->float:
    uart.write(SEND_BATTERY_MILLIVOLTS)
    return int.from_bytes(uart.read(2), 'little')/1000.0

def line_position()->float:
    uart.write(SEND_LINE_POSITION)
    return (int.from_bytes(uart.read(2), 'little')-2048.0)/2048.0

def sensor_auto_calibrate()->int:
    uart.write(AUTO_CALIBRATE)
    return int.from_bytes(uart.read(1), 'little')

def calibrate()->None:
    uart.write(PI_CALIBRATE)

def reset_calibration()->None:
    uart.write(LINE_SENSORS_RESET_CALIBRATION)

def PID_start(max_speed: int, a: int, b: int, c: int, d: int)->None:
    uart.write(START_PID)
    uart.write(bytes([max_speed, a, b, c, d]))
    
def PID_stop()->None:
    uart.write(STOP_PID)

def locate(x: int, y: int)->None:
    uart.write(DO_LCD_GOTO_XY)
    uart.write(bytes([x, y]))

def cls()->None:
    uart.write(DO_CLEAR)

#def lcd_print(str_text: str, length: int)->None: # 元の仕様
def lcd_print(str_text: str, length : int = 8)->None: # 長さ指定はデフォルト引数(省略可能)
    text = str_text.encode() # bytesへ変換
    len_text = len(text)
    if len_text < length: # 実際の文字列長が、引数の長さ指定より短いとき->実際の文字列長に修正
        length = len_text
    if length > 8:
        length = 8 # LCD表示は1行が最大8文字
    uart.write(DO_PRINT)
    uart.write(bytes([length]))
    uart.write(text[:length])

def putc(c: int)->int:
    return uart.write(bytes([c]))

def getc() ->int:
    return int.from_bytes(uart.read())

def play(str_text: str)->None:
    text = str_text.encode() # bytesへ変換
    uart.write(DO_PLAY)
    length = len(text)
    if length >= 100:
        length = 99 #  3pi slave serial play max 
    uart.write(bytes([length]))
    uart.write(text[:length])
    
# テストコード：モジュールとしてインポート(import r3pi)した場合は実行されない
if __name__ == '__main__':
    init()
    play('O5 T120 L16 ceg>crg>c8')
    print('Success!')

    pot = pot_voltage()
    print(f'distance={pot}')
    bat = battery()
    print(f'battery={bat}V')
