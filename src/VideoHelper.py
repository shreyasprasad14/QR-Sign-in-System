from threading import Thread
import cv2

from numpy import ndarray
from typing import Iterable

FONT = cv2.FONT_HERSHEY_SIMPLEX
SQUARE_COLOR = (0, 255, 0)
DEFAULT_TEXT_COLOR = (0, 0, 255)
TEXT_PADDING_PX = 16

class VideoGet:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):    
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read()

    def stop(self):
        self.stopped = True

class VideoShow:
    """
    Class that continuously shows a frame using a dedicated thread.
    """

    def __init__(self, frame=None):
        self.frame = frame
        self.stopped = False

    def start(self):
        Thread(target=self.show, args=()).start()
        return self

    def show(self):
        while not self.stopped:
            cv2.imshow("Video", self.frame)
            if cv2.waitKey(1) == ord("q"):
                self.stopped = True

    def stop(self):
        self.stopped = True

def highlight_qr(frame: ndarray, decoded_info: Iterable[str], points: ndarray) -> ndarray:
    frame = cv2.polylines(frame, points.astype(int), True, SQUARE_COLOR, 3)

    for s, p in zip(decoded_info, points):
        frame = cv2.putText(
            frame, s, p[0].astype(int), FONT, 
            1, DEFAULT_TEXT_COLOR, 2, cv2.LINE_AA
        )

    return frame

def add_text(frame: ndarray, text: str, color: tuple[int, int, int] | None) -> ndarray:        
    text_size = cv2.getTextSize(text, FONT, 1, 2)[0]
    text_x = (frame.shape[1] - text_size[0]) // 2
    text_y = text_size[1] + TEXT_PADDING_PX
    text_pos = (text_x, text_y)
    return cv2.putText(frame, text, text_pos, FONT, 1, color if color else DEFAULT_TEXT_COLOR, 2, cv2.LINE_AA)