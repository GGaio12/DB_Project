from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import Flask, request, jsonify
from DB_Connection import db_connect
from flask_bcrypt import Bcrypt
from datetime import datetime
from functools import wraps
import psycopg2
import logging
import os

app = Flask(__name__)

# Configuring JWT secret key
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'password')
jwt = JWTManager(app)

# Initialize Bcrypt
bcrypt = Bcrypt(app)

StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}

# Custom decorator for role-based access control.
def roles_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            identity = get_jwt_identity()
            if identity['role'] not in roles:
                return jsonify({'status': StatusCodes['api_error'], 'results': 'Your role cant access this functionality'})
            return fn(*args, **kwargs)
        return decorator
    return wrapper

# Help function to confirm data is in date like format.
def is_valid_date(date_string):
    try:
        # Try to parse the string with the given format
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        # If parsing fails, it's not a valid date
        return False

# Help function to confirm data is in timestamp date like format.
def is_valid_timestamp_date(timestamp_date_string):
    try:
        # Try to parse the string with the given format
        datetime.strptime(timestamp_date_string, '%Y-%m-%d %H:%M:%S')
        return True
    except ValueError:
        # If parsing fails, it's not a valid date
        return False


##########################################################
#                        ENDPOINTS                       #
##########################################################

##
## Landing Page of the Project.
##
@app.route('/')
def landing_page():
    return """
    Faculdade de Ciencias e Tecnologias da Universidade de Coimbra - FCTUC <br/>
    Departamento de Engenharia Informática - DEI <br/>
    <br/>
    Data Bases Project  <br/>
    Hospital Management System <br/>
    <br/>
    Gonçalo José Carrajola Gaio  Nº: 2022224905 <br/>
    João Ricardo Teixeira Gaspar Madeira  Nº: 2022200648 <br/>
    Rodrigo Carvalho dos Santos  Nº: 2022218283 <br/>
    <br/>
    Coimbra 2024 <br/>
    """
    
