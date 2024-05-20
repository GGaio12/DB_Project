from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import Flask, request, jsonify
from DB_Connection import db_connect
from flask_bcrypt import Bcrypt
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

# Custom decorator for role-based access control
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
## Patient:   'cc', 'name', 'birthdate', 'password'
## Nuser:     'cc', 'name', 'birthdate', 'password', 'start_date', 'end_date', 'sal', 'work_hours'
## Assistent: 'cc', 'name', 'birthdate', 'password', 'start_date', 'end_date', 'sal', 'work_hours'
## Doctor:    'cc', 'name', 'birthdate', 'password', 'start_date', 'end_date', 'sal', 'work_hours', 'medical_licence', 'spec_name'
##
@app.route('/dbproj/register/<type>', methods=['POST'])
def insert_type(type):
    # Getting json payload
    payload = request.get_json()
    
    # Fields that have to be in payload
    required_fields = ['cc', 'name', 'birthdate', 'password']         # Commun fields
    employee_fields = ['start_date', 'end_date', 'sal', 'work_hours'] # Only employee fields
    doctor_fields = ['medical_licence', 'spec_name']                  # Only doctor fields

    # Verifying commun fields
    for field in required_fields:
        if(field not in payload):
            return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} not in payload'})

    is_employee = False
    if(type in ['nurse', 'doctor', 'assistent']):
        is_employee = True
        # Verifying only employee fields
        for field in employee_fields:
            if(field not in payload):
                return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} not in payload'})

        if(type == 'doctor'):
            # Verifying only doctor fields
            for field in doctor_fields:
                if(field not in payload):
                    return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} not in payload'})
    
    # Initializing commun fields values (hashing password)
    cc = payload['cc']
    name = payload['name']
    birthdate = payload['birthdate']
    password = bcrypt.generate_password_hash(payload['password']).decode('utf-8')
    
    # Constructing all queries 'table_name', 'columns', 'values_placeholders' and 'values' and placing them in a list by order of execution 
    queries = [('person', '(cc, name, birthdate, password)', '%s, %s, %s, %s', (cc, name, birthdate, password))]
    if(is_employee):
        queries.append(('employee', '(person_cc)', '%s', (cc,)))
        if(type == 'doctor'):
            queries.append(('doctor', '(employee_person_cc, medical_licence)', '%s, %s', (cc, payload['medical_licence'])))
            queries.append(('specialization', '(name, doctor_employee_person_cc)', '%s, %s', (payload['spec_name'], cc)))
        elif(type == 'nurse'):
            queries.append(('nurse', '(employee_person_cc)', '%s', (cc,)))
        else:
            queries.append(('assistents', '(employee_person_cc)', '%s', (cc,)))
        queries.append(('contract', '(start_date, end_date, sal, work_hours, employee_person_cc)', '%s, %s, %s, %s, %s',
                        (payload['start_date'], payload['end_date'], payload['sal'], payload['work_hours'], cc)))
    else:
        queries.append(('patients', '(person_cc)', '%s', (cc,)))
    
    # Connecting to Data Base
    db = db_connect()
    cursor = db.cursor()
    
    # Executing all queries
    try:
        for table, columns, values_placeholders, values in queries:
            query = f'''
                INSERT INTO {table} {columns}
                VALUES ({values_placeholders})
                ON CONFLICT DO NOTHING;
            '''
            cursor.execute(query, values)

        db.commit()
        response = {'status': StatusCodes['success'], 'results': cc}

    except(Exception, psycopg2.DatabaseError) as error:
        logging.error(f'POST /dbproj/register/<type> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if db:
            db.close()

    return jsonify(response)
    
##
## User Authentication. Providing name and password,
## user can authenticate and receive an authentication token.
##
@app.route('/dbproj/user', methods=['PUT'])
def authenticate_user():
    # Getting json payload
    payload = request.get_json()
    
    # Connecting to Data Base
    db = db_connect()
    cursor = db.cursor()
    
    # Verifying name and password are in payload
    if('name' not in payload or 'password' not in payload):
        response = {'status': StatusCodes['api_error'], 'results': 'name/password not in payload'}
        return jsonify(response)
    
    # Getting name and password
    name = payload['name']
    password = payload['password']
    
    # Constructing the query statement to execute
    statement = '''
                SELECT password, cc from %s join person
                on cc=%s
                and name=%s;
                '''

    try:
        for i in range(4):
            # Determinig query values
            if(i == 0):
                role = 'patient'
                cc_type = 'person_cc'
                table = 'patients'
            else:
                cc_type = 'employee_person_cc'
                if(i == 1):
                    role = 'nurse'
                    table = 'nurse'
                elif(i == 2):
                    role = 'doctor'
                    table = 'doctor'
                else:
                    role = 'assistent'
                    table = 'assistents'
            values = (table, cc_type, name)
            
            # Executing query
            cursor.execute(statement, values)
            result = cursor.fetchone()
            
            # Verifying result and password
            if(result and bcrypt.check_password_hash(result[0], password)):
                access_token = create_access_token(identity={'id': result[1], 'role': role})
                response = {'status': StatusCodes['success'], 'results': access_token}
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
@app.route('/dbproj/appointment', methods=['POST'])
@jwt_required()
@roles_required('patient')
def schedule_appointment():
    return
    
##
## Get appointments information. Lists all appointments and
## their detailed info by giving the patient_user_id in url.
##
@app.route('/dbproj/appointments/<patient_user_id>', methods=['GET'])
@jwt_required()
@roles_required('assistent')
def get_patient_appointments(patient_user_id):
    return
    
##
## Schedule a new surgery for a passient that isn't hospitalized yet
## inserting the data:  --> TODOO!!!
##
@app.route('/dbproj/surgery', methods=['POST'])
@jwt_required()
@roles_required('assistent')
def shedule_new_surgery_nh():
    return

##
## Schedule a new surgery for a passient that is already hospitalized
## inserting the data:  --> TODOO!!!
##
@app.route('/dbproj/surgery/<hospitalization_id>', methods=['POST'])
@jwt_required()
@roles_required('assistent')
def shedule_new_surgery_h(hospitalization_id):
    return

##
## Get the list of prescriptions and details of it for a specific passient
##
@app.route('/dbproj/prescriptions/<person_id>', methods=['GET'])
@jwt_required()
def get_passient_prescriptions(person_id):
    identity = get_jwt_identity()
    if(identity['role'] == 'patient' and identity['id'] != person_id):
        return jsonify({'status': StatusCodes['api_error'], 'results': 'Your id does not matchs the url id provided'})
    return

##
## Adds a new prescription inserting the data:
##   --> TODOO!!!
##
@app.route('/dbproj/prescription/', methods=['POST'])
@jwt_required()
@roles_required('doctor')
def add_prescription():
    return

##
## Execute a payment of an existing bill inserting the data:
##  --> TODOO!!!
##
@app.route('/dbproj/bills/<bill_id>', methods=['POST'])
@jwt_required()
@roles_required('patient')
def pay_bill(bill_id):
    # needs to verify if the bill is from the patient who is requesting it
    return

##
## Lists top 3 passients considering the money spent in the month.
##
@app.route('/dbproj/top3', methods=['GET'])
@jwt_required()
@roles_required('assistent')
def get_top3_passients():
    return

##
## Daily summary. Lists a count for all hospitalizations details of a day.
##
@app.route('/dbproj/daily/<year-month-day>', methods=['GET'])
@jwt_required()
@roles_required('assistent')
def list_daily_summary(time_stamp):
    return

##
## Generates a monthly report where are listed the doctors with more surgeries
## in each month for the 12 months.
##
@app.route('/dbproj/report', methods=['GET'])
@jwt_required()
@roles_required('assistent')
def generate_monthly_report():
    return


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