import pandas as pd
import mysql.connector

def sql_string(string):
    return '"' + string + '"'

def prepare_data():
    '''
    Prepares the data for insertion in the airports table
    Receives: None
    Returns: Insertion command with the data from the file brazilian_airports.csv
    '''
    file_name = 'brazilian_airports.csv'
    airport_data = pd.read_csv(file_name, sep=';')

    insert_data = ''
    for line in airport_data.values:
        insert_data += '({},{},{},{},{},{}),'.format(
            sql_string(line[0]),
            sql_string(line[1]),
            sql_string(line[2]),
            sql_string(line[3]),
            line[4],
            line[5]
        )

    insert_command = f'insert into flight_tickets.airports values {insert_data[:-1]};'

    return insert_command

def insert_data(insert_command):
    '''
    Connects to the DB and insert the data on the airports table
    Receives: Insertion command
    Returns: None
    '''
    conn = mysql.connector.connect(
        host='localhost',
        user='edilson',
        password='epdf1991',
        database='flight_tickets',
        auth_plugin='mysql_native_password'
    )

    cursor = conn.cursor(buffered=True)

    try:
        cursor.execute(insert_command)
        conn.commit()
        conn.close()
    except Exception as error:
        print(error)

if __name__ == '__main__':
    command = prepare_data()
    insert_data(command)
