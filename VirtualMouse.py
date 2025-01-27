import cv2
import numpy as np
import HandTrackingModule as htm
import time
import math
import pyautogui

wCam,hCam = 640,480
frameR = 100 #Frame Reduction
smoothening = 2

pTime = 0
plocX,plocY = 0,0
clocX,clocY = 0,0

cap = cv2.VideoCapture(0)


cap.set(cv2.CAP_PROP_FRAME_WIDTH,wCam)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,hCam)

detector  = htm.handDetetctor(maxHands=1)
wScr,hScr = pyautogui.size()
indFingRaised = False
MidFingRaised = False
pyautogui.FAILSAFE=False

while True:
    #1. Find hand landmarks
    success,img = cap.read()
    img  = detector.findHands(img)
    lmList = detector.findPosition(img,draw = False)

    cv2.rectangle(img,(frameR,frameR),(wCam-frameR,hCam-frameR),(255,0,255),2)

    #2. Get the tip of the index and middle fingers
    if len(lmList)!=0:
        x1,y1 = lmList[8][1:]
        x2,y2 = lmList[12][1:]
        cx,cy = (x1+x2)//2,(y1+y2)//2

        #3. check which fingers are up
        if (lmList[0][2]-lmList[8][2])/(lmList[0][2]-lmList[5][2]) > 1.7: #index - threshold = 1.7 is raised
            indFingRaised = True
        if (lmList[0][2]-lmList[12][2])/(lmList[0][2]-lmList[9][2]) > 1.7: #middle finger - threshold = 1.7 is raised
            MidFingRaised = True

        #4. only index finger: moving mode
        if indFingRaised and not MidFingRaised:

            #5. convert coordinates

            x3 = np.interp(x1,(frameR,wCam-frameR),(0,wScr))
            y3 = np.interp(y1,(frameR,hCam-frameR),(0,hScr))
            #6. Smoothen values
            clocX = plocX+(x3-plocX) / smoothening
            clocY = plocY+(y3-plocY) / smoothening


            #7. Move mouse
            pyautogui.moveTo(wScr-clocX,clocY)
            cv2.circle(img,(x1,y1),15,(255,0,255),cv2.FILLED)
            plocX,plocY = clocX,clocY

        #8. Both index and middle fingers up: clicking mode
        if indFingRaised and MidFingRaised:
            #9. Find distance between fingers
            length = math.hypot(x2-x1,y2-y1)

            cv2.line(img,(x1,y1),(x2,y2),(255,0,255),3)
            cv2.circle(img,(x1,y1), 15, (255,0,255),cv2.FILLED)
            cv2.circle(img,(x2,y2), 15, (255,0,255),cv2.FILLED)
            cv2.circle(img,(cx,cy), 15, (0,0,255),cv2.FILLED)
            #10. click mouse if distance short
            if length<25:
                cv2.circle(img,(cx,cy), 15, (0,255,0),cv2.FILLED)
                pyautogui.click()
        
        

    #11. Frame rate
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img,str(int(fps)),(20,50),cv2.FONT_HERSHEY_COMPLEX,2,(255,0,0),3)

    #12. Display
    cv2.imshow("image", img)
    indFingRaised = False
    MidFingRaised = False
    
    key = cv2.waitKey(1)
    if key == ord('q'):  # Check if 'q' is pressed
        print("Exiting...")
        break