import asyncio
import warnings
import time
import telebot
from datetime import datetime, timedelta, time
from telebot.async_telebot import AsyncTeleBot
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from sql_scripts import *
from html_elements import *
from config import *


bot = AsyncTeleBot(telegram_token)


@bot.message_handler(commands=['start'])
async def start(message):
    user_id = message.chat.id

    if not check_user_exists(user_id):
        try:
            add_user_to_db(user_id)
            await bot.send_message(user_id, "Hello, this is a notifier bot!\n"
                                            "I send notifications about the date of the next appointments.\n"
                                            "Now you will receive the latest dates right in this chat.")
        except Exception as error:
            print(error)

    await bot.send_message(user_id, "Please stay tuned for new dates.\nAs soon as they appear - you will receive a notification in this chat.")


class Objects:
    def __init__(self, wait):
        self.wait = wait


    def scroll_to_sign_block(self, browser, sign_block):
        sign_in_block = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, sign_block)))
        browser.execute_script("arguments[0].scrollIntoView();", sign_in_block)


    def login_input(self, login):
        self.wait.until(EC.element_to_be_clickable((By.XPATH, login_line))).send_keys(login)


    def password_input(self, password):
        self.wait.until(EC.element_to_be_clickable((By.XPATH, password_line))).send_keys(password)


    def privacy_button(self, privacy_button):
        self.wait.until(EC.element_to_be_clickable((By.XPATH, privacy_button))).click()


    def log_process(self, sign_button):
        self.wait.until(EC.element_to_be_clickable((By.XPATH, sign_button))).click()


    def page_loaded(self, application_page):
        try:
            self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, application_page)))
            return True
        except:
            return False


    def parse_appointment_date(self, browser, date_block_css):
        try:
            self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, date_block_css)))
            html = browser.page_source
            soup = BeautifulSoup(html, 'html.parser')
            td_element = soup.select_one('.for-layout td.text-right')
            text = td_element.get_text(strip=True)
            text = text.replace(',', '')
            txt_lst = text.split()
            dt_app_text = "{} {}".format(txt_lst[0], txt_lst[1])
            if txt_lst[0].isdigit() == True:
                return True, dt_app_text
            else:
                return False, dt_app_text
        except Exception as error:
            print(error)
            return False, ''


async def work(browser, login, password):
    wait = WebDriverWait(browser, 30)
    objects = Objects(wait)

    try:
        browser.get(link_to_login)
        await asyncio.sleep(1)
    except Exception as error:
        print(error)

    try:
        objects.scroll_to_sign_block(browser, sign_block)
        await asyncio.sleep(0.3)
        objects.login_input(login)
        await asyncio.sleep(0.3)
        objects.password_input(password)
        await asyncio.sleep(0.3)
        objects.privacy_button(privacy_button)
        await asyncio.sleep(0.3)
        objects.log_process(sign_button)
        await asyncio.sleep(0.3)
    except Exception as error:
        print(error)

    try:
        if objects.page_loaded(application_page) == True:
            user_id = get_user_id(login)
            link_to_datapage = link_to_data.format(user_id)
            browser.get(link_to_datapage)
            await asyncio.sleep(5)

            date_status, date_app = objects.parse_appointment_date(browser, date_block_css)
            if date_status == True:
                prev_date = get_prev_date_time()
                if prev_date != date_app:
                    add_date_time(date_app)

                    users = select_users()
                    for usr in users:
                        if get_user_status(usr) == 0:
                            change_user_status(usr, 1)
                        bot = telebot.TeleBot(telegram_token)
                        bot.send_message(usr, date_app)
                elif prev_date == date_app:
                    users = select_users()
                    for usr in users:
                        if get_user_status(usr) == 0:
                            bot = telebot.TeleBot(telegram_token)
                            bot.send_message(usr, date_app)
                            change_user_status(usr, 1)


            elif date_status == False and date_app == "No Appointments":
                add_ban_date(login)
    except Exception as error:
        print(error)
    browser.quit()


async def check_user_info():
    current_time = datetime.now().time().replace(microsecond=0)

    start_time = time(7, 0)
    end_time = time(0, 0)

    if (current_time >= start_time) and (current_time > end_time):
        add_user_data_to_db()
        login_data = user_data_from_db()

        options = webdriver.ChromeOptions()
        options.binary_location = '/usr/bin/google-chrome'
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        service = webdriver.chrome.service.Service(path_to_chromedriver)
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        for lp in login_data:
            login, password = lp
            if get_login_status(login) == 1:
                browser = webdriver.Chrome(service=service, options=options)
                browser.maximize_window()
                await work(browser, login, password)
                await asyncio.sleep(delay)
            elif get_login_status(login) == 0:
                now = datetime.now()
                formatted_date1 = now.strftime("%H.%d.%m")
                formatted_date2 = get_ban_date(login)

                date1 = datetime.strptime(formatted_date1, "%H.%d.%m")
                date2 = datetime.strptime(formatted_date2, "%H.%d.%m")

                if abs(date1 - date2) >= timedelta(hours=global_delay):
                    del_ban_date(login)
                    browser = webdriver.Chrome(service=service, options=options)
                    browser.maximize_window()
                    await work(browser, login, password)
                    await asyncio.sleep(delay)
    elif (current_time >= end_time) and (current_time < start_time):
        pass


async def data_mining():
    try:
        while True:
            await check_user_info()
            await asyncio.sleep(1)
    except Exception as error:
        print(error)


async def main():
    bot_task = asyncio.create_task(bot.polling())
    data_mining_task = asyncio.create_task(data_mining())

    await asyncio.gather(bot_task, data_mining_task)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    