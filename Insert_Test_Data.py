from DB_Connection import db_connect
from psycopg2 import sql
import pandas as pd
import numpy as np
import bcrypt

# Function to insert data into the database
def insert_data(table_name, columns, data, cursor):
    # If table is prescription just add a prescription_id with auto-increment (SERIAL)
    if(table_name == 'prescription'):
        for _ in data.iterrows():
            cursor.execute(""" INSERT INTO prescription DEFAULT VALUES; """)
    else:
        # Removing from columns the columns that are SERIAL type.
        serial_columns = get_serial_columns(table_name, cursor)
        columns = [col for col in columns if col not in serial_columns]
        # Constructing query to send
        insert_query = """
            INSERT INTO {} ({})
            VALUES ({})
            ON CONFLICT DO NOTHING;
        """.format(
            table_name,
            ', '.join(columns),
            ', '.join(['%s'] * len(columns))
        )
        # Executing query with the given values
        for _, row in data.iterrows():
            values = tuple(row[col] for col in columns)
            if table_name == 'person':
                values = hash_password_in_person(values, columns)
            cursor.execute(insert_query, convert_types(values))

# Function to get SERIAL columns
def get_serial_columns(table_name, cursor):
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = %s AND column_default LIKE 'nextval%%'
    """, (table_name,))
    return [row[0] for row in cursor.fetchall()]

# Function to convert numpy types to native Python types
def convert_types(values):
    return tuple(int(val) if isinstance(val, (np.integer, np.int64)) else
                 float(val) if isinstance(val, (np.floating, np.float64)) else
                 val for val in values)
    
# Function to hash the password in the 'person' table data
def hash_password_in_person(values, columns):
    if 'password' in columns:
        password_index = columns.index('password')
        password = str(values[password_index])
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        values = list(values)
        values[password_index] = hashed_password.decode('utf-8')
    return tuple(values)
    
# DEBUG FUNCTION -- Function to select and display all rows from a table
def select_all_from_table(table_name, cursor):
    cursor.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name)))
    rows = cursor.fetchall()
    for row in rows:
        print(row)

# Connecting to the DataBase
db = db_connect()
cursor = db.cursor()

# Reading XML file with pandas DataFrames
xml_data = pd.read_xml('data.xml')

# Dictionary mapping table names to their corresponding DataFrame
tables = {
    'person': pd.read_xml('data.xml', xpath='.//person/row'),
    'patient': pd.read_xml('data.xml', xpath='.//patient/row'),
    'employee': pd.read_xml('data.xml', xpath='.//employee/row'),
    'nurse': pd.read_xml('data.xml', xpath='.//nurse/row'),
    'doctor': pd.read_xml('data.xml', xpath='.//doctor/row'),
    'assistant': pd.read_xml('data.xml', xpath='.//assistant/row'),
    'contract': pd.read_xml('data.xml', xpath='.//contract/row'),
    'specialization': pd.read_xml('data.xml', xpath='.//specialization/row'),
    'sup_specialization': pd.read_xml('data.xml', xpath='.//sup_specialization/row'),
    'sup_nurse': pd.read_xml('data.xml', xpath='.//sup_nurse/row'),
    'registration': pd.read_xml('data.xml', xpath='.//registration/row'),
    'equip': pd.read_xml('data.xml', xpath='.//equip/row'),
    'appointment': pd.read_xml('data.xml', xpath='.//appointment/row'),
    'hospitalization': pd.read_xml('data.xml', xpath='.//hospitalization/row'),
    'surgerytype': pd.read_xml('data.xml', xpath='.//surgerytype/row'),
    'surgery': pd.read_xml('data.xml', xpath='.//surgery/row'),
    'payment': pd.read_xml('data.xml', xpath='.//payment/row'),
    'nurse_equip': pd.read_xml('data.xml', xpath='.//nurse_equip/row'),
    'prescription': pd.read_xml('data.xml', xpath='.//prescription/row'),
    'medicine': pd.read_xml('data.xml', xpath='.//medicine/row'),
    'sideefect': pd.read_xml('data.xml', xpath='.//sideefect/row'),
    'medicine_prescription': pd.read_xml('data.xml', xpath='.//medicine_prescription/row'),
    'appointment_prescription': pd.read_xml('data.xml', xpath='.//appointment_prescription/row'),
    'hospitalization_prescription': pd.read_xml('data.xml', xpath='.//hospitalization_prescription/row')
}

# Inserting data into each table
for table_name, df in tables.items():
    if not df.empty:
        columns = df.columns.tolist()
        # Debug line
        # print(f"Inserting data into {table_name} with columns {columns}")
        insert_data(table_name, columns, df, cursor)

# Commiting and closing the connection
db.commit()
cursor.close()
db.close()