##
## Creates a new individual of type <type> inserting the data:
## Patient:   'cc', 'name', 'birthdate', 'email', 'password'
## Nuser:     'cc', 'name', 'birthdate', 'email', 'password', 'start_date', 'end_date', 'sal', 'work_hours'
## Assistant: 'cc', 'name', 'birthdate', 'email', 'password', 'start_date', 'end_date', 'sal', 'work_hours'
## Doctor:    'cc', 'name', 'birthdate', 'email', 'password', 'start_date', 'end_date', 'sal', 'work_hours', 'medical_license', 'spec_name'
## NOTE 
##      Dates have to be in YYYY-MM-DD format.
##      'name', 'birthdate', 'email', 'password', 'start_date', 'end_date', 'medical_license', 'spec_name' --> strings
##      'cc', 'sal', 'work_hours' --> integers
##
@app.route('/dbproj/register/<type>', methods=['POST'])
def insert_type(type):
    logger.info('POST /dbproj/register/<type>')
    logger.debug(f'type: {type}')
    
    # Getting json payload
    payload = request.get_json()
    
    logger.debug(f'POST /dbproj/register/<type> - payload: {payload}')
    
    # Fields that have to be in payload
    required_fields = ['cc', 'name', 'birthdate', 'email', 'password'] # Commun fields
    employee_fields = ['start_date', 'end_date', 'sal', 'work_hours']  # Only employee fields
    doctor_fields = ['medical_license', 'spec_name']                   # Only doctor fields

    # Verifying commun fields
    for field in required_fields:
        if(field not in payload):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} not in payload'})
        if(field == 'cc' and not isinstance(payload[field], int)):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} should be an integer'})
        if(field != 'cc' and not isinstance(payload[field], str)):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} should be a string'})
    
    is_employee = False
    if(type in ['nurse', 'doctor', 'assistant']):
        is_employee = True
        # Verifying only employee fields
        for field in employee_fields:
            if(field not in payload):
                return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} not in payload'})
            if(field in ['sal', 'work_hours']):
                if(not isinstance(payload[field], int)):
                    return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} should be an integer'})
            if(field in ['start_date', 'end_date']):
                if(not isinstance(payload[field], str) or not is_valid_date(payload[field])):
                    return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} should be a valid date string in YYYY-MM-DD format'})

        if(type == 'doctor'):
            # Verifying only doctor fields
            for field in doctor_fields:
                if(field not in payload or not isinstance(payload[field], str)):
                    return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} should be a string'})
    
    # Initializing commun fields values (hashing password)
    cc = payload['cc']
    name = payload['name']
    birthdate = payload['birthdate']
    email = payload['email']
    password = bcrypt.generate_password_hash(payload['password']).decode('utf-8')
    
    # Constructing all queries 'table_name', 'columns', 'values_placeholders' and 'values' and placing them in a list by order of execution 
    queries = [('person', '(cc, name, birthdate, email, password)', '%s, %s, %s, %s, %s', (cc, name, birthdate, email, password))]
    if(is_employee):
        # Adding employee-related queries
        queries.append(('employee', '(person_cc)', '%s', (cc,)))
        
        if(type == 'doctor'):
            # Adding doctor-specific queries
            queries.append((type, '(employee_person_cc, medical_license)', '%s, %s', (cc, payload['medical_license'])))
            queries.append(('specialization', '(name, doctor_employee_person_cc)', '%s, %s', (payload['spec_name'], cc)))
        else:
            # Adding other employee type queries (nurse, assistant)
            queries.append((type, '(employee_person_cc)', '%s', (cc,)))
        
        # Adding contract-related query
        queries.append(('contract', '(start_date, end_date, sal, work_hours, employee_person_cc)', '%s, %s, %s, %s, %s',
                        (payload['start_date'], payload['end_date'], payload['sal'], payload['work_hours'], cc)))
    else:
        # Adding patient-related query
        queries.append((type, '(person_cc)', '%s', (cc,)))
    
    # Connecting to Data Base
    db = db_connect()
    cursor = db.cursor()
    
    # Executing all queries
    try:
        cursor.execute("BEGIN")
        
        for table, columns, values_placeholders, values in queries:
            query = f'''
                    INSERT INTO {table} {columns}
                    VALUES ({values_placeholders})
                    ON CONFLICT DO NOTHING;
                    '''
            cursor.execute(query, values)

        db.commit()
        
        response = {'status': StatusCodes['success'], 'results': {'personal_id': cc}}

    except(Exception, psycopg2.DatabaseError) as error:
        logging.error(f'POST /dbproj/register/<type> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        if(db is not None):
            db.rollback()

    finally:
        if(db is not None):
            db.close()

    return jsonify(response)
    
##
## User Authentication. Providing name and password,
## user can authenticate and receive an authentication token.
## NOTE Name and password need to be strings.
##
@app.route('/dbproj/user', methods=['PUT'])
def authenticate_user():
    logger.info('PUT /dbproj/user')
    
    # Getting json payload
    payload = request.get_json()
    
    logger.debug(f'PUT /dbproj/user - payload: {payload}')
    
    auth_fields = ['name', 'password']
    
    # Verifying if all authentication fields are in payload
    for field in auth_fields:
        if(field not in payload):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} not or incorrect type in payload'})
        if(not isinstance(payload[field], str)):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} should be a string'})
    
    # Getting name and password
    name = payload['name']
    password = payload['password']
    
    # Constructing the query statement to execute
    statement_temp = '''
                     SELECT password, cc
                     FROM {role}
                     JOIN person ON {role}.{cc_type} = person.cc
                     WHERE person.name = %s;
                     '''

    # Connecting to Data Base
    db = db_connect()
    cursor = db.cursor()

    try:
        for i in range(4):
            # Determinig query values
            if(i == 0):
                role = 'patient'
                cc_type = 'person_cc'
            else:
                cc_type = 'employee_person_cc'
                if(i == 1):
                    role = 'nurse'
                elif(i == 2):
                    role = 'doctor'
                else:
                    role = 'assistant'
            
            statement = statement_temp.format(role=role, cc_type=cc_type)
            
            # Executing query
            cursor.execute(statement, (name,))
            result = cursor.fetchone()

            # Verifying result and password
            if(result and bcrypt.check_password_hash(result[0], password)):
                access_token = create_access_token(identity={'id': result[1], 'role': role})
                response = {'status': StatusCodes['success'], 'results': {'access_token': access_token}}
                break
            elif(i == 3):
                response = {'status': StatusCodes['api_error'], 'results': 'Incorrect name/passord'}
                
    except(Exception, psycopg2.DatabaseError) as error:
        logger.error(f'PUT /dbproj/user - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if(db is not None):
            db.close()

    return jsonify(response)

## the data:  --> TODOO!!!
##
## MADEIRA
@app.route('/dbproj/appointment', methods=['POST'])
@jwt_required()
@roles_required('patient')
def schedule_appointment():
    logger.info('POST /dbproj/appointment')
    
    # Getting json payload
    payload = request.get_json()
    logger.debug(f'POST /dbproj/appointment - payload: {payload}')
    
    # Required fields for scheduling an appointment
    required_fields = ['appointment_date', 'bill', 'bill_payed', 'assistant_id', 'doctor_id', 'nurse_id']
    
    # Verifying required fields in payload
    for field in required_fields:
        if field not in payload:
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} not in payload'})

    appointment_date = payload['appointment_date']
    bill = payload['bill']
    bill_payed = payload['bill_payed']
    assistant_id = payload['assistant_id']
    doctor_id = payload['doctor_id']
    nurse_id = payload['nurse_id']
    
    # Ensure bill is a positive number
    if bill < 0:
        return jsonify({'status': StatusCodes['api_error'], 'results': 'Bill amount must be greater or equals to zero'})
    
    # Get patient identity
    identity = get_jwt_identity()

    # Queries to insert into equip and nurse_equip tables
    equip_query = '''
                  INSERT INTO equip (doctor_employee_person_cc)
                  VALUES (%s)
                  RETURNING equip_id
                  '''
    nurse_equip_query = '''
                        INSERT INTO nurse_equip (nurse_employee_person_cc, equip_equip_id)
                        VALUES (%s, %s)
                        '''
    
    # Insert into registration table
    registration_query = '''
                         INSERT INTO registration (bill, bill_payed, assistant_employee_person_cc, patient_person_cc)
                         VALUES (%s, %s, %s, %s)
                         RETURNING registration_id
                         '''
    registration_values = (bill, bill_payed, assistant_id, identity['id'])
    
    # Insert into appointment table
    appointment_query = '''
                        INSERT INTO appointment (appoint_date, registration_registration_id)
                        VALUES (%s, %s)
                        RETURNING appoint_id
                        '''
    
    # Connecting to Data Base
    db = db_connect()
    cursor = db.cursor()

    try:
        cursor.execute("BEGIN")
        
        # Insert into equip table and get equip_id
        cursor.execute(equip_query, (doctor_id,))
        equip_id = cursor.fetchone()[0]
        
        # Insert into nurse_equip table
        cursor.execute(nurse_equip_query, (nurse_id, equip_id))
        
        # Insert into registration table and get registration_id
        cursor.execute(registration_query, registration_values)
        registration_id = cursor.fetchone()[0]
        
        # Insert into appointment table
        appointment_values = (appointment_date, registration_id)
        cursor.execute(appointment_query, appointment_values)
        appointment_id = cursor.fetchone()[0]

        db.commit()
        
        response = {'status': StatusCodes['success'], 'results': {'appointment_id': appointment_id}}
        
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /dbproj/appointment - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        if(db is not None):
            db.rollback()
    
    finally:
        if(db is not None):
            db.close()
    
    return jsonify(response)

    
