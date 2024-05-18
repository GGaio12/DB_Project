from DB_Connection import db_connect
from psycopg2 import sql
import pandas as pd

# Helper function to insert data
def insert_data(table_name, columns, data):
    insert_query = sql.SQL("""
        INSERT INTO {table} ({fields})
        VALUES ({values})
        ON CONFLICT DO NOTHING;
    """).format(
        table=sql.Identifier(table_name),
        fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
        values=sql.SQL(', ').join(sql.Placeholder() * len(columns))
    )
    for _, row in data.iterrows():
        cursor.execute(insert_query, list(row))

# Connect to PostgreSQL
db = db_connect()
cursor = db.cursor()

# Read XML file into pandas DataFrame
xml_data = pd.read_xml('data.xml', xpath='.//row')

# Dictionary mapping table names to their corresponding DataFrame
tables = {
    'person': xml_data[xml_data['type'] == 'person'],
    'patients': xml_data[xml_data['type'] == 'patients'],
    'nurse': xml_data[xml_data['type'] == 'nurse'],
    'doctor': xml_data[xml_data['type'] == 'doctor'],
    'assistents': xml_data[xml_data['type'] == 'assistents'],
    'employee': xml_data[xml_data['type'] == 'employee'],
    'hospitalization': xml_data[xml_data['type'] == 'hospitalization'],
    'surgery': xml_data[xml_data['type'] == 'surgery'],
    'appointment': xml_data[xml_data['type'] == 'appointment'],
    'equip': xml_data[xml_data['type'] == 'equip'],
    'registation': xml_data[xml_data['type'] == 'registation'],
    'prescription': xml_data[xml_data['type'] == 'prescription'],
    'medicine': xml_data[xml_data['type'] == 'medicine'],
    'sideefect': xml_data[xml_data['type'] == 'sideefect'],
    'payment': xml_data[xml_data['type'] == 'payment'],
    'specialization': xml_data[xml_data['type'] == 'specialization'],
    'contract': xml_data[xml_data['type'] == 'contract'],
    'surgerytypes': xml_data[xml_data['type'] == 'surgerytypes'],
    'sup_specializations': xml_data[xml_data['type'] == 'sup_specializations'],
    'medicine_prescription': xml_data[xml_data['type'] == 'medicine_prescription'],
    'appointment_prescription': xml_data[xml_data['type'] == 'appointment_prescription'],
    'hospitalization_prescription': xml_data[xml_data['type'] == 'hospitalization_prescription'],
    'nurse_equip': xml_data[xml_data['type'] == 'nurse_equip'],
    'sup_nurses': xml_data[xml_data['type'] == 'sup_nurses']
}

# Insert data into each table
for table_name, df in tables.items():
    if not df.empty:
        columns = df.columns.tolist()
        insert_data(table_name, columns, df)

# Commit and close the connection
db.commit()
cursor.close()
db.close()

