import math
import cv2
import mediapipe as mp
import time
import speech_recognition
#import autopy
import numpy as np
import sys
import pyautogui
from pymata4 import pymata4
import pyaudio

import pyttsx3




class handDetector():
    def __init__(self, mode=False, maxHands=2, modelcomp=1, detectionCon=0.5, trackCon=0.5):
        self.recognizer = speech_recognition.Recognizer()
        self.mode = mode
        self.maxHands = maxHands
        self.modelcomp = modelcomp
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelcomp,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipid = [4, 8, 12, 16, 20]

    def findHands(self, img, draw=True):

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        self.results = self.hands.process(imgRGB)

        # print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:

            for handLms in self.results.multi_hand_landmarks:

                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)

                    #print(len(self.results.multi_hand_landmarks))
        return img

    def findPosition(self, img, handNo=0, draw=True):

        xList=[]
        yList = []
        bbox=[]

        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                # print(id, cx, cy)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)


            xmin,xmax = min(xList), max(xList)
            ymin,ymax = min(yList), max(yList)

            bbox= xmin, ymin, xmax, ymax

            if draw:
                cv2.rectangle(img, (bbox[0]-20, bbox[1]-20), (bbox[2]+20, bbox[3]+20), (0,255,0), 2)
        return self.lmList, bbox

    def fingersUp(self, img):
        finger = []

        handside = self.LoRside(img)

        # Thumb
        if handside == 1:
            if self.lmList[self.tipid[0]][1] < self.lmList[self.tipid[0] - 1][1]:
                finger.append(1)
            else:
                finger.append(0)

                # Four Fingers

            for id in range(1, 5):
                if self.lmList[self.tipid[id]][2] < self.lmList[self.tipid[id] - 2][2]:
                    finger.append(1)
                else:
                    finger.append(0)

                #print(finger)
        elif handside == -1:
            if self.lmList[self.tipid[0]][1] > self.lmList[self.tipid[0] - 1][1]:
                finger.append(1)
            else:
                finger.append(0)

                # Four Fingers

            for id in range(1, 5):
                if self.lmList[self.tipid[id]][2] < self.lmList[self.tipid[id] - 2][2]:
                    finger.append(1)
                else:
                    finger.append(0)
        return finger

    def findDistance(self, p1, p2, img, draw=True):

        x1, y1 = self.lmList[p1][1], self.lmList[p1][2]
        x2, y2 = self.lmList[p2][1], self.lmList[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2


        if draw:

            cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)

            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        length = math.hypot((x1 - x2), (y1 - y2))
        return length, img, [x1, y1, x2, y2, cx, cy]

    def LoRside(self, img):

        if self.results.multi_hand_landmarks:
            # Get the landmarks for the first hand
            hand_landmarks = self.results.multi_hand_landmarks[0]

            # Check if the hand is the left or right hand
            if hand_landmarks.landmark[self.mpHands.HandLandmark.WRIST].x < 0.5:
                hand_side = -1
            else:
                hand_side = 1

            return hand_side
        else:
            return 0

    #def openapp(self):



    def NoOfHandsonScreen(self, img):

        if self.results.multi_hand_landmarks:

            for handLms in self.results.multi_hand_landmarks:
                return len(self.results.multi_hand_landmarks)

    def sonar_control(self,board,trig,echo):

        board.set_pin_mode_sonar(trig, echo)

        ans = board.sonar_read(trig)


        # print(ans)
        a = 20
        # print(a)
        b = ans[0]
        print(b)

        # print(b)
        if (b > 5 and b < a):
            pyautogui.hotkey('right')
            time.sleep(0.5)

                # print(a)
        if (b < 50 and b > a):
            pyautogui.hotkey('left')
            time.sleep(0.5)


    def readtemp(self, board, pinNo):

        board.set_pin_mode_dht(pinNo, sensor_type=11)

        a = board.dht_read(pinNo)
        time.sleep(2)
        b = board.dht_read(pinNo)
        return(b)


    def voiceconvert(self,b):
        engine = pyttsx3.init()

        a = "The temperature right now is"+(str)(b)+"degree Celsius"

        engine.say(a)
        engine.runAndWait()
        engine.stop()

    def voice_recognition(self):
        with speech_recognition.Microphone() as user_voice_input_source:
            self.recognizer.adjust_for_ambient_noise(user_voice_input_source, duration=1)

            try:
                print("Listening...")
                user_voice_input = self.recognizer.listen(user_voice_input_source, timeout=5, phrase_time_limit=5)

                # Recognize speech using Google Web Speech API
                user_voice_text = self.recognizer.recognize_google(user_voice_input)

                # Convert to lowercase for uniformity
                user_voice_text = user_voice_text.lower()

                print("Recognized Text:", user_voice_text)

                return user_voice_text

            except speech_recognition.WaitTimeoutError:
                print("Speech recognition timed out. No speech detected.")
                return None
            except speech_recognition.UnknownValueError:
                print("Speech recognition could not understand the audio.")
                return None
            except speech_recognition.RequestError as e:
                print("Could not request results from Google Web Speech API; {0}".format(e))
                return None

def main():

    pTime = 0

    cap = cv2.VideoCapture(0)

    detector = handDetector()

    while True:
        success, img = cap.read()

        img = cv2.flip(img, 1)
        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        #detector.fingercounter(img, lmList)

        #if len(lmList) != 0:
            #print(lmList[4])

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        hand_side = detector.LoRside(img)
        noOfhands = detector.NoOfHandsonScreen(img)

        #print(noOfhands)

        #print(detector.LoRside(img))

        #print(detector.Voicerec())

        #print(f"The detected hand is on the {hand_side}")

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)
        cv2.imshow("Image", img)
        cv2.waitKey(1)




if __name__ == "__main__":
    main()