##
## Get appointments information. Lists all appointments and
## their detailed info by giving the patient_user_id in url.
##
@app.route('/dbproj/appointments/<patient_user_id>', methods=['GET'])
@jwt_required()
@roles_required('assistant')
def get_patient_appointments(patient_user_id):
    logger.info('GET /dbproj/appointments/<patient_user_id>')
    logger.debug(f'patient_user_id: {patient_user_id}')
    
    statement = '''
                SELECT appoint_id AS id, cost, appoint_date AS date, doctor_employee_person_cc AS doctor_id
                FROM appointment AS ap
                JOIN equip ON ap.equip_equip_id = equip.equip_id
                JOIN registration AS reg ON ap.registration_registration_id = reg.registration_id
                WHERE reg.patient_person_cc = %s;            
                '''
    
    # Connecting to Data Base
    db = db_connect()
    cursor = db.cursor()
    
    try:
        cursor.execute(statement, (patient_user_id,))
        result = cursor.fetchall()
        
        if(result):
            # Convert the result to a list of dictionaries
            appointments = []
            for row in result:
                appointments.append({
                    'id': row[0],
                    'cost': row[1],
                    'date': row[2],
                    'doctor_id': row[3]
                })
            response = {'status': StatusCodes['success'], 'results': {'appointments': appointments}}
        else:
            response = {'status': StatusCodes['api_error'], 'results': 'Patient does not exist or do not have any appointments registered'}

    except(Exception, psycopg2.DatabaseError) as error:
        logging.error(f'GET /dbproj/appointments/<patient_user_id> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if(db is not None):
            db.close()

    return jsonify(response)
    
##
## Schedule a new surgery for a patient that isn't hospitalized yet inserting the data:
## 'patient_id', 'hosp_cost', 'hosp_date', 'hosp_room_num', 'hosp_nurse_id', 'sur_cost', 'operating_room', 'surgery_type_id', 'doctor_id', 'surgery_date', 'nurses'
## NOTE 
##      'surgery_date' have to be in YYYY-MM-DD format.
##      'hosp_date' have to be in 'YYYY-MM-DD HH:MM:SS' format.
##      'hosp_date', 'operating_room', 'surgery_date' --> strings
##      'patient_id', 'hosp_room_num', 'hosp_nurse_id', 'surgery_type_id', 'doctor_id' --> integers
##      'hosp_cost', 'sur_cost' --> integers or floats
##      'nurses' --> list of integers
##
@app.route('/dbproj/surgery', methods=['POST'])
@jwt_required()
@roles_required('assistant')
def schedule_new_surgery_nh():
    logger.info('POST /dbproj/surgery')
    
    # Get JSON payload
    payload = request.get_json()
    logger.debug(f'POST /dbproj/surgery - payload: {payload}')

    # Required fields for scheduling a surgery
    required_fields = ['patient_id', 'hosp_cost', 'hosp_date', 'hosp_room_num', 'hosp_nurse_id', 'sur_cost', 'operating_room', 'surgery_type_id', 'doctor_id', 'surgery_date', 'nurses']

    # Verifying required fields in payload
    for field in required_fields:
        if(field not in payload):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} not in payload'})
        if(field == 'operating_room' and not isinstance(payload[field], str)):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} should be a string'})
        if(field in ['patient_id', 'hosp_room_num', 'hosp_nurse_id', 'surgery_type_id', 'doctor_id'] and not isinstance(payload[field], int)):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} should be an integer'})
        if(field == 'hosp_date' and (not isinstance(payload[field], str) or not is_valid_timestamp_date(payload[field]))):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} should be a valid timestamp date string in "YYYY-MM-DD HH:MM:SS" format'})
        if(field in ['hosp_cost', 'sur_cost'] and (not isinstance(payload[field], float) and not isinstance(payload[field], int))):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} should be an integer or float'})
        if(field == 'surgery_date' and (not isinstance(payload[field], str) or not is_valid_date(payload[field]))):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} should be a valid date string in YYYY-MM-DD format'})
        if(field == 'nurses' and not isinstance(payload[field], list)):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} should be a list of nurses ids'})
        
    # Verifying all nurses ids
    for i, (id) in enumerate(payload['nurses']):
        if(not isinstance(id, int)):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'id N:{i} of nurses ids should be an integer'})
            
    # Extract data from payload
    patient_id = payload['patient_id']
    surgery_date = payload['surgery_date']
    operating_room = payload['operating_room']
    hosp_cost = payload['hosp_cost']
    hosp_date = payload['hosp_date']
    hosp_room_num = payload['hosp_room_num']
    hosp_nurse_id = payload['hosp_nurse_id']
    sur_cost = payload['sur_cost']
    surgery_type_id = payload['surgery_type_id']
    doctor_id = payload['doctor_id']
    nurses = payload['nurses']

    # Get assistant identity
    identity = get_jwt_identity()

    registration_id = hospitalization_id = surgery_id = equip_id = 0
    queries = [
                ['equip', '(doctor_employee_person_cc)', '(%s)', (doctor_id,), 'equip_id'],
                ['registration', '(assistant_employee_person_cc, patient_person_cc)', '(%s, %s)', [identity['id'], patient_id], 'registration_id'],
                ['hospitalization', '(cost, date, room_num, nurse_employee_person_cc, registration_registration_id)', '(%s, %s, %s, %s, %s)', [hosp_cost, hosp_date, hosp_room_num, hosp_nurse_id, registration_id], 'registration_registration_id'],
                ['surgery', '(cost, date, operating_room, surgerytype_sur_type_id, equip_equip_id, hospitalization_registration_registration_id)', '(%s, %s, %s, %s, %s, %s)', [sur_cost, surgery_date, operating_room, surgery_type_id, equip_id, hospitalization_id], 'sur_id']
              ]

    for nurse_id in nurses:
        queries.append(['nurse_equip', '(nurse_employee_person_cc, equip_equip_id)', '(%s, %s)', [nurse_id, equip_id], None])

    # Connect to database
    db = db_connect()
    cursor = db.cursor()

    try:
        cursor.execute("BEGIN")
        
        for i, (table, columns, values_placeholders, values, returns) in enumerate(queries):
            if(returns == None): 
                statement = f'''
                             INSERT INTO {table} {columns}
                             VALUES {values_placeholders};
                             '''
            else:
                statement = f'''
                             INSERT INTO {table} {columns}
                             VALUES {values_placeholders}
                             RETURNING {returns};
                             '''
            cursor.execute(statement, tuple(values))
            if(i == 0):
                equip_id = cursor.fetchone()[0]
                queries[3][3][4] = equip_id
                for j, nurse_id in enumerate(nurses):
                    queries[4+j][3] = [nurse_id, equip_id]
            elif(i == 1):
                queries[2][3][4] = cursor.fetchone()[0]
            elif(i == 2):
                queries[3][3][5] = cursor.fetchone()[0]
            elif(i == 3):
                surgery_id = cursor.fetchone()[0]

        db.commit()
        
        response = {'status': StatusCodes['success'], 'results': {'surgery_id': surgery_id}}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /dbproj/surgery - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        if(db is not None):
            db.rollback()

    finally:
        if(db is not None):
            db.close()

    return jsonify(response)

