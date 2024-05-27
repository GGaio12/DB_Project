import psycopg2

def db_connect():
    '''
    Creates and connects to the Data Base
    '''
    db = psycopg2.connect(
        user = 'projectuser',
        password= 'password',
        host = '127.0.0.1',
        port = '5432',
        database = 'ProjectDB'
    )
    return db