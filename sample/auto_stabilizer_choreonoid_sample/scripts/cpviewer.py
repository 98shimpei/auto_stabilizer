#!/usr/bin/env python3

import cv2
import numpy as np
import math
import time
import sys

scale = 500
mode = "play"

center_x = 0
center_y = 0

mouse_start_x = 0
mouse_start_y = 0
center_start_x = 0
center_start_y = 0

drag = False

def mousePoints(event, x, y, flag, params):
    global center_x, center_y, mouse_start_x, mouse_start_y, center_start_x, center_start_y, drag
    if event == cv2.EVENT_LBUTTONDOWN:
        drag = True
        mouse_start_x = x
        mouse_start_y = y
        center_start_x = center_x
        center_start_y = center_y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drag:
            center_x = center_start_x + (x - mouse_start_x) * 1
            center_y = center_start_y + (y - mouse_start_y) * 1
    elif event == cv2.EVENT_LBUTTONUP:
        drag = False


def reshape_list(lst):
    global center_x, center_y
    lst = lst*scale+750
    lst = lst.astype(np.int64)
    lst = lst.reshape(int(lst.shape[0]/2), 2)
    lst += np.array([center_x, center_y])
    return lst

def reshape_pos(pos):
    global center_x, center_y
    return (int(pos[0]*scale+750+center_x), int(pos[1]*scale+750+center_y))

args = sys.argv

tmpdata = np.loadtxt(args[1]+"ast_tmpOut")
cpdata = np.loadtxt(args[1]+"ast_actDcmOut")
landingdata = np.loadtxt(args[1]+"ast_dstLandingPosOut")
cr_data = []
with open(args[1]+"ast_captureRegionOut") as f:
    for line in f:
        cr_data.append(np.array(line.split()).astype(np.float32))
sr_data = []
sr_num_data = []
with open(args[1]+"ast_steppableRegionLogOut") as f:
    for line in f:
        sr_data.append(np.array(line.split()).astype(np.float32))
with open(args[1]+"ast_steppableRegionNumLogOut") as f:
    for line in f:
        sr_num_data.append(np.array(line.split()).astype(np.float32))
stride_data = []
with open(args[1]+"ast_strideLimitationHullOut") as f:
    for line in f:
        stride_data.append(np.array(line.split()).astype(np.float32))

print(tmpdata.shape[0])
if len(args) >= 3:
    start = int(args[2])
else:
    start = 0

i = start
while True:
    img = np.zeros((1500, 1500, 3))

    capture_region = reshape_list(cr_data[i][1:])

    steppable_region = []
    index = 1
    for j in sr_num_data[i][1:]:
        steppable_region.append(reshape_list(sr_data[i][index:index+int(j)*2]))
        index+=int(j)*2

    supportleg = reshape_list(tmpdata[i][1:9])

    stridelimit = reshape_list(stride_data[i][1:])

    zmplimit = reshape_list(tmpdata[i][9:17])

    cv2.polylines(img, [capture_region], True, (255, 255, 0))
    cv2.polylines(img, steppable_region, True, (255, 255, 0))
    cv2.polylines(img, [supportleg], True, (0, 255, 0))
    cv2.polylines(img, [stridelimit], True, (0, 255, 255))
    cv2.circle(img, reshape_pos(cpdata[i][1:3]), 10, (0, 0, 255), -1)
    cv2.circle(img, reshape_pos(landingdata[i][1:3]), 10, (255, 0, 0), -1)
    cv2.circle(img, reshape_pos(landingdata[i][4:6]), 10, (255, 0, 0), -1)
    cv2.circle(img, reshape_pos(tmpdata[i][17:19]), 5, (255, 0, 255), -1)
    cv2.line(img, reshape_pos(tmpdata[i][19:21]), reshape_pos(tmpdata[i][21:23]), (255, 100, 100), 3)
    for j in range(zmplimit.shape[0]):
        cv2.circle(img, (zmplimit[j][0], zmplimit[j][1]), 5, (255, 0, 255), -1)

    if mode == "play":
        cv2.circle(img, (10, 10), 5, (0, 255, 0), -1)
    elif mode == "stop":
        cv2.circle(img, (10, 10), 5, (0, 0, 255), -1)
    cv2.imshow('img', img)
    cv2.setMouseCallback("img", mousePoints)
    key = cv2.waitKey(1)
    if key == -1:
        if mode == "play":
            i += 1
            i = max(0, min(tmpdata.shape[0]-1, i))
    elif key == 103:
        mode = "stop"
        i -= 100
        i = max(0, min(tmpdata.shape[0]-1, i))
    elif key == 104:
        mode = "stop"
        i -= 10
        i = max(0, min(tmpdata.shape[0]-1, i))
    elif key == 106:
        mode = "stop"
        i -= 1
        i = max(0, min(tmpdata.shape[0]-1, i))
    elif key == 59:
        mode = "stop"
        i += 100
        i = max(0, min(tmpdata.shape[0]-1, i))
    elif key == 107:
        mode = "stop"
        i += 1
        i = max(0, min(tmpdata.shape[0]-1, i))
    elif key == 108:
        mode = "stop"
        i += 10
        i = max(0, min(tmpdata.shape[0]-1, i))
    elif key == 32:
        mode = "play"
    elif key == 13:
        print(tmpdata[i][0])
    elif key == 27:
        break
    #if key != -1:
    #    print(key)
    #    #print(tmpdata[i][0])

