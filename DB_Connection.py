import psycopg2
import maskpass

def db_connect():
    '''
    Creates and connects to the Data Base
    '''
    decoded_pass = 0
    db = psycopg2.connect(
        user = '',
        password = int(decoded_pass),
        host = '127.0.0.1',
        port = '1234',
        database = ''
    )
    return db