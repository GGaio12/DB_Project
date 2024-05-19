from DB_Connection import db_connect
import flask
import logging

app = flask.Flask(__name__)

StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}


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
## Creates a new individual of type <type> inserting
## the data:  --> TODOO!!!
##
@app.route('/dbproj/register/<type>', methods=['POST'])
def insert_type(type):
    return
    
##
## User Authentication. Providing username and password,
## user can authenticate and receive a authentication token.
##
@app.route('/dbproj/user', methods=['PUT'])
def authenticate_user():
    return
    
##
## Schedule	Appointment. Creates a new appointment inserting
## the data:  --> TODOO!!!
##
@app.route('/dbproj/appointment', methods=['POST'])
def schedule_appointment():
    return
    
##
## Get appointments information. Lists all appointments and
## their detailed info by giving the patient_user_id in url.
##
@app.route('/dbproj/appointments/<patient_user_id>', methods=['GET'])
def get_patient_appointments(patient_user_id):
    return
    
##
## Schedule a new surgery for a passient that isn't hospitalized yet
## inserting the data:  --> TODOO!!!
##
@app.route('/dbproj/surgery', methods=['POST'])
def shedule_new_surgery_nh():
    return

##
## Schedule a new surgery for a passient that is already hospitalized
## inserting the data:  --> TODOO!!!
##
@app.route('/dbproj/surgery/<hospitalization_id>', methods=['POST'])
def shedule_new_surgery_h(hospitalization_id):
    return

##
## Get the list of prescriptions and details of it for a specific passient
##
@app.route('/dbproj/prescriptions/<person_id>', methods=['GET'])
def get_passient_prescriptions(person_id):
    return

##
## Adds a new prescription inserting the data:
##   --> TODOO!!!
##
@app.route('/dbproj/prescription/', methods=['POST'])
def get_passient_prescriptions():
    return

##
## Execute a payment of an existing bill inserting the data:
##  --> TODOO!!!
##
@app.route('/dbproj/bills/<bill_id>', methods=['POST'])
def pay_bill(bill_id):
    return

##
## Lists top 3 passients considering the money spent in the month.
##
@app.route('/dbproj/top3', methods=['GET'])
def get_top3_passients():
    return

##
## Daily summary. Lists a count for all hospitalizations details of a day.
##
@app.route('/dbproj/daily/<year-month-day>', methods=['GET'])
def list_daily_summary(time_stamp):
    return

##
## Generates a monthly report where are listed the doctors with more surgeries
## in each month for the 12 months.
##
@app.route('/dbproj/report', methods=['GET'])
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