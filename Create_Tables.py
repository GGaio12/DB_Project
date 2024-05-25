from DB_Connection import db_connect

db = db_connect()
cursor = db.cursor()

cursor.execute('''
DROP TABLE IF EXISTS 
patient, person, nurse, doctor, assistant, employee, hospitalization, 
surgery, appointment, equip, registration, prescription, medicine, 
sideefect, payment, specialization, contract, surgerytype, 
sup_specialization, medicine_prescription, appointment_prescription, 
hospitalization_prescription, nurse_equip, nurserank;
               
CREATE TABLE patient (
	patient_id SERIAL,
	person_cc	 INTEGER,
	PRIMARY KEY(person_cc)
);

CREATE TABLE person (
	cc	 INTEGER,
	name	 VARCHAR(512) NOT NULL,
	birthdate DATE NOT NULL,
	password	VARCHAR(512) NOT NULL,
	email	 VARCHAR(512) NOT NULL,
	PRIMARY KEY(cc)
);

CREATE TABLE nurse (
	nurse_id		 SERIAL,
 	nurserank_rank_id INTEGER NOT NULL,
	employee_person_cc INTEGER,
	PRIMARY KEY(employee_person_cc)
);

CREATE TABLE doctor (
	doctor_id	 SERIAL,
	medical_license	 VARCHAR(512) NOT NULL,
	employee_person_cc INTEGER,
	PRIMARY KEY(employee_person_cc)
);

CREATE TABLE assistant (
	assistant_id	 SERIAL,
	employee_person_cc INTEGER,
	PRIMARY KEY(employee_person_cc)
);

CREATE TABLE employee (
	emp_id	 SERIAL,
	person_cc INTEGER,
	PRIMARY KEY(person_cc)
);

CREATE TABLE hospitalization (
	hosp_id			 SERIAL,
	cost			DOUBLE PRECISION,
	date		TIMESTAMP NOT NULL,
	room_num			 INTEGER NOT NULL,
	nurse_employee_person_cc	 INTEGER NOT NULL,
	registration_registration_id INTEGER,
	PRIMARY KEY(registration_registration_id)
);

CREATE TABLE surgery (
	sur_id					 SERIAL,
 	cost			DOUBLE PRECISION,
	date					TIMESTAMP NOT NULL,
	operating_room				 VARCHAR(512) NOT NULL,
	surgerytype_sur_type_id			 INTEGER NOT NULL,
	equip_equip_id				 INTEGER NOT NULL,
	hospitalization_registration_registration_id INTEGER NOT NULL,
	PRIMARY KEY(sur_id)
);

CREATE TABLE appointment (
	appoint_id		 SERIAL,
	cost			DOUBLE PRECISION,
	appoint_date	TIMESTAMP NOT NULL,
	equip_equip_id		 INTEGER NOT NULL,
	registration_registration_id INTEGER,
	PRIMARY KEY(registration_registration_id)
);

CREATE TABLE equip (
	equip_id		 SERIAL,
	doctor_employee_person_cc INTEGER NOT NULL,
	PRIMARY KEY(equip_id)
);

CREATE TABLE registration (
	registration_id		 SERIAL,
	regist_date	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	bill			 DOUBLE PRECISION DEFAULT 0,
	bill_payed	BOOLEAN DEFAULT TRUE,
	assistant_employee_person_cc INTEGER NOT NULL,
	patient_person_cc		 INTEGER NOT NULL,
	PRIMARY KEY(registration_id)
);

CREATE TABLE prescription (
	prescription_id SERIAL,
	validity	DATE NOT NULL,
	PRIMARY KEY(prescription_id)
);

CREATE TABLE medicine (
	medicine_id SERIAL,
	med_name	VARCHAR(512) NOT NULL,
	dosage	 VARCHAR(512) NOT NULL,
	frequency	VARCHAR(512) NOT NULL,
	PRIMARY KEY(medicine_id)
);

CREATE TABLE sideefect (
	sidefect_id		 SERIAL,
	probability		 INTEGER NOT NULL,
	severity		 VARCHAR(512) NOT NULL,
	medicine_medicine_id INTEGER,
	PRIMARY KEY(sidefect_id,medicine_medicine_id)
);

CREATE TABLE payment (
	payment_id		 SERIAL,
	amount			DOUBLE PRECISION,
	type			 VARCHAR(512),
	registration_registration_id INTEGER,
	PRIMARY KEY(payment_id,registration_registration_id)
);

CREATE TABLE specialization (
	spec_id			 SERIAL,
	name			 VARCHAR(512) NOT NULL,
	doctor_employee_person_cc INTEGER NOT NULL,
	PRIMARY KEY(spec_id)
);

CREATE TABLE contract (
	contract_id	 SERIAL,
	start_date	 DATE NOT NULL,
	end_date		 DATE NOT NULL,
	sal		 FLOAT(8) NOT NULL,
	work_hours	 INTEGER NOT NULL,
	employee_person_cc INTEGER NOT NULL,
	PRIMARY KEY(contract_id)
);

CREATE TABLE surgerytype (
	sur_type_ip SERIAL,
	name	 VARCHAR(512) NOT NULL,
	PRIMARY KEY(sur_type_ip)
);

CREATE TABLE sup_specialization (
	specialization_spec_id	 INTEGER,
	low_specialization_spec_id INTEGER NOT NULL,
	PRIMARY KEY(specialization_spec_id)
);

CREATE TABLE medicine_prescription (
	medicine_medicine_id	 INTEGER,
	prescription_prescription_id INTEGER,
	PRIMARY KEY(medicine_medicine_id,prescription_prescription_id)
);

CREATE TABLE appointment_prescription (
	appointment_registration_registration_id INTEGER NOT NULL,
	prescription_prescription_id		 INTEGER,
	PRIMARY KEY(prescription_prescription_id)
);

CREATE TABLE hospitalization_prescription (
	hospitalization_registration_registration_id INTEGER NOT NULL,
	prescription_prescription_id		 INTEGER,
	PRIMARY KEY(prescription_prescription_id)
);

CREATE TABLE nurse_equip (
    nurse_equip_id	SERIAL,
	nurse_employee_person_cc INTEGER,
	equip_equip_id		 INTEGER NOT NULL,
	PRIMARY KEY(nurse_equip_id)
);

CREATE TABLE nurserank (
	rank_id SERIAL,
	rank	 INTEGER NOT NULL,
	PRIMARY KEY(rank_id)
);

ALTER TABLE patient ADD CONSTRAINT patient_fk1 FOREIGN KEY (person_cc) REFERENCES person(cc);
ALTER TABLE nurse ADD CONSTRAINT nurse_fk1 FOREIGN KEY (employee_person_cc) REFERENCES employee(person_cc);
ALTER TABLE nurse ADD CONSTRAINT nurse_fk2 FOREIGN KEY (nurserank_rank_id) REFERENCES nurserank(rank_id);
ALTER TABLE doctor ADD CONSTRAINT doctor_fk1 FOREIGN KEY (employee_person_cc) REFERENCES employee(person_cc);
ALTER TABLE assistant ADD CONSTRAINT assistant_fk1 FOREIGN KEY (employee_person_cc) REFERENCES employee(person_cc);
ALTER TABLE employee ADD CONSTRAINT employee_fk1 FOREIGN KEY (person_cc) REFERENCES person(cc);
ALTER TABLE hospitalization ADD CONSTRAINT hospitalization_fk1 FOREIGN KEY (nurse_employee_person_cc) REFERENCES nurse(employee_person_cc);
ALTER TABLE hospitalization ADD CONSTRAINT hospitalization_fk2 FOREIGN KEY (registration_registration_id) REFERENCES registration(registration_id);
ALTER TABLE surgery ADD CONSTRAINT surgery_fk1 FOREIGN KEY (surgerytype_sur_type_id) REFERENCES surgerytype(sur_type_ip);
ALTER TABLE surgery ADD CONSTRAINT surgery_fk2 FOREIGN KEY (equip_equip_id) REFERENCES equip(equip_id);
ALTER TABLE surgery ADD CONSTRAINT surgery_fk3 FOREIGN KEY (hospitalization_registration_registration_id) REFERENCES hospitalization(registration_registration_id);
ALTER TABLE appointment ADD CONSTRAINT appointment_fk1 FOREIGN KEY (equip_equip_id) REFERENCES equip(equip_id);
ALTER TABLE appointment ADD CONSTRAINT appointment_fk2 FOREIGN KEY (registration_registration_id) REFERENCES registration(registration_id);
ALTER TABLE equip ADD CONSTRAINT equip_fk1 FOREIGN KEY (doctor_employee_person_cc) REFERENCES doctor(employee_person_cc);
ALTER TABLE registration ADD CONSTRAINT registration_fk1 FOREIGN KEY (assistant_employee_person_cc) REFERENCES assistant(employee_person_cc);
ALTER TABLE registration ADD CONSTRAINT registration_fk2 FOREIGN KEY (patient_person_cc) REFERENCES patient(person_cc);
ALTER TABLE sideefect ADD CONSTRAINT sideefect_fk1 FOREIGN KEY (medicine_medicine_id) REFERENCES medicine(medicine_id);
ALTER TABLE payment ADD CONSTRAINT payment_fk1 FOREIGN KEY (registration_registration_id) REFERENCES registration(registration_id);
ALTER TABLE specialization ADD CONSTRAINT specialization_fk1 FOREIGN KEY (doctor_employee_person_cc) REFERENCES doctor(employee_person_cc);
ALTER TABLE contract ADD CONSTRAINT contract_fk1 FOREIGN KEY (employee_person_cc) REFERENCES employee(person_cc);
ALTER TABLE sup_specialization ADD CONSTRAINT sup_specialization_fk1 FOREIGN KEY (specialization_spec_id) REFERENCES specialization(spec_id);
ALTER TABLE sup_specialization ADD CONSTRAINT sup_specialization_fk2 FOREIGN KEY (low_specialization_spec_id) REFERENCES specialization(spec_id);
ALTER TABLE medicine_prescription ADD CONSTRAINT medicine_prescription_fk1 FOREIGN KEY (medicine_medicine_id) REFERENCES medicine(medicine_id);
ALTER TABLE medicine_prescription ADD CONSTRAINT medicine_prescription_fk2 FOREIGN KEY (prescription_prescription_id) REFERENCES prescription(prescription_id);
ALTER TABLE appointment_prescription ADD CONSTRAINT appointment_prescription_fk1 FOREIGN KEY (appointment_registration_registration_id) REFERENCES appointment(registration_registration_id);
ALTER TABLE appointment_prescription ADD CONSTRAINT appointment_prescription_fk2 FOREIGN KEY (prescription_prescription_id) REFERENCES prescription(prescription_id);
ALTER TABLE hospitalization_prescription ADD CONSTRAINT hospitalization_prescription_fk1 FOREIGN KEY (hospitalization_registration_registration_id) REFERENCES hospitalization(registration_registration_id);
ALTER TABLE hospitalization_prescription ADD CONSTRAINT hospitalization_prescription_fk2 FOREIGN KEY (prescription_prescription_id) REFERENCES prescription(prescription_id);
ALTER TABLE nurse_equip ADD CONSTRAINT nurse_equip_fk1 FOREIGN KEY (nurse_employee_person_cc) REFERENCES nurse(employee_person_cc);
ALTER TABLE nurse_equip ADD CONSTRAINT nurse_equip_fk2 FOREIGN KEY (equip_equip_id) REFERENCES equip(equip_id);
ALTER TABLE nurserank ADD UNIQUE (rank);

CREATE OR REPLACE FUNCTION update_registration() RETURNS TRIGGER AS $$
BEGIN
    IF TG_TABLE_NAME = 'surgery' THEN
        UPDATE registration
        SET bill = bill + NEW.cost,
            bill_payed = FALSE
        WHERE registration_id = NEW.hospitalization_registration_registration_id;
    ELSE
        UPDATE registration
        SET bill = bill + NEW.cost,
            bill_payed = FALSE
        WHERE registration_id = NEW.registration_registration_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER appointment_insert
AFTER INSERT ON appointment
FOR EACH ROW
EXECUTE FUNCTION update_registration();

CREATE TRIGGER surgery_insert
AFTER INSERT ON surgery
FOR EACH ROW
EXECUTE FUNCTION update_registration();

CREATE TRIGGER hospitalization_insert
AFTER INSERT ON hospitalization
FOR EACH ROW
EXECUTE FUNCTION update_registration();
''')

db.commit()
db.close()