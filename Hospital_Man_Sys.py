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
## NOTE Dates have to be in YYYY-MM-DD format.
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
    
    is_employee = False
    if(type in ['nurse', 'doctor', 'assistant']):
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
    queries = [('person', '(cc, name, birthdate, email, password)', '%s, %s, %s, %s', (cc, name, birthdate, password))]
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
        if db is not None:
            db.close()

    return jsonify(response)
    
##
## User Authentication. Providing name and password,
## user can authenticate and receive an authentication token.
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
            response = {'status': StatusCodes['api_error'], 'results': f'{field} not in payload'}
            return jsonify(response)
    
    # Getting name and password
    name = payload['name']
    password = payload['password']
    
    # Constructing the query statement to execute
    statement = '''
                SELECT password, cc
                FROM %s 
                JOIN person ON cc=%s
                AND name=%s;
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
            values = (role, cc_type, name)
            
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
        if db is not None:
            db.close()

    return jsonify(response)


## the data:  --> TODOO!!!
##
## MADEIRA
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
@roles_required('assistant')
def get_patient_appointments(patient_user_id):
    logger.info('GET /dbproj/appointments/<patient_user_id>')
    logger.debug(f'patient_user_id: {patient_user_id}')
    
    # Connecting to Data Base
    db = db_connect()
    cursor = db.cursor()
    
    try:
        statement = '''
                    SELECT appoint_id AS id, appoint_date AS date, doctor_employee_person_cc AS doctor_id
                    FROM appointment AS ap
                    JOIN equip ON ap.equip_equip_id = equip.equip_id
                    JOIN registration AS reg ON ap.registration_registration_id = reg.registration_id
                    WHERE reg.patient_person_cc = %s;            
                    '''
        cursor.execute(statement, (patient_user_id,))
        result = cursor.fetchone()
        
        if(result):
            # Convert the result to a list of dictionaries
            appointments = []
            for row in result:
                appointments.append({
                    'id': row[0],
                    'date': row[1],
                    'doctor_id': row[2]
                })
            response = {'status': StatusCodes['success'], 'results': appointments}
        else:
            response = {'status': StatusCodes['api_error'], 'results': 'Patient does not exist or do not have any appointments registered'}

    except(Exception, psycopg2.DatabaseError) as error:
        logging.error(f'GET /dbproj/appointments/<patient_user_id> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if db is not None:
            db.close()

    return jsonify(response)
    
##
## Schedule a new surgery for a passient that isn't hospitalized yet
## inserting the data:  --> TODOO!!!
##
@app.route('/dbproj/surgery', methods=['POST'])
@jwt_required()
@roles_required('assistant')
def shedule_new_surgery_nh():
    return

##
## Schedule a new surgery for a passient that is already hospitalized
## inserting the data:  --> TODOO!!!
##
@app.route('/dbproj/surgery/<hospitalization_id>', methods=['POST'])
@jwt_required()
@roles_required('assistant')
def shedule_new_surgery_h(hospitalization_id):
    return

##
## Get the list of prescriptions and details of it for a specific passient
##
@app.route('/dbproj/prescriptions/<person_id>', methods=['GET'])
@jwt_required()
def get_passient_prescriptions(person_id):
    logger.info('GET /dbproj/prescriptions/<person_id>')
    logger.debug(f'person_id: {person_id}')
    
    identity = get_jwt_identity()
    logger.debug(f'identity: {identity}')
    if(identity['role'] == 'patient' and identity['id'] != person_id):
        return jsonify({'status': StatusCodes['api_error'], 'results': 'Your id does not matchs the url id provided'})
    
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
        result = cursor.fetchone()
        
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
                
            response = {'status': StatusCodes['success'], 'results': prescriptions}
        else:
            response = {'status': StatusCodes['api_error'], 'results': 'Patient does not exist or do not have any appointments registered'}

    except(Exception, psycopg2.DatabaseError) as error:
        logging.error(f'GET /dbproj/prescriptions/<person_id> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if db is not None:
            db.close()

    return jsonify(response)

##
## Adds a new prescription inserting the data:
## 'type', 'event_id', 'validity', 'medicines'
## NOTE: 'medicines' is a list of medicines each containing: 'medicine_name', 'dosage', 'frequency'
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
    
    # Verifying the inserted type
    if(payload['type'] == 'appointment'):
        type_id = 'appoint_id'
    elif(payload['type'] == 'hospitalization'):
        type_id = 'hosp_id'
    else:
        return jsonify({'status': StatusCodes['api_error'], 'results': f'Type in payload not regonized'})
    
    # Verifying medicines fields
    for i, medicine in enumerate(payload['medicines'], start=1):
        for field in med_fields:
            if field not in medicine:
                return jsonify({'status': StatusCodes['api_error'], 'results': f'{field} not in medicine N:{i} payload'})

    # SQL Statements
    # Note: Because type_id and payload['type'] are created in code or already verifyed, it doesn't represent a scurity issue
    statements = {
        'max_prescription_id': 'SELECT MAX(prescription_id) FROM prescription;',
        'max_medicine_id': 'SELECT MAX(medicine_id) FROM medicine;',
        'max_event_type_id': f'SELECT MAX({type_id}) FROM {payload['type']};'
    }
    
    queries = [('prescription', 'validity', '%s', [payload['validity']])]
    
    # Connecting to Data Base
    db = db_connect()
    cursor = db.cursor()
    
    try:
        # Check if event_id exists
        cursor.execute(statements['max_event_type_id'])
        max_event_type_id = cursor.fetchone()[0]
        if int(payload['event_id']) > int(max_event_type_id):
            return jsonify({'status': StatusCodes['api_error'], 'results': 'Event id in payload does not exist'})

        # Get new prescription_id
        cursor.execute(statements['max_prescription_id'])
        pres_id = cursor.fetchone()[0] + 1

        # Get new medicine_id starting point
        cursor.execute(statements['max_medicine_id'])
        med_id = cursor.fetchone()[0]
        
        for medicine in payload['medicines']:
            med_id += 1
            queries.extend([
                            ('medicine', '(med_name, dosage, frequency)', '%s, %s, %s', [medicine['medicine_name'], medicine['dosage'], medicine['frequency']]),
                            ('medicine_prescription', '(medicine_medicine_id, prescription_prescription_id)', '%s, %s', [med_id, pres_id])
                          ])
        if(payload['type'] == 'appointment'):
            queries.append(('appointment_prescription', '(appointment_registration_registration_id, prescription_prescription_id)', '%s, %s', [payload['event_id'], pres_id]))
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
                
        response = {'status': StatusCodes['success'], 'results': pres_id}

    except(Exception, psycopg2.DatabaseError) as error:
        logging.error(f'POST /dbproj/prescription/ - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if db is not None:
            db.close()

    return jsonify(response)

##
## Execute a payment of an existing bill inserting the data:
##  --> TODOO!!!
##
@app.route('/dbproj/bills/<bill_id>', methods=['POST'])
@jwt_required()
@roles_required('patient')
def pay_bill(bill_id):
    current_user_id = get_jwt_identity()

    # Retrieve the bill from the database
    bill = Bill.query.get(bill_id)
    
    if not bill:
        return jsonify({"error": "Bill not found"}), 404

    # Verify that the bill belongs to the patient making the request
    if bill.patient_id != current_user_id:
        return jsonify({"error": "Unauthorized access to this bill"}), 403

    # Process the payment (dummy implementation)
    payment_amount = request.json.get('amount')
    if not payment_amount or payment_amount <= 0:
        return jsonify({"error": "Invalid payment amount"}), 400

    if payment_amount > bill.amount_due:
        return jsonify({"error": "Payment amount exceeds amount due"}), 400

    # Update the bill's status and the amount due
    bill.amount_due -= payment_amount
    if bill.amount_due == 0:
        bill.status = 'Paid'

    # Record the payment
    payment = Payment(
        bill_id=bill_id,
        patient_id=current_user_id,
        amount=payment_amount,
        payment_date=datetime.utcnow()
    )

    db.session.add(payment)
    db.session.commit()

    return jsonify({"message": "Payment successful", "bill_id": bill_id, "amount_paid": payment_amount}), 200

##
## Lists top 3 passients considering the money spent in the month.
##
@app.route('/dbproj/top3', methods=['GET'])
@jwt_required()
@roles_required('assistant')
def get_top3_passients():
    return

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
                    SUM(ammount) AS "Total Ammount Payed",
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
        response = {'status': StatusCodes['success'], 'results': monthly_rep}    
        
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