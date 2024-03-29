import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from queue import Queue
from threading import Thread

import os
from dotenv import load_dotenv

import pymongo
from pymongo import MongoClient

from datetime import datetime

TIMEOUT_SEC = 6

PRINT_PREFIX = "[WD]: "

class MathnasiumSite:
    def __init__(self, driver: webdriver):
        self.driver = driver
        self.stopped = False

        self.mongo_client = MongoClient(os.getenv("MONGO_URI"))

        username, password = MathnasiumSite.get_environment_variables()
        self.load_student_roster_page(username, password)
        self.student_rows = self.get_table_rows()

    def start(self, queue: Queue, message_queue: Queue) -> None:
        Thread(target=self.sign_in_process, args=(queue, message_queue)).start()
    
    def stop(self) -> None:
        self.driver.quit()
        self.mongo_client.close()
        self.stopped = True
    
    def sign_in_process(self, queue: Queue, message_queue: Queue) -> None:
        while True:
            if self.stopped: break
            if queue.empty(): continue

            s = queue.get()
            db = self.mongo_client["mathnasium"]
            collection = db["students"]
            student = collection.find_one({"name": s})
            if student:
                if student["date"] and (datetime.now() - student["date"]).total_seconds() < 2 * 60:
                    #message_queue.put(f"{s} already signed in")
                    continue
                else:
                    collection.update_one(
                        {"name": s},
                        {"$set": {"date": datetime.now()}}, upsert=True
                    )
            else:
                collection.insert_one({"name": s, "date": datetime.now()})

            row = self.get_student_row(s)

            if not row:
                error_message = f"Unable to find student {s}"
                if error_message not in message_queue.queue:
                    message_queue.put(error_message)
                continue

            if self.sign_in_student(row):
                message_queue.put(f"Signed in {s}")
            else:
                collection.update_one(
                    {"name": s},
                    {"$set": {"date": datetime.now()}}, upsert=True
                )
                self.driver.refresh()
                message_queue.put(f"Unable to sign in {s}")

    def load_student_roster_page(self, username: str, password: str) -> None:
        MathnasiumSite.output("Loading Page...")
        self.driver.get("https://radius.mathnasium.com/")

        username_entry = self.driver.find_element(By.ID, "UserName")
        username_entry.send_keys(username)

        password_entry = self.driver.find_element(By.ID, "Password")
        password_entry.send_keys(password)

        login_button = self.driver.find_element(By.ID, "login")
        self.driver.execute_script("document.getElementById('login').scrollIntoView();")
        login_button.click()

        #try:
        connected_cookie = WebDriverWait(self.driver, timeout=TIMEOUT_SEC).until(lambda d: d.get_cookie("Connected"))
        #except:
        #    raise Exception("Unable to Login")
        
        if not connected_cookie or connected_cookie["value"] != "UserConnected":
            raise Exception("Unable to Login")

        MathnasiumSite.output("Logged in as: " + username)

        self.driver.get("https://radius.mathnasium.com/Attendance/StudentCheckIn")
        self.driver.get('chrome://settings/')
        zoom = 0.25 #for example 0.5, or 1.5 or 2.0 and so on
        self.driver.execute_script(f'chrome.settingsPrivate.setDefaultZoom({zoom});')
        self.driver.back()
        
        try:
            WebDriverWait(self.driver, timeout=TIMEOUT_SEC).until(lambda d: d.find_element(By.CLASS_NAME, "activeRow"))
        except:
            raise Exception("Unable to load check-in page") 

        MathnasiumSite.output("Check-In Page Loaded")
    
    def get_signed_in_students(self) -> list[str]:
        signed_in_students = []
        for row in self.student_rows:
            try:
                last_activity_cell = self.driver.find_element(By.CLASS_NAME, "LastActivityCell")
                if "checked in" in last_activity_cell.text:
                    signed_in_students.append(row.find_element(By.CLASS_NAME, "StudentNameCell").text)
            except: continue
        return signed_in_students
                
    def get_table_rows(self) -> list[WebElement]:
        try:
            table = self.driver.find_element(By.ID, "StudentCheckInTable")
            return table.find_elements(By.TAG_NAME, "tr")
        except:
            raise Exception("Unable to find student table")

    def get_student_row(self, student_name: str) -> WebElement:
        target_student_row = None

        for row in self.student_rows:
            try:
                name_element = row.find_element(By.CLASS_NAME, "StudentNameCell")
            except:
                continue
            name = name_element.text
            if name == student_name:
                target_student_row = row
                break
        
        return target_student_row

    def sign_in_student(self, row: WebElement) -> bool:
        try:
            button_container = row.find_element(By.CLASS_NAME, "ButtonCell")
            button = button_container.find_element(By.CLASS_NAME, "statusCheckBoxBtn")
            button.click()

            WebDriverWait(self.driver, timeout=TIMEOUT_SEC).until(lambda d: d.find_element(By.ID, "kendoWindow").is_displayed())
            
            dialog = self.driver.find_element(By.ID, "kendoWindow")
            # TODO: See if below is necessary
            WebDriverWait(self.driver, timeout=TIMEOUT_SEC).until(lambda d: d.find_element(By.ID, "confirmAttBtn"))
            confirm_button = dialog.find_element(By.ID, "confirmAttBtn")
            confirm_button.click()
            return True
        except Exception as e:
            return False

    @staticmethod
    def output(msg: str):
        print(PRINT_PREFIX + msg)

    @staticmethod
    def get_environment_variables() -> tuple[str, str]:
        if not os.path.exists(".env"):
            raise Exception("No .env file found")
        
        load_dotenv()
        username = os.getenv("MathnasiumUsername")
        password = os.getenv("MathnasiumPassword")

        if not username or not password:
            raise Exception("Username or password not set as environment variable")

        return username, password