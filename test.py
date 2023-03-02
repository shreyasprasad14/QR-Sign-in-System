import cv2
import time
vid = cv2.VideoCapture(0)

while True:
    start = time.time()
    ret, frame = vid.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    print(1/(time.time() - start))