## 
## Schedule a new surgery for a patient that is already hospitalized inserting the data:
## 'sur_cost', 'operating_room', 'surgery_type_id', 'doctor_id', 'surgery_date', 'nurses'
## NOTE 
##      'surgery_date' have to be in YYYY-MM-DD format.
##      'operating_room', 'surgery_date' --> strings
##      'surgery_type_id', 'doctor_id' --> integers
##      'sur_cost' --> integers or floats
##      'nurses' --> list of integers
##
@app.route('/dbproj/surgery/<hospitalization_id>', methods=['POST'])
@jwt_required()
@roles_required('assistant')
def schedule_new_surgery_h(hospitalization_id):
    logger.info(f'POST /dbproj/surgery/<hospitalization_id>')
    logger.debug(f'POST /dbproj/surgery/<hospitalization_id> - hospitalization_id: {hospitalization_id}')
    
    # Get JSON payload
    payload = request.get_json()
    logger.debug(f'POST /dbproj/surgery/<hospitalization_id> - payload: {payload}')

    # Required fields for scheduling a surgery
    required_fields = ['sur_cost', 'operating_room', 'surgery_type_id', 'doctor_id', 'surgery_date', 'nurses']

    # Verify required fields in payload
    for field in required_fields:
        if(field not in payload):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} not in payload'})
        if(field == 'operating_room' and not isinstance(payload[field], str)):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} should be a string'})
        if(field in ['surgery_type_id', 'doctor_id'] and not isinstance(payload[field], int)):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} should be an integer'})
        if(field == 'sur_cost' and (not isinstance(payload[field], float) and not isinstance(payload[field], int))):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} should be an integer or float'})
        if(field == 'surgery_date' and (not isinstance(payload[field], str) or not is_valid_date(payload[field]))):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} should be a valid date string in YYYY-MM-DD format'})
        if(field == 'nurses' and not isinstance(payload[field], list)):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} should be a list of nurses ids'})
    
    # Verifying all nurses ids
    for i, (id) in enumerate(payload['nurses']):
        if(not isinstance(id, int)):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'id N:{i} of nurses ids should be an integer'})
    
    # Extract data from payload
    surgery_date = payload['surgery_date']
    operating_room = payload['operating_room']
    sur_cost = payload['sur_cost']
    surgery_type_id = payload['surgery_type_id']
    doctor_id = payload['doctor_id']
    nurses = payload['nurses']
    
    check_hosp_reg = '''
                     SELECT *
                     FROM hospitalization
                     WHERE registration_registration_id = %s
                     '''
    
    equip_id = 0
    queries = [
                ['equip', '(doctor_employee_person_cc)', '(%s)', (doctor_id,), 'equip_id'],
                ['surgery', '(cost, date, operating_room, surgerytype_sur_type_id, equip_equip_id, hospitalization_registration_registration_id)', '(%s, %s, %s, %s, %s, %s)', [sur_cost, surgery_date, operating_room, surgery_type_id, equip_id, hospitalization_id], 'sur_id']
              ]

    for nurse_id in nurses:
        queries.append(['nurse_equip', '(nurse_employee_person_cc, equip_equip_id)', '(%s, %s)', [nurse_id, equip_id], None])

    # Connect to database
    db = db_connect()
    cursor = db.cursor()

    try:
        cursor.execute("BEGIN")
        
        # Check if hospitalization exists
        cursor.execute(check_hosp_reg, (hospitalization_id,))
        if cursor.fetchone() is None:
            return jsonify({'status': StatusCodes['api_error'], 'results': 'Invalid hospitalization_id'})
        
        for i, (table, columns, values_placeholders, values, returns) in enumerate(queries):
            if(returns == None): 
                statement = f'''
                             INSERT INTO {table} {columns}
                             VALUES {values_placeholders};
                             '''
            else:
                statement = f'''
                             INSERT INTO {table} {columns}
                             VALUES {values_placeholders}
                             RETURNING {returns};
                             '''
            cursor.execute(statement, tuple(values))
            if(i == 0):
                equip_id = cursor.fetchone()[0]
                queries[1][3][4] = equip_id
                for j, nurse_id in enumerate(nurses):
                    queries[2+j][3] = [nurse_id, equip_id]
            elif(i == 1):
                surgery_id = cursor.fetchone()[0]

        db.commit()
        
        response = {'status': StatusCodes['success'], 'results': {'surgery_id': surgery_id}}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /dbproj/surgery/{hospitalization_id} - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        if(db is not None):
            db.rollback()

    finally:
        if(db is not None):
            db.close()

    return jsonify(response)

