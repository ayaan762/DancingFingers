import autopy
#make it smoother
#try fixing hand distance issue
#create a function to find distance between two finger for future
#volume incrementation in whole nos
#count the number of fingers up
#somehow set the volume to make sure it doesnt change when hand is removed
#install cv2
#install mediapipe
#install pywhatkit
#install numpy
#install pycaw
#install speech recognition
#install wheel
#install pipwin
#install pyaudio


import cv2
import pyautogui
import pywhatkit
import mediapipe
import webbrowser
import time
import numpy
import numpy as np
import HandTracker as ht
import os
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from subprocess import call

from pymata4 import pymata4



Wcam , Hcam = 640, 480

cap = cv2.VideoCapture(0)

cap.set(3,Wcam)

cap.set(4, Hcam)

pt=0


detector = ht.handDetector(detectionCon=0.85, maxHands=1)

board = pymata4.Pymata4()



devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
#volume.GetMute()
#print(volume.GetMasterVolumeLevel())


volumerange = volume.GetVolumeRange()
minvol = volumerange[0]
maxvol = volumerange[1]
vol =0
volbar = 400
volper = 0
area = 0
colorvol = (255,0,0)
check =0




while True:


    success, img = cap.read()

    img = cv2.flip(img, 1)

    img = detector.findHands(img)

    handside = detector.LoRside(img)

    lmlist, bbox = detector.findPosition(img, draw=True)

    fingers = detector.fingersUp(img)



    if len(lmlist) !=0:
     #print(lmlist[4], lmlist[8])

     area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100

     #print(area)

     if 250<area<1000  and handside ==1:

         #print("yes")

         length , img , info = detector.findDistance(4,8,img)

         vol = numpy.interp(length, [50,300] , [minvol , maxvol])
         volbar = numpy.interp(length, [50,200] , [400 , 150])
         volper = numpy.interp(length, [50,200] , [0 , 100])

         smoothness = 10

         volper = smoothness*round(volper/smoothness)

         #print(fingers[1])


         #print(fingers)

         if not fingers[4]:
            volume.SetMasterVolumeLevelScalar(volper/100, None)
            cv2.circle(img, (info[4], info[5]), 15, (0, 255, 0), cv2.FILLED)
            colorvol = (255, 255, 0)
         else:
             colorvol= (255,0,0)

     elif (handside == -1):
         if fingers[1] and fingers[2] and not fingers[0] and not fingers[3] and not fingers[4]:
             # then make a url variable
             url = "https://middlesexcollege.edu/"

             # getting path
             browser_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

             # First registers the new browser
             webbrowser.register('brave', None,
                                 webbrowser.BackgroundBrowser(browser_path))

             # after registering we can open it by getting its code.
             webbrowser.get('brave').open(url)

             time.sleep(2)

         elif fingers == [0,1,0,0,0]:

             search = detector.voice_recognition()
             if (search != None):
                 pywhatkit.search(search)
                 time.sleep(5)

         elif fingers[1] and fingers[2] and fingers[3] and fingers[4] and not fingers[0]:

             search = detector.voice_recognition()
             if search != None:
                 pywhatkit.playonyt(search)
                 time.sleep(5)



         elif fingers[1] and fingers[2] and fingers[3] and not fingers[0] and not fingers[4]:

                detector.sonar_control(board)



         elif fingers[1] and not fingers[2] and not fingers[3] and fingers[4] and fingers[0]:

             os.startfile(r"C:\Users\Acer\AppData\Local\Microsoft\WindowsApps\Spotify.exe")

         elif fingers == [0,0,0,0,0]:
             pyautogui.hotkey('space')
             time.sleep(0.5)


         elif fingers == [1,0,0,0,1]:

             a =(detector.readtemp(board,9))

             detector.voiceconvert(a[1])



    cv2.rectangle(img, (50,150), (85, 400) , (0, 0 , 255), 3)
    cv2.rectangle(img, (50,int(volbar)), (85, 400) , (255, 0 , 0), cv2.FILLED)
    cv2.putText(img, f'{int(volper)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)

    cvol = int(volume.GetMasterVolumeLevelScalar()*100)
    cv2.putText(img, f'Volume:{int(cvol)}' , (400,50) , cv2.FONT_HERSHEY_DUPLEX , 1 , colorvol, 2 )


    ct= time.time()
    fps=1/(ct-pt)
    pt=ct

    cv2.putText(img, f'FPS: {int(fps)}', (40,50), cv2.FONT_HERSHEY_DUPLEX , 1 , (255, 255, 0), 2 )

    cv2.imshow("Img",img)
    cv2.waitKey(1)


