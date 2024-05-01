import psycopg2
import maskpass

def db_connect():
    '''
    Creates and connects to the Data Base
    '''
    decoded_pass = 0
    db = psycopg2.connect(
        user = 'user123',
        password = int(decoded_pass),
        host = '127.0.0.1',
        port = '1234',
        database = 'test321'
    )
    return db