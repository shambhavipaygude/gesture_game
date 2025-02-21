import cv2
import mediapipe as mp
from math import hypot
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np


cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands 
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils 


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()
min,max = volRange[0],volRange[1]; 

vol = 0
while cap.isOpened():
    res, frame = cap.read() 
    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 

    results = hands.process(imgRGB) 
 
    lmlist = []

    if results.multi_hand_landmarks:
        for hand_landmark in results.multi_hand_landmarks:
            for id, lm in enumerate(hand_landmark.landmark):
                h, w, _ = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmlist.append([id, cx, cy])
            mpDraw.draw_landmarks(frame, hand_landmark, mpHands.HAND_CONNECTIONS)
    
    if lmlist != []:
        x1, y1 = lmlist[4][1], lmlist[4][2] 
        x2, y2 = lmlist[8][1], lmlist[8][2]  

        cv2.circle(frame, (x1, y1), 15, (255, 0, 255), cv2.FILLED) 
        cv2.circle(frame, (x2, y2), 15, (255, 0, 255), cv2.FILLED) 
        cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 3) 

        length = hypot(x2 - x1, y2 - y1)
   
        vol = np.interp(length, [20,190], [min,max])
    
        volume.SetMasterVolumeLevel(vol, None)
    cv2.imshow('Image', frame)
    if cv2.waitKey(1) == ord('x'): 
        break
        
cap.release()     
cv2.destroyAllWindows()