-- Pharmaceutical Research Company POC Database Design
-- Simple structure for drug research and clinical trials

researchers {
	id int pk
	researcher_type_id int > researcher_types.id
	employee_id varchar
	email varchar
	password varchar
	is_active boolean
	token_okta varchar
	token_azure varchar
	user_token varchar
	token_expiration datetime
}

researcher_types {
	id int pk
	type varchar -- 'scientist', 'lab_tech', 'data_analyst', 'principal_investigator'
	access_level int
}

researcher_labs {
	id int pk
	researcher_id int > researchers.id
	lab_name varchar
	building varchar
	room_number varchar
}

compounds {
	id int pk
	compound_code varchar
	molecular_formula varchar
	research_stage varchar -- 'discovery', 'preclinical', 'phase1', 'phase2', 'phase3', 'approved'
	target_disease varchar
	created_date datetime
}

research_studies {
	id int pk
	compound_id int > compounds.id
	lead_researcher_id int > researchers.id
	study_protocol varchar
	start_date datetime
	end_date datetime
	status varchar -- 'planning', 'active', 'completed', 'terminated'
}

study_participants {
	id int pk
	study_id int > research_studies.id
	participant_code varchar
	age int
	gender varchar
	consent_signed boolean
	enrollment_date datetime
}

test_results {
	id int pk
	study_id int > research_studies.id
	participant_id int > study_participants.id
	test_date datetime
	test_type varchar
	result_value varchar
	notes text
}

lab_equipment {
	id int pk
	equipment_name varchar
	serial_number varchar
	last_calibration datetime
	next_calibration datetime
}

experiments {
	id int pk
	compound_id int > compounds.id
	researcher_id int > researchers.id
	equipment_id int > lab_equipment.id
	experiment_date datetime
	protocol_id varchar
	outcome varchar
	data_file_path varchar
}
