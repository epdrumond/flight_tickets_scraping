#Import libraries
import numpy as np
import pandas as pd

import os
from os.path import join, exists
import requests
import json

from bs4 import BeautifulSoup as bs
from selenium import webdriver

headers = {'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' \
    '(KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}

USER_AGENT = \
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)' \
    ' Chrome/60.0.3112.50 Safari/537.36'
REFERRER = 'https://www.youtube.com'


class expedia_scrapper():

    def __init__(self):
        #Setup the search url in parts
        self.base_url = 'https://www.expedia.com.br/Flights-Search?'
        self.flight_mode_url = 'flight-type=on&mode=search&trip=oneway'
        self.source_url = '&leg1=from%3A{}%2C'
        self.destination_url = 'to%3A{}%2C'
        self.departure_url = 'departure%3A{}%2F{}%2F{}TANYT&options=cabinclass%3Aeconomy&'
        self.passengers_url = 'passengers=children%3A0%2Cadults%3A1%2Cseniors%3A0%2Cinfantinlap%3AY'
        self.end_url = '&fromDate={}%2F{}%2F{}&d1={}'

    def split_date(self, date):
        return date[-2:], date[5:7], date[:4]

    def assemble_url(self):
        '''
        Inserts the request data and assemble the request url
        Receives: source, destination and date for flight search
        Returns: complete url for request
        '''
        self.source_url = self.source_url.format(self.source)
        self.destination_url = self.destination_url.format(self.destination)

        date_part = self.split_date(self.date)
        self.departure_url = self.departure_url.format(
            date_part[0], date_part[1], date_part[2]
        )
        self.end_url = self.end_url.format(
            date_part[0], date_part[1], date_part[2], self.date
        )

        return self.base_url + \
            self.flight_mode_url + \
            self.source_url + \
            self.destination_url + \
            self.departure_url + \
            self.passengers_url + \
            self.end_url

    def extract_from_html(self, raw_data):
        '''
        Extract desired information from the provided html tag element provided
        Receives: Beautiful Soup element with the chunk of HTML containing the
            desired data
        Returns: Desired data in a list of dictionaries
        '''

        self.extracted_data = []
        for data in raw_data:
            #Extract departure and arrival time
            departure_time = data.find('div', {'data-test-id': 'arrival-time'})
            departure_time = str(departure_time.find('span').contents[0])

            #Extract flight duration
            duration = data.find('div', {'data-test-id': 'journey-duration'}).contents[0]

            #Extract ticket price
            ticket_price = data.find('span', {'class': 'uitk-lockup-price'}).contents[0]

            #Extract operating company
            company = data.find('div', {'data-test-id': 'flight-operated'}).contents[0]

            self.extracted_data.append({
                'departure_time': departure_time,
                'duration': duration,
                'ticket_price': ticket_price,
                'company': company
            })

    def process_extracted_data(self):
        '''
        Treats the extracted data in order to adjust it for initial storage
        Receives: Extracted data as a dictionary
        Returns: Processed data also as a dictionary
        '''

        #Set up processed data dictionary
        self.processed_data = []

        for element in self.extracted_data:
            processed_element = {}

            #Departure time
            dep_time = element['departure_time'].split('-')[0].strip().split('h')
            dep_time = np.datetime64(f'{self.date} {dep_time[0].zfill(2)}:{dep_time[1]}:00')
            processed_element.update({'departure_time': dep_time})

            #Arrival time
            duration, stops = element['duration'].split('(')
            hours_minutes = [
                int(''.join([ch for ch in part if ch.isdigit()]))
                for part
                in duration.split()
            ]

            if len(hours) == 1:
                hours = hours_minutes[0]
                minutes = 0
            else:
                hours = hours_minutes[0]
                minutes = hours_minutes[1]

            arv_time = dep_time + np.timedelta64(hours, 'h') + np.timedelta64(minutes, 'm')
            processed_element.update({'arrival_time': arv_time})

            #Stops
            stops = stops.split()[0]
            stops = 0 if stops == 'sem' else int(stops)
            processed_element.update({'stops': stops})

            #Ticket price
            price = ''.join(ch for ch in element['ticket_price'] if ch.isdigit())
            processed_element.update({'ticket_price': int(price)})

            #Company
            processed_element.update({'company': element['company']})

            #Extraction date
            processed_element.update({'extraction_date': self.extraction_date})

            #Origin and destination
            processed_element.update({'source': self.source, 'destination': self.destination})

            self.processed_data.append(processed_element)

    def save_processed_data(self):
        '''
        Save the processed data into a file for later use
        Receives: The processed data list of dictionaries
        Returns: Saved data in a file
        '''

        #Check whether the storage folder already exists and create it otherwise
        base_path = 'extracted_data'
        complete_path = join(base_path, str(self.extraction_date))

        if not exists(complete_path):
            os.makedirs(complete_path)

        #Convert data to a Pandas dataframe
        df = pd.DataFrame(self.processed_data)

        #Save data to a csv file
        file_name = f'{self.source}-{self.destination}_{self.extraction_date}.csv'
        df.to_csv(join(complete_path, file_name), sep=';', index=False)


    def extract_data(self, source, destination, date):
        '''
        Scrape flight ticket data from expedia
        Receives: search parameters (source, destination and departure date)
        Returns: flight ticket data
        '''

        #Storage input as class variables
        self.source = source
        self.destination = destination
        self.date = date
        self.extraction_date = np.datetime64('today')

        #Setup browser for data scraping
        op = webdriver.ChromeOptions()
        op.add_argument('--headless')
        op.add_argument(f'user-agent={USER_AGENT}')
        op.add_argument(f'referrer={REFERRER}')
        browser = webdriver.Chrome(options=op)

        #Get url and extract raw data
        url = self.assemble_url()

        browser.get(url)
        browser.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        #browser.get_screenshot_as_file('test.png')

        soup = bs(browser.page_source, 'html.parser')
        data = soup.find_all('div', {'class': "uitk-layout-flex uitk-layout-flex-justify-content-space-between uitk-layout-flex-gap-six uitk-layout-flex-flex-wrap-nowrap uitk-layout-grid-item"})

        #Extract data from the selected HTML tag
        try:
            self.extract_from_html(data)
        except Exception as error:
            print('Not this again!')
            print(error)

        #Process data for storage
        self.process_extracted_data()

        #Save processed data into a file
        self.save_processed_data()

if __name__ == '__main__':
    scrap = expedia_scrapper()
    scrap.extract_data(source='GRU', destination='FOR', date='2022-06-01')
