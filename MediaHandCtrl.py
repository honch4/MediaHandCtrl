from sre_constants import SUCCESS
import cv2
import socket
import time
from cv2 import COLOR_BAYER_BG2RGB
from matplotlib import Color
import mediapipe as mediapp
from numpy import true_divide



class HandDetect():
    def __init__(self):
        self.hand_detect = mediapp.solutions.hands.Hands()
        self.draw = mediapp.solutions.drawing_utils

    def process(self, ipc, draw = True):
        ipc_rgb = cv2.cvtColor(ipc, cv2,COLOR_BAYER_BG2RGB)
        if draw:
            if self.hands_data.multi_hand_landmarks:
                for handlms in self.hands_data.multi_hand_landmarks:
                    self.draw.draw_landmarks(ipc, handlms, mediapp.solutions.hands.HAND_CONNECTIONS)
    
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

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
camera = cv2.VideoCapture(0)
hand_detect = HandDetect()

while True:
    SUCCESS, ipc = camera.read()
    ipc = cv2.flip(ipc, 1)
        h, w, c = ipc.shape
        hand_detector.process(ipc, draw=False)
        position = hand_detector.find_position(ipc)
        left_fingers = hand_detector.fingers_count('Left')
        cv2.putText(ipc, str(left_fingers), (100, 75), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 3, (255, 0, 0))
        right_fingers = hand_detector.fingers_count('Right')
        cv2.putText(ipc, str(right_fingers), (w-200, 75), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 3, (0, 0, 255))
        cv2.imshow('ViewHandCtrl', ipc)
        if right_fingers == 5:
            socket.sendto('PAGEDOWN'.encode(),(str('192.168.1.18',int(5501))))
        if left_fingers == 5:
            socket.sendto('PAGEUP'.encode(),(str('192.16.1.18'),int(5501)))

    key = cv2.waitKey(1) 
    if key == 27:
        break

camera.release()

cv2.destroyAllWindows