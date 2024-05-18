from DB_Connection import db_connect

db = db_connect()
cursor = db.cursor()

cursor.execute('''
DROP TABLE IF EXISTS 
patients, person, nurse, doctor, assistents, employee, hospitalization, 
surgery, appointment, equip, registation, prescription, medicine, 
sideefect, payment, specialization, contract, surgerytypes, 
sup_specializations, medicine_prescription, appointment_prescription, 
hospitalization_prescription, nurse_equip, sup_nurses;
               
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
	employee_person_cc INTEGER,
	PRIMARY KEY(employee_person_cc)
);

CREATE TABLE doctor (
	doctor_id	 SERIAL,
	medical_licence	 VARCHAR(512) NOT NULL,
	employee_person_cc INTEGER,
	PRIMARY KEY(employee_person_cc)
);

CREATE TABLE assistents (
	assistent_id	 SERIAL,
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
	room_num			 INTEGER NOT NULL,
	nurse_employee_person_cc	 INTEGER NOT NULL,
	registation_registation_id INTEGER,
	PRIMARY KEY(registation_registation_id)
);

CREATE TABLE surgery (
	sur_id					 SERIAL,
	operating_room				 VARCHAR(512) NOT NULL,
	surgerytypes_sur_type_ip			 INTEGER NOT NULL,
	equip_equip_id				 INTEGER NOT NULL,
	hospitalization_registation_registation_id INTEGER NOT NULL,
	PRIMARY KEY(sur_id)
);

CREATE TABLE appointment (
	appoint_id		 SERIAL,
	equip_equip_id		 INTEGER NOT NULL,
	registation_registation_id INTEGER,
	PRIMARY KEY(registation_registation_id)
);

CREATE TABLE equip (
	equip_id		 SERIAL,
	doctor_employee_person_cc INTEGER NOT NULL,
	PRIMARY KEY(equip_id)
);

CREATE TABLE registation (
	registation_id		 SERIAL,
	billing			 DOUBLE PRECISION NOT NULL,
	assistents_employee_person_cc INTEGER NOT NULL,
	patients_person_cc		 INTEGER NOT NULL,
	PRIMARY KEY(registation_id)
);

CREATE TABLE prescription (
	prescription_id SERIAL,
	PRIMARY KEY(prescription_id)
);

CREATE TABLE medicine (
	medicine_id SERIAL,
	dosage	 INTEGER,
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
	spec_id			 SERIAL,
	name			 VARCHAR(512) NOT NULL,
	doctor_employee_person_cc INTEGER NOT NULL,
	PRIMARY KEY(spec_id)
);

CREATE TABLE contract (
	contract_id	 SERIAL,
	start_date	 VARCHAR(512) NOT NULL,
	end_date		 VARCHAR(512) NOT NULL,
	sal		 FLOAT(8) NOT NULL,
	work_hours	 INTEGER NOT NULL,
	employee_person_cc INTEGER NOT NULL,
	PRIMARY KEY(contract_id)
);

CREATE TABLE surgerytypes (
	sur_type_ip SERIAL,
	name	 VARCHAR(512) NOT NULL,
	PRIMARY KEY(sur_type_ip)
);

CREATE TABLE sup_specializations (
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
	appointment_registation_registation_id INTEGER NOT NULL,
	prescription_prescription_id		 INTEGER,
	PRIMARY KEY(prescription_prescription_id)
);

CREATE TABLE hospitalization_prescription (
	hospitalization_registation_registation_id INTEGER NOT NULL,
	prescription_prescription_id		 INTEGER,
	PRIMARY KEY(prescription_prescription_id)
);

CREATE TABLE nurse_equip (
	nurse_employee_person_cc INTEGER,
	equip_equip_id		 INTEGER NOT NULL,
	PRIMARY KEY(nurse_employee_person_cc)
);

CREATE TABLE sup_nurses (
	nurse_employee_person_cc	 INTEGER,
	low_nurse_employee_person_cc INTEGER NOT NULL,
	PRIMARY KEY(nurse_employee_person_cc)
);

ALTER TABLE patients ADD CONSTRAINT patients_fk1 FOREIGN KEY (person_cc) REFERENCES person(cc);
ALTER TABLE nurse ADD CONSTRAINT nurse_fk1 FOREIGN KEY (employee_person_cc) REFERENCES employee(person_cc);
ALTER TABLE doctor ADD CONSTRAINT doctor_fk1 FOREIGN KEY (employee_person_cc) REFERENCES employee(person_cc);
ALTER TABLE assistents ADD CONSTRAINT assistents_fk1 FOREIGN KEY (employee_person_cc) REFERENCES employee(person_cc);
ALTER TABLE employee ADD CONSTRAINT employee_fk1 FOREIGN KEY (person_cc) REFERENCES person(cc);
ALTER TABLE hospitalization ADD CONSTRAINT hospitalization_fk1 FOREIGN KEY (nurse_employee_person_cc) REFERENCES nurse(employee_person_cc);
ALTER TABLE hospitalization ADD CONSTRAINT hospitalization_fk2 FOREIGN KEY (registation_registation_id) REFERENCES registation(registation_id);
ALTER TABLE surgery ADD CONSTRAINT surgery_fk1 FOREIGN KEY (surgerytypes_sur_type_ip) REFERENCES surgerytypes(sur_type_ip);
ALTER TABLE surgery ADD CONSTRAINT surgery_fk2 FOREIGN KEY (equip_equip_id) REFERENCES equip(equip_id);
ALTER TABLE surgery ADD CONSTRAINT surgery_fk3 FOREIGN KEY (hospitalization_registation_registation_id) REFERENCES hospitalization(registation_registation_id);
ALTER TABLE appointment ADD CONSTRAINT appointment_fk1 FOREIGN KEY (equip_equip_id) REFERENCES equip(equip_id);
ALTER TABLE appointment ADD CONSTRAINT appointment_fk2 FOREIGN KEY (registation_registation_id) REFERENCES registation(registation_id);
ALTER TABLE equip ADD CONSTRAINT equip_fk1 FOREIGN KEY (doctor_employee_person_cc) REFERENCES doctor(employee_person_cc);
ALTER TABLE registation ADD CONSTRAINT registation_fk1 FOREIGN KEY (assistents_employee_person_cc) REFERENCES assistents(employee_person_cc);
ALTER TABLE registation ADD CONSTRAINT registation_fk2 FOREIGN KEY (patients_person_cc) REFERENCES patients(person_cc);
ALTER TABLE sideefect ADD CONSTRAINT sideefect_fk1 FOREIGN KEY (medicine_medicine_id) REFERENCES medicine(medicine_id);
ALTER TABLE payment ADD CONSTRAINT payment_fk1 FOREIGN KEY (registation_registation_id) REFERENCES registation(registation_id);
ALTER TABLE specialization ADD CONSTRAINT specialization_fk1 FOREIGN KEY (doctor_employee_person_cc) REFERENCES doctor(employee_person_cc);
ALTER TABLE contract ADD CONSTRAINT contract_fk1 FOREIGN KEY (employee_person_cc) REFERENCES employee(person_cc);
ALTER TABLE sup_specializations ADD CONSTRAINT sup_specializations_fk1 FOREIGN KEY (specialization_spec_id) REFERENCES specialization(spec_id);
ALTER TABLE sup_specializations ADD CONSTRAINT sup_specializations_fk2 FOREIGN KEY (low_specialization_spec_id) REFERENCES specialization(spec_id);
ALTER TABLE medicine_prescription ADD CONSTRAINT medicine_prescription_fk1 FOREIGN KEY (medicine_medicine_id) REFERENCES medicine(medicine_id);
ALTER TABLE medicine_prescription ADD CONSTRAINT medicine_prescription_fk2 FOREIGN KEY (prescription_prescription_id) REFERENCES prescription(prescription_id);
ALTER TABLE appointment_prescription ADD CONSTRAINT appointment_prescription_fk1 FOREIGN KEY (appointment_registation_registation_id) REFERENCES appointment(registation_registation_id);
ALTER TABLE appointment_prescription ADD CONSTRAINT appointment_prescription_fk2 FOREIGN KEY (prescription_prescription_id) REFERENCES prescription(prescription_id);
ALTER TABLE hospitalization_prescription ADD CONSTRAINT hospitalization_prescription_fk1 FOREIGN KEY (hospitalization_registation_registation_id) REFERENCES hospitalization(registation_registation_id);
ALTER TABLE hospitalization_prescription ADD CONSTRAINT hospitalization_prescription_fk2 FOREIGN KEY (prescription_prescription_id) REFERENCES prescription(prescription_id);
ALTER TABLE nurse_equip ADD CONSTRAINT nurse_equip_fk1 FOREIGN KEY (nurse_employee_person_cc) REFERENCES nurse(employee_person_cc);
ALTER TABLE nurse_equip ADD CONSTRAINT nurse_equip_fk2 FOREIGN KEY (equip_equip_id) REFERENCES equip(equip_id);
ALTER TABLE sup_nurses ADD CONSTRAINT sup_nurses_fk1 FOREIGN KEY (nurse_employee_person_cc) REFERENCES nurse(employee_person_cc);
ALTER TABLE sup_nurses ADD CONSTRAINT sup_nurses_fk2 FOREIGN KEY (low_nurse_employee_person_cc) REFERENCES nurse(employee_person_cc);
''')

db.commit()
db.close()