from DB_Connection import db_connect

db = db_connect()
cursor = db.cursor()

cursor.execute('''
DROP TABLE IF EXISTS 
patients, person, nurse, doctor, assistents, 
employe, hospitalization, equip_surgery_appointment, registation, 
prescription, medicine, sideefect, payment, specialization, contract, 
surgerytypes, specialization_specialization, medicine_prescription, 
equip_surgery_appointment_prescription, hospitalization_prescription, 
nurse_equip_surgery_appointment, nurse_nurse;
               
CREATE TABLE patients (
	patient_id SERIAL,
	person_cc	 INTEGER,
	PRIMARY KEY(person_cc)
);

CREATE TABLE person (
	cc	 INTEGER,
	name	 VARCHAR(512) NOT NULL,
	birthdate VARCHAR(512) NOT NULL,
	PRIMARY KEY(cc)
);

CREATE TABLE nurse (
	nurse_id		 SERIAL,
	employe_person_cc INTEGER,
	PRIMARY KEY(employe_person_cc)
);

CREATE TABLE doctor (
	doctor_id	 SERIAL,
	medical_licence	 VARCHAR(512) NOT NULL,
	employe_person_cc INTEGER,
	PRIMARY KEY(employe_person_cc)
);

CREATE TABLE assistents (
	assistent_id	 SERIAL,
	employe_person_cc INTEGER,
	PRIMARY KEY(employe_person_cc)
);

CREATE TABLE employe (
	emp_id	 SERIAL,
	person_cc INTEGER,
	PRIMARY KEY(person_cc)
);

CREATE TABLE hospitalization (
	hosp_id			 SERIAL,
	room_num			 INTEGER NOT NULL,
	nurse_employe_person_cc	 INTEGER NOT NULL,
	registation_registation_id INTEGER,
	PRIMARY KEY(registation_registation_id)
);

CREATE TABLE equip_surgery_appointment (
	equip_id					 SERIAL,
	surgery_sur_id				 SERIAL NOT NULL,
	surgery_operating_room			 VARCHAR(512) NOT NULL,
	appointment_appoint_id			 SERIAL NOT NULL,
	surgerytypes_sur_type_ip			 INTEGER NOT NULL,
	doctor_employe_person_cc			 INTEGER NOT NULL,
	hospitalization_registation_registation_id INTEGER NOT NULL,
	registation_registation_id		 INTEGER,
	PRIMARY KEY(registation_registation_id)
);

CREATE TABLE registation (
	registation_id		 SERIAL,
	billing			 DOUBLE PRECISION NOT NULL,
	assistents_employe_person_cc INTEGER NOT NULL,
	patients_person_cc		 INTEGER NOT NULL,
	PRIMARY KEY(registation_id)
);

CREATE TABLE prescription (
	prescription_id SERIAL,
	PRIMARY KEY(prescription_id)
);

CREATE TABLE medicine (
	medicine_id SERIAL,
	dosage	 CHAR(255),
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
	type			 VARCHAR(512),
	registation_registation_id INTEGER,
	PRIMARY KEY(payment_id,registation_registation_id)
);

CREATE TABLE specialization (
	spec_id			 INTEGER,
	name			 VARCHAR(512) NOT NULL,
	doctor_employe_person_cc INTEGER NOT NULL,
	PRIMARY KEY(spec_id)
);

CREATE TABLE contract (
	contract_id	 SERIAL,
	start_date	 VARCHAR(512) NOT NULL,
	end_date		 VARCHAR(512) NOT NULL,
	sal		 FLOAT(8) NOT NULL,
	work_hours	 INTEGER NOT NULL,
	employe_person_cc INTEGER NOT NULL,
	PRIMARY KEY(contract_id)
);

CREATE TABLE surgerytypes (
	sur_type_ip SERIAL,
	name	 VARCHAR(512) NOT NULL,
	PRIMARY KEY(sur_type_ip)
);

CREATE TABLE specialization_specialization (
	specialization_spec_id	 INTEGER,
	specialization_spec_id1 INTEGER NOT NULL,
	PRIMARY KEY(specialization_spec_id)
);

CREATE TABLE medicine_prescription (
	medicine_medicine_id	 INTEGER,
	prescription_prescription_id INTEGER,
	PRIMARY KEY(medicine_medicine_id,prescription_prescription_id)
);

CREATE TABLE equip_surgery_appointment_prescription (
	equip_surgery_appointment_registation_registation_id INTEGER NOT NULL,
	prescription_prescription_id			 INTEGER,
	PRIMARY KEY(prescription_prescription_id)
);

CREATE TABLE hospitalization_prescription (
	hospitalization_registation_registation_id INTEGER NOT NULL,
	prescription_prescription_id		 INTEGER,
	PRIMARY KEY(prescription_prescription_id)
);

CREATE TABLE nurse_equip_surgery_appointment (
	nurse_employe_person_cc				 INTEGER,
	equip_surgery_appointment_registation_registation_id INTEGER NOT NULL,
	PRIMARY KEY(nurse_employe_person_cc)
);

CREATE TABLE nurse_nurse (
	nurse_employe_person_cc	 INTEGER,
	nurse_employe_person_cc1 INTEGER NOT NULL,
	PRIMARY KEY(nurse_employe_person_cc)
);

ALTER TABLE patients ADD CONSTRAINT patients_fk1 FOREIGN KEY (person_cc) REFERENCES person(cc);
ALTER TABLE nurse ADD CONSTRAINT nurse_fk1 FOREIGN KEY (employe_person_cc) REFERENCES employe(person_cc);
ALTER TABLE doctor ADD CONSTRAINT doctor_fk1 FOREIGN KEY (employe_person_cc) REFERENCES employe(person_cc);
ALTER TABLE assistents ADD CONSTRAINT assistents_fk1 FOREIGN KEY (employe_person_cc) REFERENCES employe(person_cc);
ALTER TABLE employe ADD CONSTRAINT employe_fk1 FOREIGN KEY (person_cc) REFERENCES person(cc);
ALTER TABLE hospitalization ADD CONSTRAINT hospitalization_fk1 FOREIGN KEY (nurse_employe_person_cc) REFERENCES nurse(employe_person_cc);
ALTER TABLE hospitalization ADD CONSTRAINT hospitalization_fk2 FOREIGN KEY (registation_registation_id) REFERENCES registation(registation_id);
ALTER TABLE equip_surgery_appointment ADD UNIQUE (surgery_sur_id, appointment_appoint_id);
ALTER TABLE equip_surgery_appointment ADD CONSTRAINT equip_surgery_appointment_fk1 FOREIGN KEY (surgerytypes_sur_type_ip) REFERENCES surgerytypes(sur_type_ip);
ALTER TABLE equip_surgery_appointment ADD CONSTRAINT equip_surgery_appointment_fk2 FOREIGN KEY (doctor_employe_person_cc) REFERENCES doctor(employe_person_cc);
ALTER TABLE equip_surgery_appointment ADD CONSTRAINT equip_surgery_appointment_fk3 FOREIGN KEY (hospitalization_registation_registation_id) REFERENCES hospitalization(registation_registation_id);
ALTER TABLE equip_surgery_appointment ADD CONSTRAINT equip_surgery_appointment_fk4 FOREIGN KEY (registation_registation_id) REFERENCES registation(registation_id);
ALTER TABLE registation ADD CONSTRAINT registation_fk1 FOREIGN KEY (assistents_employe_person_cc) REFERENCES assistents(employe_person_cc);
ALTER TABLE registation ADD CONSTRAINT registation_fk2 FOREIGN KEY (patients_person_cc) REFERENCES patients(person_cc);
ALTER TABLE sideefect ADD CONSTRAINT sideefect_fk1 FOREIGN KEY (medicine_medicine_id) REFERENCES medicine(medicine_id);
ALTER TABLE payment ADD CONSTRAINT payment_fk1 FOREIGN KEY (registation_registation_id) REFERENCES registation(registation_id);
ALTER TABLE specialization ADD CONSTRAINT specialization_fk1 FOREIGN KEY (doctor_employe_person_cc) REFERENCES doctor(employe_person_cc);
ALTER TABLE contract ADD CONSTRAINT contract_fk1 FOREIGN KEY (employe_person_cc) REFERENCES employe(person_cc);
ALTER TABLE specialization_specialization ADD CONSTRAINT specialization_specialization_fk1 FOREIGN KEY (specialization_spec_id) REFERENCES specialization(spec_id);
ALTER TABLE specialization_specialization ADD CONSTRAINT specialization_specialization_fk2 FOREIGN KEY (specialization_spec_id1) REFERENCES specialization(spec_id);
ALTER TABLE medicine_prescription ADD CONSTRAINT medicine_prescription_fk1 FOREIGN KEY (medicine_medicine_id) REFERENCES medicine(medicine_id);
ALTER TABLE medicine_prescription ADD CONSTRAINT medicine_prescription_fk2 FOREIGN KEY (prescription_prescription_id) REFERENCES prescription(prescription_id);
ALTER TABLE equip_surgery_appointment_prescription ADD CONSTRAINT equip_surgery_appointment_prescription_fk1 FOREIGN KEY (equip_surgery_appointment_registation_registation_id) REFERENCES equip_surgery_appointment(registation_registation_id);
ALTER TABLE equip_surgery_appointment_prescription ADD CONSTRAINT equip_surgery_appointment_prescription_fk2 FOREIGN KEY (prescription_prescription_id) REFERENCES prescription(prescription_id);
ALTER TABLE hospitalization_prescription ADD CONSTRAINT hospitalization_prescription_fk1 FOREIGN KEY (hospitalization_registation_registation_id) REFERENCES hospitalization(registation_registation_id);
ALTER TABLE hospitalization_prescription ADD CONSTRAINT hospitalization_prescription_fk2 FOREIGN KEY (prescription_prescription_id) REFERENCES prescription(prescription_id);
ALTER TABLE nurse_equip_surgery_appointment ADD CONSTRAINT nurse_equip_surgery_appointment_fk1 FOREIGN KEY (nurse_employe_person_cc) REFERENCES nurse(employe_person_cc);
ALTER TABLE nurse_equip_surgery_appointment ADD CONSTRAINT nurse_equip_surgery_appointment_fk2 FOREIGN KEY (equip_surgery_appointment_registation_registation_id) REFERENCES equip_surgery_appointment(registation_registation_id);
ALTER TABLE nurse_nurse ADD CONSTRAINT nurse_nurse_fk1 FOREIGN KEY (nurse_employe_person_cc) REFERENCES nurse(employe_person_cc);
ALTER TABLE nurse_nurse ADD CONSTRAINT nurse_nurse_fk2 FOREIGN KEY (nurse_employe_person_cc1) REFERENCES nurse(employe_person_cc);
''')

db.commit()
db.close()