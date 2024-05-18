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
## Landing Page of the Project
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
@app.route('/dbproj/register/<type>')
def insert_type(type):
    return
    
##
## User Authentication. Providing username and password,
## user can authenticate and receive a authentication token.
##
@app.route('/dbproj/user')
def landing_page():
    return
    
##
## Landing Page of the Project
##
@app.route('/')
def landing_page():
    return
    
##
## Landing Page of the Project
##
@app.route('/')
def landing_page():
    
    
##
## Landing Page of the Project
##
@app.route('/')
def landing_page():





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