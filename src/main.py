import selenium.webdriver as webdriver

from cv2 import QRCodeDetector

import sys
from queue import Queue
from datetime import datetime

from VideoHelper import VideoGet, VideoShow, highlight_qr, add_text
from WebScraper import MathnasiumSite

TEXT_SCREEN_TIMEOUT_SEC = 1.5

DEFAULT_MESSAGE = "Scan QR Code"

def main():
    camera_only = False
    if len(sys.argv) > 1 and sys.argv[1] == "-c":
            print("Running in Camera Only Mode")
            camera_only = True

    video_getter = VideoGet().start()
    video_shower = VideoShow(video_getter.frame).start()

    queue = Queue()
    message_queue = Queue()
    signed_in: dict[str, datetime] = {}

    site_handler = None        

    try:
        if not camera_only:
            driver = webdriver.Chrome()
            site_handler = MathnasiumSite(driver)
            site_handler.start(queue, message_queue)

        last_detected = datetime.now()
        message = None
        detector = QRCodeDetector()
        while True:
            frame = video_getter.frame
            value_found, data, points, _ = detector.detectAndDecodeMulti(frame)
            if value_found:
                frame = highlight_qr(frame, data, points)
                for d in data:
                    if d and d not in queue.queue and d:
                        student_prev_signed_in = d in signed_in.keys()
                        if not student_prev_signed_in or (datetime.now() - signed_in[d]).total_seconds() > 60:
                            queue.put(d)
                            if not student_prev_signed_in:
                                signed_in[d] = datetime.now()
                            else:
                                signed_in.pop(d, None)
                            print(f"Added {d} to queue")

            if (datetime.now() - last_detected).total_seconds() > TEXT_SCREEN_TIMEOUT_SEC:
                message = None
                if not message_queue.empty():
                    message = message_queue.get()
                    last_detected = datetime.now()

            frame = add_text(frame, message if message else DEFAULT_MESSAGE)

            video_shower.frame = frame

            if video_shower.stopped:
                break
    except Exception as e:
        print(e)
    finally:
        video_getter.stop()
        video_shower.stop()
        if not camera_only and site_handler is not None:
            site_handler.stop()
        sys.exit() 


if __name__ == "__main__":
    main()