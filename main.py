import os.path
import time
import base64
import re
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import chromedriver_binary  # これにより、ChromeDriverのパスが自動的に設定される
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as WebdriverService
from dotenv import load_dotenv
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send']
load_dotenv()

username = os.getenv('IDNUMBER')
password_value = os.getenv('PASSWORD')
open_url = os.getenv('URL')
def main():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=8080)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        except Exception as e:
            print(f"An error occurred during the authentication process: {e}")
            return

    try:
        gmail_service = build('gmail', 'v1', credentials=creds)
        results = gmail_service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
            return

        # Read the latest email
        auto_login(gmail_service)


    except HttpError as error:
        print(f'An error occurred: {error}')

def read_latest_email(gmail_service):
    try:
        results = gmail_service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=1).execute()
        messages = results.get('messages', [])

        if not messages:
            print('No new messages found.')
            return

        message_id = messages[0]['id']
        message = gmail_service.users().messages().get(userId='me', id=message_id).execute()
        number  = re.findall(r'\d+', message['snippet'])
        # print('Message snippet: %s' % message['snippet'])
        print('Message snippet: %s' % number[0])
        return number[0]

    except HttpError as error:
        print(f'An error occurred: {error}')


def auto_login(gmail_service):
        webdriver_service = WebdriverService()
        driver = webdriver.Chrome(service=webdriver_service)

        # 自動ログインしたいウェブサイトのURLをコピペ
        driver.get(open_url) 

        # ログインボタンをクリック
        login_button = driver.find_element(By.ID, 'loginButton')
        login_button.click()
        time.sleep(0.5)
        user_id = driver.find_element(By.ID, 'username_input')
        password = driver.find_element(By.ID, 'password_input')
        user_id.send_keys(username)
        password.send_keys(password_value)
        submit_button = driver.find_element(By.ID, 'login_button')
        submit_button.click()
        time.sleep(4.2)

        number = read_latest_email(gmail_service)
        onetime = driver.find_element(By.ID, 'password_input')
        onetime.send_keys(number)
        submit_button = driver.find_element(By.ID, 'login_button')
        submit_button.click()
        time.sleep(30)
        driver.quit()
if __name__ == '__main__':
    main()
