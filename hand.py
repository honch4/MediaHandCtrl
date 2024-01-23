import cv2  # opencv的库
import socket  # UDP通讯必要的库
import time  # 做延时使用的
# import os
# import sys
# from cv2 import VideoCapture
import mediapipe as mpp


class HandDetector():
    # 定义类的初始化方法
    def __init__(self):
        # 创建mediapipe的手部识别对象
        self.hand_detector = mpp.solutions.hands.Hands()
        # 
        self.drawer = mpp.solutions.drawing_utils

    # 手部20个关节数据
    def process(self, ipc, draw=True):
        # 将画面转换成RGB格式后进行处理
        ipc_rgb = cv2.cvtColor(ipc, cv2.COLOR_BGR2RGB)
        # 处理采集到的视频画面
        self.hands_data = self.hand_detector.process(ipc_rgb)
        if draw:
            # 判断有没有获取到关节数据
            if self.hands_data.multi_hand_landmarks:
                # 取出关节数据
                for handlms in self.hands_data.multi_hand_landmarks:
                    # 画出捕捉到的数据，将进行连线
                    self.drawer.draw_landmarks(ipc, handlms, mpp.solutions.hands.HAND_CONNECTIONS)

    def find_position(self, ipc):
        h, w, c = ipc.shape
        self.position = {'Left': {}, 'Right': {}}
        if self.hands_data.multi_hand_landmarks:
            i = 0
            for point in self.hands_data.multi_handedness:
                score = point.classification[0].score
                if score >= 0.8:
                    label = point.classification[0].label
                    hand_lms = self.hands_data.multi_hand_landmarks[i].landmark
                    for id, lm in enumerate(hand_lms):
                        x, y = int(lm.x * w), int(lm.y * h)
                        self.position[label][id] = (x, y)
                i = i + 1
        return self.position

    # 定义计算手指数量的方法
    def fingers_count(self, hand='Left'):
        tips = [4, 8, 12, 16, 20]
        tip_data = {4:0, 8:0, 12:0, 16:0, 20:0}
        for tip in tips:
            ltp1 = self.position[hand].get(tip, None)
            ltp2 = self.position[hand].get(tip-2, None)
            if ltp1 and ltp2:
                if tip == 4:
                    if ltp1[0] > ltp2[0]:
                        if hand == 'Left':
                            tip_data[tip] = 1
                        else:
                            tip_data[tip] = 0
                    else:
                        if hand == 'Left':
                            tip_data[tip] = 0
                        else:
                            tip_data[tip] = 1
                else:
                    if ltp1[1] > ltp2[1]:
                        tip_data[tip] = 0
                    else:
                        tip_data[tip] = 1
        return list(tip_data.values()).count(1)


# ipc_url = 'rtsp://admin:admin@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0'
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# 根据电脑摄像头选择，一般是1，如果有多个摄像头，要改变数值
camera = cv2.VideoCapture(1)
# camera = cv2.VideoCapture(ipc_url)
hand_detector = HandDetector()

while True:
    # 读取摄像头，判断有无成功
    success, ipc = camera.read()
    # 如果读取成功
    if success:
        ipc = cv2.flip(ipc, 1)
        h, w, c = ipc.shape
        hand_detector.process(ipc, draw=False)
        position = hand_detector.find_position(ipc)
        left_fingers = hand_detector.fingers_count('Left')
        # print('LeftHand: ', left_fingers)
        # note:颜色值为BGR模式
        cv2.putText(ipc, str(left_fingers), (100, 75), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 3, (255, 0, 0))
        right_fingers = hand_detector.fingers_count('Right')
        # print('RightHand：', right_fingers)
        cv2.putText(ipc, str(right_fingers), (w-200, 75), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 3, (0, 0, 255))
        # opencv创建一个名称为Video的窗口
        cv2.imshow('ViewHandCtrl', ipc)
        # 右手执行动作
        # if left_fingers == 1:
        #    sock.sendto('M1001M0001'.encode(), (str('192.168.1.18'), int(8666)))
        #    time.sleep(1)
        if left_fingers == 2:
            sock.sendto('mode01'.encode(), (str('192.168.1.72'), int(5501)))
        #    time.sleep(1)
        if left_fingers == 3:
            sock.sendto('mode02'.encode(), (str('192.168.1.72'), int(5501)))
        #    time.sleep(1)
        # if left_fingers == 4:
        #    sock.sendto('M1001M0004'.encode(), (str('192.168.1.72'), int(5501)))
        #    time.sleep(1)
        if left_fingers == 5:
            sock.sendto('mode03'.encode(), (str('192.168.1.72'), int(5501)))
        #    time.sleep(1)
        # 左手执行动作
        # if right_fingers == 1:
        #    sock.sendto('Lock'.encode(), (str('192.168.1.18'), int(10240)))
        #    time.sleep(1)
        # if right_fingers == 2:
        #    sock.sendto('601'.encode(), (str('192.168.1.72'), int(10240)))
        #    time.sleep(1)
        # if right_fingers == 3:
        #    sock.sendto('602'.encode(), (str('192.168.1.72'), int(10240)))
        #    time.sleep(1)
        # if right_fingers == 4:
        #    sock.sendto('CTRL,ALT,W'.encode(), (str('192.168.1.18'), int(10240)))
        #    time.sleep(1)
        # if right_fingers == 5:
            #sock.sendto('CTRL,WIN,LEFT'.encode(), (str('192.168.1.18'), int(10240)))
        #    sock.sendto('M3002M0001'.encode(), (str('192.168.1.18'), int(8666)))
        #    time.sleep(1)
    # 等待按待1ms时间
    key = cv2.waitKey(1)
    # 按下按键Esc时停止运行
    if key == 27:
        break
# 释放摄像头资源
camera.release()
# 释放所有窗口
cv2.destroyAllWindows()


