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

arduino = Arduino(ARDUINO_PORT, baudrate=115200, timeout=10)
time.sleep(1)

cap = cv2.VideoCapture(CAMERA_ID, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

arduino.set_speed(CAR_SPEED)

last_err = 0

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('./output20.avi', fourcc, 60, (1280, 720))

def go_forward_per():
    global ret, frame
    print("PEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEER")
    print(np.sum(bottom))
    arduino.stop()
    old = time.time()
    while time.time() - old < 0.1:
        ret, frame = cap.read()
        out.write(frame)
    arduino.set_angle(79)
    arduino.set_speed(CAR_SPEED - 10)
    old = time.time()
    while time.time() - old < 2:
        ret, frame = cap.read()
        out.write(frame)
    arduino.stop()
    old = time.time()
    while time.time() - old < 0.01:
        ret, frame = cap.read()
        out.write(frame)
    arduino.set_angle(90)
    while time.time() - old < 1:
        ret, frame = cap.read()
        out.write(frame)
    old = time.time()
    while time.time() - old < 0.01:
        ret, frame = cap.read()
        out.write(frame)

def turn():
    global ret, frame
    arduino.set_angle(90)
    old = time.time()
    while time.time() - old < 0.1:
        ret, frame = cap.read()
        out.write(frame)
    arduino.set_angle(65)
    old = time.time()
    while time.time() - old < 3.4:
        ret, frame = cap.read()
        out.write(frame)
    arduino.set_angle(60)
    old = time.time()
    while time.time() - old < 1:
        ret, frame = cap.read()
        out.write(frame)


try:
    point_start = 0
    per = 0
    old1 = time.time()
    while True:
        ret, frame = cap.read()

        if not ret:
            break

        out.write(frame)
        img = cv2.resize(frame, SIZE)
        binary = binarize(img, THRESHOLD)
        perspective = trans_perspective(binary, TRAP, RECT, SIZE)
        mask_tower = binary[:, 350:]
        summ_pic = np.sum(mask_tower)
        if per < 1:
            if summ_pic > 2000000:
                point_start = 2
                print(2)
        #else:
            #print(1, 3)
        #perspective = perspective[:, :]
        left, right = centre_mass(perspective)
        bottom = perspective[150:250, :]
        #cv2.imshow('bot', bottom)
        if np.sum(bottom) > 1500000:
            per += 1
            print("PEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEeeeeeeeeeeeR")
            ret, frame = cap.read()
            if not ret:
                break
            if per == 1:
                print(time.time() - old1)
                if time.time() - old1 > 15 and point_start == 0:
                    point_start = 1
                    turn()
                    print(1)
                elif point_start == 0:
                    point_start = 3
                    print(np.sum(bottom))
                    go_forward_per()
            elif per == 2:
                if point_start == 1:
                    go_forward_per()
                else:
                    turn()
            else:
                turn()
             # if time.time()- old1
            print("PEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEER")
            # print(np.sum(bottom))
        #     # print(np.sum(bottom))
        print(point_start)
        err = 0 - ((left + right) // 2 - SIZE[0] // 2)
        if abs(right - left) < 100:
            err = last_err

        angle = int(90 + KP * err + KD * (err - last_err))

        if angle < 60:
            angle = 60
        elif angle > 120:
            angle = 120

        last_err = err
        print(f'angle={angle}')
        arduino.set_speed(CAR_SPEED)
        arduino.set_angle(angle)
except KeyboardInterrupt as e:
    print('Program stopped!', e)


arduino.stop()
arduino.set_angle(90)
cap.release()
out.release()
