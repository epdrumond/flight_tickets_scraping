import pandas as pd
import numpy as np
import time
from tqdm import tqdm

from scrapper import expedia_scrapper
import mysql.connector

#Connect to the DB
conn = mysql.connector.connect(
    host='localhost',
    user='edilson',
    password='epdf1991',
    database='flight_tickets',
    auth_plugin='mysql_native_password'
)

#Load all airports combinations not in the same state
airport_query = '''
select
	t1.code as origin_code,
	t2.code as destination_code
from
	flight_tickets.airports as t1
	left join flight_tickets.airports as t2 on (t1.state != t2.state)
'''
airports = pd.read_sql(airport_query, conn)

for origin, destination in tqdm(airports.values):
    reference_date = str(np.datetime64('today') + 30)

    scrap = expedia_scrapper()
    scrap.extract_data(
        source=origin,
        destination=destination,
        date=reference_date
    )

    time.sleep(0.5)
