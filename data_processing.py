import pandas as pd
import mysql.connector

def insert_timezone(date, timezone):
    '''
    Insert timezone information to a date value
    Receives: date and timezone
    Returns: date with timezone
    '''
    signal = '-' if timezone < 0 else ''
    str_timezone = f'{signal}{str(abs(timezone)).zfill(2)}00'

    return f'{date} {str_timezone}'

def process_data(df, conn):
    '''
    Apply the necessary treatments in the data pre loading into the DB table
    Receives: extracted data, as saved in file
    Returns: data ready for DB loading
    '''

    #Add timezone to the timestamp fields
    origin = df['source'][0]
    destination = df['destination'][0]

    ts_query = '''
    select code, timezone
    from flight_tickets.airports
    where code in ("{}","{}")
    '''.format(origin, destination)

    ts_data = pd.read_sql(ts_query, conn)

    timestamp_cols = ['departure_time', 'arrival_time']
    for col, code in zip(timestamp_cols, (origin, destination)):
        timezone = ts_data[ts_data['code'] == code]['timezone'].values[0]
        df[col] = [insert_timezone(date, timezone) for date in df[col]]

    print(df)
    return 0

if __name__ == '__main__':
    conn = mysql.connector.connect(
        host='localhost',
        user='edilson',
        password='epdf1991',
        database='flight_tickets',
        auth_plugin='mysql_native_password'
    )

    example_file = '/home/edilson/Desktop/Edilson/Python/flight_tickets/extracted_data/2022-06-01/CGR-THE_2022-06-01.csv'
    df = pd.read_csv(example_file, sep=';')
    process_data(df, conn)