##
## Get the list of prescriptions and details of it for a specific patient
##
@app.route('/dbproj/prescriptions/<person_id>', methods=['GET'])
@jwt_required()
def get_patient_prescriptions(person_id):
    logger.info('GET /dbproj/prescriptions/<person_id>')
    logger.debug(f'person_id: {person_id}')
    
    # Verifying if the connected person is a patient and if true veryfing if id match the person_id in URL
    identity = get_jwt_identity()
    logger.debug(f'identity: {identity}')
    if(identity['role'] == 'patient' and identity['id'] != person_id):
        return jsonify({'status': StatusCodes['api_error'], 'results': 'Your id does not matchs the URL id provided'})
    
    statement = '''
                SELECT prescription_id AS "id", validity, med_name AS "medicine name", dosage, frequency
                FROM prescription AS pres
                JOIN medicine_prescription AS med_pres ON pres.prescription_id = med_pres.prescription_prescription_id
                JOIN medicine AS med ON med_pres.medicine_medicine_id = med.medicine_id
                JOIN hospitalization_prescription AS hosp_pres ON pres.prescription_id = hosp_pres.prescription_prescription_id
                JOIN hospitalization AS hosp ON hosp_pres.hospitalization_registration_registration_id = hosp.registration_registration_id
                JOIN registration AS reg ON hosp.registration_registration_id = reg.registration_id
                WHERE reg.patient_person_cc = %(person_id)s

                UNION

                SELECT prescription_id AS "id", validity, med_name AS "medicine name", dosage, frequency
                FROM prescription AS pres
                JOIN medicine_prescription AS med_pres ON pres.prescription_id = med_pres.prescription_prescription_id
                JOIN medicine AS med ON med_pres.medicine_medicine_id = med.medicine_id
                JOIN appointment_prescription AS ap_pres ON pres.prescription_id = ap_pres.prescription_prescription_id
                JOIN appointment AS ap ON ap_pres.appointment_registration_registration_id = ap.registration_registration_id
                JOIN registration AS reg ON ap.registration_registration_id = reg.registration_id
                WHERE reg.patient_person_cc = %(person_id)s;
                '''
    params = {'person_id': person_id}
    
    # Connecting to Data Base
    db = db_connect()
    cursor = db.cursor()
    
    try:
        cursor.execute(statement, params)
        result = cursor.fetchall()
        
        if(result):
            # Convert the result to a list of dictionaries
            prescriptions = []
            presc_id = 0
            for row in result:
                if(presc_id != row[0]):
                    if(presc_id != 0):
                        prescriptions.append({
                            'id': presc_id,
                            'validity': row[1],
                            'posology': medicines
                        })
                    presc_id = row[0]
                    medicines = []
                medicines.append({
                    'medicine name': row[2],
                    'dosage': row[3],
                    'frequency': row[4]
                })
            
            prescriptions.append({
                'id': presc_id,
                'validity': row[1],
                'posology': medicines
            })

            response = {'status': StatusCodes['success'], 'results': {'prescriptions': prescriptions}}
        else:
            response = {'status': StatusCodes['api_error'], 'results': 'Patient does not exist or do not have any appointments registered'}

    except(Exception, psycopg2.DatabaseError) as error:
        logging.error(f'GET /dbproj/prescriptions/<person_id> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if(db is not None):
            db.close()

    return jsonify(response)

##
## Adds a new prescription inserting the data:
## 'type', 'event_id', 'validity', 'medicines'
## 'medicines' is a list of medicines each containing: 'medicine_name', 'dosage', 'frequency'
## NOTE 
##      'validity' have to be in YYYY-MM-DD format.
##      'type', 'validity', 'medicine_name', 'dosage', 'frequency' --> strings
##      'event_id' --> integers
##      'medicines' --> list
##
@app.route('/dbproj/prescription/', methods=['POST'])
@jwt_required()
@roles_required('doctor')
def add_prescription():
    logger.info('POST /dbproj/prescription/')
    
    # Getting json payload
    payload = request.get_json()
    
    logger.debug(f'POST /dbproj/prescription/ - payload: {payload}')
    
    general_fields = ['type', 'event_id', 'validity', 'medicines']
    med_fields = ['medicine_name', 'dosage', 'frequency']
    
    # Verifying general fields
    for field in general_fields:
        if(field not in payload):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} not in payload'})
        if(field == 'type'):
            if(not isinstance(payload[field], str)):
                return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} should be a string'})
            if(payload[field] == 'appointment'):
                type_id = 'appoint_id'
            elif(payload[field] == 'hospitalization'):
                type_id = 'hosp_id'
            else:
                return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} in payload not regonized. Should be "appointment" or "hospitalization"'})
        if(field == 'event_id' and not isinstance(payload[field], int)):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} should be an integer'})
        if(field == 'validity' and (not isinstance(payload[field], str) or not is_valid_date(payload[field]))):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} should be a valid date string in YYYY-MM-DD format'})
        if(field == 'medicines' and not isinstance(payload[field], list)):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} should be a list'})
        
    # Verifying medicines fields
    for i, medicine in enumerate(payload['medicines'], start=1):
        for field in med_fields:
            if(field not in medicine):
                return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} not in medicine N:{i} payload'})
            if(not isinstance(medicine[field], str)):
                return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} in medicine N:{i} should be a string'})

    # SQL Statements
    # Note: Because type_id and payload['type'] are created in code or already verifyed, it doesn't represent a scurity issue
    statements = {
        'max_prescription_id': 'SELECT MAX(prescription_id) FROM prescription;',
        'max_medicine_id': 'SELECT MAX(medicine_id) FROM medicine;',
        'max_event_type_id': f'SELECT MAX({type_id}) FROM {payload['type']};',
        'get_reg_id': '''
                      SELECT registration_id 
                      FROM registration 
                      JOIN {type} ON registration_id = registration_registration_id
                      WHERE {type_id} = %s
                      '''.format(type=payload['type'], type_id=type_id)
    }
    
    queries = [('prescription', '(validity)', '%s', [payload['validity']])]
    
    # Connecting to Data Base
    db = db_connect()
    cursor = db.cursor()
    saved = False
    
    try:
        cursor.execute("BEGIN")
        cursor.execute("SAVEPOINT no_db_modifications")
        
        # Check if event_id exists
        cursor.execute(statements['max_event_type_id'])
        max_event_type_id = cursor.fetchone()[0]
        if payload['event_id'] > int(max_event_type_id):
            return jsonify({'status': StatusCodes['api_error'], 'results': 'Event id does not exist'})

        # Getting registration id of the event
        cursor.execute(statements['get_reg_id'], str(payload['event_id']))
        reg_id = cursor.fetchone()[0]
        
        # Getting new prescription_id
        cursor.execute(statements['max_prescription_id'])
        pres_id = cursor.fetchone()[0] + 1

        # Getting new medicine_id starting point
        cursor.execute(statements['max_medicine_id'])
        med_id = cursor.fetchone()[0]
        
        for medicine in payload['medicines']:
            med_id += 1
            queries.extend([
                            ('medicine', '(med_name, dosage, frequency)', '%s, %s, %s', [medicine['medicine_name'], medicine['dosage'], medicine['frequency']]),
                            ('medicine_prescription', '(medicine_medicine_id, prescription_prescription_id)', '%s, %s', [med_id, pres_id])
                          ])
        if(payload['type'] == 'appointment'):
            queries.append(('appointment_prescription', '(appointment_registration_registration_id, prescription_prescription_id)', '%s, %s', [reg_id, pres_id]))
        else:
            queries.append(('hospitalization_prescription', '(hospitalization_registration_registration_id, prescription_prescription_id)', '%s, %s', [payload['event_id'], pres_id]))
    
        # Executting all queries to insert elements in tables
        for table, columns, values_placeholders, values in queries:
            statement = f'''
                        INSERT INTO {table} {columns}
                        VALUES ({values_placeholders})
                        ON CONFLICT DO NOTHING;
                        '''
            cursor.execute(statement, values)
            if(table == 'medicine'):
                db.commit()
                saved = True
                cursor.execute("BEGIN")
        
        db.commit()
        response = {'status': StatusCodes['success'], 'results': {'prescription_id': pres_id}}

    except(Exception, psycopg2.DatabaseError) as error:
        logging.error(f'POST /dbproj/prescription/ - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        if(db is not None):
            db.rollback()
        if(saved):
            cursor.execute("ROLLBACK TO SAVEPOINT no_db_modifications")

    finally:
        if(db is not None):
            db.close()

    return jsonify(response)

##
## Execute a payment of an existing bill inserting the data:
##  --> TODOO!!!
##
@app.route('/dbproj/bills/<registration_id>', methods=['POST'])
@jwt_required()
@roles_required('patient')
def pay_bill(registration_id):
    logger.info(f'POST /dbproj/bills/{registration_id}')
    
    # Getting json payload
    payload = request.get_json()
    logger.debug(f'POST /dbproj/bills/{registration_id} - payload: {payload}')
    
    # Required fields for payment
    required_fields = ['amount', 'type']
    
    # Verifying required fields in payload
    for field in required_fields:
        if field not in payload:
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} not in payload'})

    amount = payload['amount']
    payment_type = payload['type']
    
    # Ensure amount is a positive number
    if amount <= 0:
        return jsonify({'status': StatusCodes['api_error'], 'results': 'Amount must be greater than zero'})
    
    # Connecting to Data Base
    db = db_connect()
    cursor = db.cursor()

    try:
        # SE EXISTE
        # SE PERTENCE AO RESPETIVO ID
        identity = get_jwt_identity()
        statement = '''
                    SELECT bill, bill_payed
                    FROM registration
                    WHERE registration_id = %s
                    AND patient_person_cc = %s
                    '''
        values = (registration_id, identity['id'])
        cursor.execute(statement, values)
        
        bill_info = cursor.fetchone()
        
        if not bill_info:
            return jsonify({'status': StatusCodes['api_error'], 'results': 'Bill not found or access denied'})
        
        bill_amount, bill_payed = bill_info
        
        if bill_payed:
            return jsonify({'status': StatusCodes['api_error'], 'results': 'Bill is already paid'})
        
        # VERIFCAR VALOR PAGO
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0)
            FROM payment
            WHERE registration_registration_id = %s
        """, (registration_id,))
        
        total_paid = cursor.fetchone()[0]
        if(total_paid + amount > bill_amount):
            return
        
        
        #PROCESSAR PAGAMENTO
        cursor.execute("""
            INSERT INTO payment (amount, type, registration_registration_id)
            VALUES (%s, %s, %s)
            RETURNING payment_id
        """, (amount, payment_type, registration_id))
        
        payment_id = cursor.fetchone()[0]
        
        # mUDAR bill_payed PARA TRUE
        if total_paid >= bill_amount:
            cursor.execute("""
                UPDATE registration
                SET bill_payed = TRUE
                WHERE registration_id = %s
            """, (registration_id,))
        
        db.commit()
        
        response = {'status': StatusCodes['success'], 'results': {'payment_id': payment_id, 'payed_ammount': amount}}
        
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /dbproj/bills/{registration_id} - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        if(db is not None):
            db.rollback()
    
    finally:
        if(db is not None):
            db.close()
    
    return jsonify(response)

##
## Lists top 3 patients considering the money spent in the month.
##
@app.route('/dbproj/top3', methods=['GET'])
@jwt_required()
@roles_required('assistant')
def get_top3_patients():
    logger.info('GET /dbproj/top3')

    # Current month and year
    now = datetime.now()
    
    # Query to get the top 3 patients by money spent in the current month and all their procedures informations
    top3_query = '''
                 WITH total_spent AS (
                     SELECT 
                         r.patient_person_cc,
                         p.name,
                         SUM(COALESCE(a.cost, 0) + COALESCE(h.cost, 0)) AS amount_spent
                     FROM registration r
                     JOIN person p ON r.patient_person_cc = p.cc
                     LEFT JOIN appointment a ON r.registration_id = a.registration_registration_id AND a.appoint_date >= date_trunc('month', current_date)
                     LEFT JOIN hospitalization h ON r.registration_id = h.registration_registration_id AND h.date >= date_trunc('month', current_date)
                     WHERE r.regist_date >= date_trunc('month', current_date)
                     GROUP BY r.patient_person_cc, p.name
                 ),
                 ranked_patients AS (
                     SELECT 
                         patient_person_cc,
                         name,
                         amount_spent,
                         ROW_NUMBER() OVER (ORDER BY amount_spent DESC) AS rank
                     FROM total_spent
                 )
                 SELECT 
                     rp.patient_person_cc AS patient_id,
                     rp.name,
                     rp.amount_spent,
                     a.appoint_date AS procedure_date,
                     'Appointment' AS procedure_type,
                     a.cost AS procedure_cost,
                     a.equip_equip_id AS procedure_equip_id
                 FROM ranked_patients rp
                 JOIN registration r ON rp.patient_person_cc = r.patient_person_cc
                 JOIN appointment a ON r.registration_id = a.registration_registration_id
                 WHERE rp.rank <= 3
                 AND a.appoint_date >= date_trunc('month', current_date)
                    
                 UNION ALL
                
                 SELECT 
                     rp.patient_person_cc AS patient_id,
                     rp.name,
                     rp.amount_spent,
                     h.date AS procedure_date,
                     'Hospitalization' AS procedure_type,
                     h.cost AS procedure_cost,
                     h.nurse_employee_person_cc AS procedure_nurse_id
                 FROM ranked_patients rp
                 JOIN registration r ON rp.patient_person_cc = r.patient_person_cc
                 JOIN hospitalization h ON r.registration_id = h.registration_registration_id
                 WHERE rp.rank <= 3
                 AND h.date >= date_trunc('month', current_date)
                 ORDER BY amount_spent DESC, name, procedure_date;
                 '''

    results = []
    current_patient = {}
    current_procedures = []
    current_id = None

    # Connecting to Data Base
    db = db_connect()
    cursor = db.cursor()
    
    try:
        cursor.execute(top3_query)
        top3_patients_infos = cursor.fetchall()
        
        for patient in top3_patients_infos:
            patient_id = patient[0]
            name = patient[1]
            total_spent = patient[2]
            procedure_date = patient[3]
            procedure_type = patient[4]
            procedure_cost = patient[5]
            procedure_equip_id = patient[6]

            # Check if is still processing the same patient
            if((current_id is None) or (patient_id != current_id)):
                # If it's a new patient and there's a current patient being processed, append it to results
                if(current_id is not None):
                    current_patient['procedures'] = current_procedures
                    results.append(current_patient)

                # Reset for the new patient
                current_patient = {
                    'patient_id': patient_id,
                    'name': name,
                    'total_spent': total_spent,
                    'procedures': []
                }
                current_procedures = []
                current_id = patient_id

            # Add the procedure to the current patient's procedures
            current_procedures.append({
                'type': procedure_type,
                'date': procedure_date,
                'cost': procedure_cost,
                'encar_equip': procedure_equip_id
            })

        # Add the last patient being processed
        if(current_id is not None):
            current_patient['procedures'] = current_procedures
            results.append(current_patient)
            
        response = {'status': StatusCodes['success'], 'results': results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /dbproj/top3 - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if(db is not None):
            db.close()

    return jsonify(response)

##
## Daily summary. Lists a count for all hospitalizations details of a day.
##
@app.route('/dbproj/daily/<year_month_day>', methods=['GET'])
@jwt_required()
@roles_required('assistant')
def list_daily_summary(year_month_day):
    logger.info('GET /dbproj/daily/<year_month_day>')
    logger.debug(f'GET /dbproj/daily/<year_month_day> - year_month_day: {year_month_day}')
    
    # Verifying the date inserted in URL
    if(not is_valid_date(year_month_day)):
        return jsonify({'status': StatusCodes['api_error'], 'results': f'Date in URL not correct. USE format: YYYY-MM-DD'})
    
    statement = '''
                SELECT
                    SUM(bill) AS "Total Registed Bill",
                    SUM(amount) AS "Total Ammount Payed",
                    COUNT(sur_id) AS "Total Agended Surgeries",
                    COUNT(prescription_prescription_id) AS "Total Prescriptions Writed"
                FROM hospitalization AS hos
                LEFT JOIN registration AS reg ON reg.registration_id = hos.registration_registration_id
                LEFT JOIN payment AS pay ON reg.registration_id = pay.registration_registration_id
                LEFT JOIN surgery AS sur ON reg.registration_id = sur.hospitalization_registration_registration_id
                LEFT JOIN hospitalization_prescription AS hosp_pres ON hos.registration_registration_id = hosp_pres.hospitalization_registration_registration_id
                WHERE DATE(reg.regist_date) = %s;
                '''
    
    # Connecting to Data Base
    db = db_connect()
    cursor = db.cursor()
    
    try:
        # Executing the query
        cursor.execute(statement, (year_month_day,))
        result = cursor.fetchall()
        
        if result:
            total_registered_bill = result[0][0] if result[0][0] is not None else 0
            total_amount_paid = result[0][1] if result[0][1] is not None else 0
            total_agended_surgeries = result[0][2] if result[0][2] is not None else 0
            total_prescriptions_writed = result[0][3] if result[0][3] is not None else 0
        else:
            total_registered_bill = total_amount_paid = total_agended_surgeries = total_prescriptions_writed = 0
        
        response = {'status': StatusCodes['success'], 'results': {
                    'Total Registed Bill': total_registered_bill,
                    'Total Ammount Payed': total_amount_paid,
                    'Total Agended Surgeries': total_agended_surgeries,
                    'Total Prescriptions Writed': total_prescriptions_writed
                  }}
        
    except(Exception, psycopg2.DatabaseError) as error:
        logging.error(f'GET /dbproj/daily/<year_month_day> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if db is not None:
            db.close()

    return jsonify(response)

##
## Generates a monthly report where are listed the doctors with more surgeries
## in each month for the last 12 months.
## NOTE: The current month is not included.
##
@app.route('/dbproj/report', methods=['GET'])
@jwt_required()
@roles_required('assistant')
def generate_monthly_report():
    logger.info('GET /dbproj/report')
    
    statement = '''
                WITH MonthlySurgeryCount AS (
                    SELECT
                        EXTRACT(YEAR FROM s.date) AS year,
                        EXTRACT(MONTH FROM s.date) AS month,
                        e.doctor_employee_person_cc AS doctor_id,
                        COUNT(*) AS surgery_count,
                        ROW_NUMBER() OVER (PARTITION BY EXTRACT(YEAR FROM s.date), EXTRACT(MONTH FROM s.date) ORDER BY COUNT(*) DESC) AS rank
                    FROM surgery s
                    INNER JOIN equip e ON s.equip_equip_id = e.equip_id
                    WHERE
                        s.date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '12 months' AND
                        s.date <= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 day'
                    GROUP BY
                        EXTRACT(YEAR FROM s.date),
                        EXTRACT(MONTH FROM s.date),
                        e.doctor_employee_person_cc
                )
                SELECT
                    to_char(to_date(concat(msc.year::text, '-', msc.month::text, '-01'), 'YYYY-MM-DD'), 'Month YYYY') AS month_year,
                    p.name AS doctor_name,
                    msc.surgery_count AS surgery_count
                FROM MonthlySurgeryCount msc
                INNER JOIN person p ON msc.doctor_id = p.cc
                WHERE msc.rank = 1
                ORDER BY msc.year DESC, msc.month DESC;
                '''
    
    # Connecting to Data Base
    db = db_connect()
    cursor = db.cursor()

    try:
        # Executing the query
        cursor.execute(statement)
        result = cursor.fetchall()
        
        monthly_rep = []
        for row in result:
            monthly_rep.append({
                'year-month': row[0],
                'doctor': row[1],
                'number of surgeries': row[2]
            })
        response = {'status': StatusCodes['success'], 'results': {'monthly_report': monthly_rep}}    
        
    except(Exception, psycopg2.DatabaseError) as error:
        logging.error(f'GET /dbproj/report - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if db is not None:
            db.close()

    return jsonify(response)


if __name__ == '__main__':
    # set up logging
    logging.basicConfig(filename='log_file.log')
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    host = '127.0.0.1'
    port = 8080
    app.run(host=host, debug=True, threaded=True, port=port)
    logger.info(f'API v1.0 online: http://{host}:{port}')