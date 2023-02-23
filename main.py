import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC


from selenium.webdriver.common.keys import Keys

import time as timer

import cv2
from cv2 import VideoCapture, QRCodeDetector

import os
import sys
from dotenv import load_dotenv

from threading import Event, Thread

from queue import Queue

TIMEOUT_SEC = 6

def main():
    load_dotenv()
    username = os.getenv("MathnasiumUsername")
    password = os.getenv("MathnasiumPassword")

    if not username or not password:
        raise Exception("Username or password not set as environment variable")

    driver = webdriver.Chrome()

    vid = None

    table_rows = []

    queue = Queue()
    kill_event = Event()

    def sign_in_process(driver: webdriver, table_rows: list[WebElement], queue: Queue) -> None:
        while True:
            if kill_event.is_set():
                break
            if not queue.empty():
                table_rows = sign_in(driver, queue.get(), table_rows, queue)

    def scan_qr_process(vid: VideoCapture, detect: QRCodeDetector, queue: Queue, display_stream: bool = False) -> None:
        while True:
            if kill_event.is_set():
                break
            data = scan_qr(vid, detect, display_stream)
            if data:
                queue.put(data)
    
    try:
        load_page(driver, username, password)

        vid = cv2.VideoCapture(0)
        detect = cv2.QRCodeDetector()
        

        cam_thread = Thread(target=scan_qr_process, args=(vid, detect, queue, True))
        cam_thread.start()

        sign_in_thread = Thread(target=sign_in_process, args=(driver,table_rows, queue))
        sign_in_thread.start()

        while True:
            key = cv2.waitKey(1)
            if key == ord("q"):
                kill_event.set()
                break

        cam_thread.join()
        sign_in_thread.join()
    except Exception as e:
        print(e)
    finally:
        vid.release()
        cv2.destroyAllWindows()
        driver.quit()
        sys.exit()

def load_page(driver: webdriver, username: str, password: str) -> None:
    driver.get("https://radius.mathnasium.com/")

    username_entry = driver.find_element(By.ID, "UserName")
    username_entry.send_keys(username)

    password_entry = driver.find_element(By.ID, "Password")
    password_entry.send_keys(password)

    login_button = driver.find_element(By.ID, "login")
    login_button.click()

    try:
        connected_cookie = WebDriverWait(driver, timeout=TIMEOUT_SEC).until(lambda d: d.get_cookie("Connected"))
    except:
        raise Exception("Unable to Login")
    
    if not connected_cookie or connected_cookie["value"] != "UserConnected":
        raise Exception("Unable to Login")

    driver.get("https://radius.mathnasium.com/Attendance/StudentCheckIn")
    
    try:
        _ = WebDriverWait(driver, timeout=TIMEOUT_SEC).until(lambda d: d.find_element(By.CLASS_NAME, "activeRow"))
    except:
        raise Exception("Unable to load check-in page")    

def scan_qr(vid: VideoCapture, detect: QRCodeDetector, display_stream: bool = False) -> str | None:
    if not vid or not detect:
        raise Exception("Invalid video capture or QR code detector")

    if not vid.isOpened():
        raise Exception("Video capture is not open")

    _, img = vid.read()

    data, _, _ = detect.detectAndDecode(img)

    if display_stream:
        cv2.imshow("QR Code", img)

    return data

def sign_in(driver: webdriver, student_name: str, table_rows: list[WebElement]) -> list[WebElement]:
    if table_rows == []:
        try:
            table = driver.find_element(By.ID, "StudentCheckInTable")
            table_rows = table.find_elements(By.TAG_NAME, "tr")
        except:
            raise Exception("Unable to find student table")

    target_student_row = None

    for row in table_rows:
        try:
            name_element = row.find_element(By.CLASS_NAME, "StudentNameCell")
        except:
            continue
        name = name_element.text
        if name == student_name:
            target_student_row = row
            break
    
    if not target_student_row:
        print(f"[ERR]: Student {student_name} not found")
        return table_rows
    
    try:
        button_container = target_student_row.find_element(By.CLASS_NAME, "ButtonCell")
        button = button_container.find_element(By.CLASS_NAME, "statusCheckBoxBtn")
        button.click()

        _ = WebDriverWait(driver, timeout=TIMEOUT_SEC).until(lambda d: d.find_element(By.ID, "kendoWindow").is_displayed())
        
        dialog = driver.find_element(By.ID, "kendoWindow")
        # TODO: See if below is necessary
        WebDriverWait(driver, timeout=TIMEOUT_SEC).until(lambda d: d.find_element(By.ID, "confirmAttBtn"))
        confirm_button = dialog.find_element(By.ID, "confirmAttBtn")
        confirm_button.click()
        # TODO: See if below is necessary
        ActionChains(driver).move_to_element(confirm_button).click().perform()
        print(f"Signed in {student_name}")

    except Exception as e:
        print(f"Unable to sign in {student_name}")
    finally:
        return table_rows

if __name__ == "__main__":
    main()