#Import libraries
import requests
import json
from bs4 import BeautifulSoup as bs
from selenium import webdriver

from lxml import html
from collections import OrderedDict

headers = {'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' \
    '(KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}

USER_AGENT = \
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)' \
    ' Chrome/60.0.3112.50 Safari/537.36'

class expedia_scrapper():

    def __init__(self):
        #Setup the search url in parts
        self.base_url = 'https://www.expedia.com.br/Flights-Search?'
        self.flight_mode = 'flight-type=on&mode=search&trip=oneway'
        self.source = '&leg1=from%3A{}%2C'
        self.destination = 'to%3A{}%2C'
        self.departure = 'departure%3A{}%2F{}%2F{}TANYT&options=cabinclass%3Aeconomy&'
        self.passengers = 'passengers=children%3A0%2Cadults%3A1%2Cseniors%3A0%2Cinfantinlap%3AY'
        self.url_end = '&fromDate={}%2F{}%2F{}&d1={}'

    def split_date(self, date):
        return date[-2:], date[5:7], date[:4]

    def assemble_url(self, source, destination, date):
        '''
        Inserts the request data and assemble the request url
        Receives: source, destination and date for flight search
        Returns: complete url for request
        '''
        self.source = self.source.format(source)
        self.destination = self.destination.format(destination)

        date_part = self.split_date(date)
        self.departure = self.departure.format(
            date_part[0], date_part[1], date_part[2]
        )
        self.url_end = self.url_end.format(
            date_part[0], date_part[1], date_part[2], date
        )

        return self.base_url + \
            self.flight_mode + \
            self.source + \
            self.destination + \
            self.departure + \
            self.passengers + \
            self.url_end

    def extract_from_html(self, raw_data):
        '''
        Extract desired information from the provided html tag element provided
        Receives: Beautiful Soup element with the chunk of HTML containing the
            desired data
        Returns: Desired data in a dictionary
        '''

        #Extract departure and arrival time
        departure_time = raw_data.find('div', {'data-test-id': 'arrival-time'})
        print(departure_time)
        print(type(departure_time))
        departure_time = str(departure_time.find('span').contents[0])


    def extract_data(self, source, destination, date):
        '''
        Scrape flight ticket data from expedia
        Receives: search parameters (source, destination and departure date)
        Returns: flight ticket data
        '''

        #Setup browser for data scraping
        op = webdriver.ChromeOptions()
        op.add_argument('--headless')
        op.add_argument(f'user-agent={USER_AGENT}')
        browser = webdriver.Chrome(options=op)

        #Get url and extract raw data
        url = self.assemble_url(source, destination, date)
        browser.get(url)
        browser.get_screenshot_as_file('test.png')

        soup = bs(browser.page_source, 'html.parser')
        data = soup.find('div', {'class': "uitk-layout-flex uitk-layout-flex-justify-content-space-between uitk-layout-flex-gap-six uitk-layout-flex-flex-wrap-nowrap uitk-layout-grid-item"})

        #print(data)
        try:
            self.extract_from_html(data)
        except Exception as error:
            print('Not this again!')
            print(error)

if __name__ == '__main__':
    scrap = expedia_scrapper()
    scrap.extract_data(source='GRU', destination='CWB', date='2022-06-01')
