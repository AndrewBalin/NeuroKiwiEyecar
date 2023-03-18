import argparse
import time
from pathlib import Path

import cv2
import numpy as np
import serial

from arduino import Arduino
from utils import *


CAR_SPEED = 1440
SLOW = 1450
ARDUINO_PORT = '/dev/ttyUSB0'
CAMERA_ID = '/dev/video0'

KP = 0.63 #0.55  # 0.22 0.32 0.42 0.55
KD = 0.17  # 0.17
last = 0
METER = 545

SIZE = (533, 300)

RECT = np.float32([[0, SIZE[1]],
                   [SIZE[0], SIZE[1]],
                   [SIZE[0], 0],
                   [0, 0]])

TRAP = np.float32([[10, 299],
                   [523, 299],
                   [440, 200],
                   [93, 200]])

src_draw = np.array(TRAP, dtype=np.int32)

# OPENCV PARAMS
THRESHOLD = 228
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

model_file = 'yolov4-tiny_uint8.tmfile'
model = yolopy.Model(model_file, use_uint8=True, use_timvx=True, cls_num=12)

arduino = Arduino(ARDUINO_PORT, baudrate=115200, timeout=10)
time.sleep(1)

cap = cv2.VideoCapture(CAMERA_ID, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

arduino.set_speed(CAR_SPEED)

last_err = 0

try:

    while True:
        ret, frame = cap.read()
        classes, scores, boxes = model.detect(frame)

        data = zip(classes, boxes)
        parks = list(filter(lambda e: e[0] == 4, data))
        park_info = {
            'xmin': parks[0][1][0],
            'ymin': parks[0][1][1],
            'xmax': parks[0][1][0] + parks[0][1][2],
            'ymax': parks[0][1][1] - parks[0][1][3],
            'width': parks[0][1][2],
            'height': parks[0][1][3]
        }
        if park_info['xmin'] > 750 and park_info['ymin'] < 400 and park_info['xmax'] < 1150 and park_info['ymax'] > 10:
            print('Знак найден')
            if park_info['height'] * park_info['width'] > 10000:
                print('Парковка')

except KeyboardInterrupt as e:
    print('Program stopped!', e)

arduino.stop()
arduino.set_angle(90)
cap.release()

