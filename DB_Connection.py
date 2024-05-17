import psycopg2
import maskpass

password = 'password'

def db_connect():
    '''
    Creates and connects to the Data Base
    '''
    decoded_pass = 0
    db = psycopg2.connect(
        user = 'projectuser',
        password = int(decoded_pass),
        host = '127.0.0.1',
        port = '5432',
        database = 'ProjectDB'
    )
    return db