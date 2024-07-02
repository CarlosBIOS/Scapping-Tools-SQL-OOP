import selectorlib
import sqlite3
import requests
from twilio.rest import Client
import time
from os import getenv
import smtplib


class Events:

    def __init__(self, yaml_file):
        self.headers: dict = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/39.0.2171.95 Safari/537.36'
        }
        self.yaml_file: str = yaml_file

    def scrape(self, url: str) -> str | None:
        """Scrape the page source from the `url`"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as error:
            print(f"Error scraping url: {error}")
            return None

    def extract(self, source: str) -> str:
        """Vai extrair uma específica data/value from a `source`"""
        # Tenho que criar o extract.yaml no meu directory, se não, não vai dar!!
        # E tenho que acrescentar código:
        # tours(pode ser qualquer nome):\n(mudo de linha) css: '#displaytimer'(posso ir ao site, inspecionar elemento,
        # copy, copy selector)
        extractor = selectorlib.Extractor.from_yaml_file(self.yaml_file)
        value: str = extractor.extract(source)['tours']
        return value


class Send:

    def __init__(self):
        # port: int = 465  # port do SSL
        self.port: int = 587
        self.host: str = 'smtp.gmail.com'
        # Hotmail: smtp.live.com
        # Outlook: outlook.office365.com
        # Yahoo: smtp.mail.yahoo.com
        self.username: str = 'portfoliowebsitepython@gmail.com'
        self.password: str = getenv('PASSWORD_PORTFOLIO_WEBSITE')
        self.receiver: str = self.username
        self.mynumber: str = getenv('my_number')
        self.number: str = getenv('phone_number_twilio')
        self.account: str = getenv('account_sid_twilio')
        self.token: str = getenv('auth_token_twilio')

    def email(self, message: bytes | str) -> None:
        with smtplib.SMTP(self.host, self.port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.username, self.receiver, message.encode('utf-8'))
        print('Email was sent!')

    def sms(self, message: bytes | str) -> None:
        client = Client(self.account, self.token)
        client.messages.create(from_=self.number, body=message, to=self.mynumber)
        print('SMS was sent!\n')


class DataBase:

    def __init__(self, database_path):
        self.connection = sqlite3.connect(database_path)

    def store(self, extracted: str) -> None:
        # """Vai guardar os `extracted` num documento de texto"""
        # with open('data.txt', 'a', encoding='utf-8') as file:
        #     file.write(extracted + '\n')
        band, city, date = extracted.split(', ')
        cursor = self.connection.cursor()
        cursor.execute('INSERT INTO events VALUES(?,?,?)', (band, city, date))
        self.connection.commit()

    def read(self, extracted: str) -> list:
        # with open('data.txt', encoding='utf-8') as file:
        #     data: list = file.readlines()
        band, city, date = extracted.split(', ')
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM events WHERE city=? AND band=? AND date=?', (city, band, date))
        return cursor.fetchall()

    def __str__(self):
        return 'Reads and Stores data from a database'


def main(url: str) -> None:
    events = Events('extract.yaml')
    print(events.scrape(url))
    while True:
        extracted: str = events.extract(events.scrape(url))
        if extracted != 'No upcoming tours':
            database = DataBase('tutorial.db')
            data: list = database.read(extracted)
            if not data:
                database.store(extracted)
                message: str = '''\
Subject: A new content

Hey, new event was found: {}
'''.format(extracted)
                send = Send()
                send.email(message)
                send.sms(message)
        time.sleep(2)


if __name__ == "__main__":
    main(url='http://programmer100.pythonanywhere.com/tours/')
