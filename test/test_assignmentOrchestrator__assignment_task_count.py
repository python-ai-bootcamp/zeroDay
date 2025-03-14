import pytest
from unittest.mock import patch, mock_open, Mock
from pathlib import Path
from assignmentOrchestrator import AssignmentSubmission, assignment_task_count
import base64,os,shutil,json

gconf={}

@pytest.fixture
def mocker__on_empty_data(mocker,request):   
    gconf["base_test_directory"]                        =f"./data/testData/assignmentOrchestrator/assignment_description/{request.node.name}"
    gconf["relative_data_directory"]                    =os.path.join(gconf["base_test_directory"],"data")
    gconf["relative_submitted_files_directory"]         =os.path.join(gconf["relative_data_directory"],"submitted_files")

    gconf["relative_assignments_directory"]             =os.path.join(gconf["base_test_directory"],"resources","config","assignments")
    gconf["relative_validators_directory"]              =os.path.join(gconf["relative_assignments_directory"],"validators")
    gconf["relative_assignment_descriptions_directory"] =os.path.join(gconf["relative_assignments_directory"],"assignment_descriptions")
    gconf["test_assignment_mapper_json_file_location"]  =os.path.join(gconf["relative_assignments_directory"],"assignment_mapper.json")

    shutil.rmtree(gconf["relative_data_directory"],ignore_errors=True) 
    os.makedirs(gconf["relative_submitted_files_directory"],exist_ok=True)
    
    shutil.rmtree(gconf["relative_assignments_directory"],ignore_errors=True)
    os.makedirs(gconf["relative_validators_directory"],exist_ok=True)
    os.makedirs(gconf["relative_assignment_descriptions_directory"],exist_ok=True)

    mocker.patch("assignmentOrchestrator.SUBMITTED_FILES_DIR",          gconf["relative_submitted_files_directory"])
    mocker.patch("assignmentOrchestrator.ASSIGNMENT_VALIDATOR_DIR",     gconf["relative_validators_directory"])
    mocker.patch("assignmentOrchestrator.ASSIGNMENT_MAPPER_FILE",       gconf["test_assignment_mapper_json_file_location"])
    mocker.patch("assignmentOrchestrator.ASSIGNMENT_DESCRIPTIONS_DIR",  gconf["relative_assignment_descriptions_directory"])
    
def test_load_existing_validators_count_in_assignment_mapper(mocker__on_empty_data):
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py']}}
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    assert assignment_task_count(1) == {"task_count":1}

def test_load_non_existing_validators_entry_in_assignment_mapper(mocker__on_empty_data):
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md'}}
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    assert assignment_task_count(1) == {"status":"ERROR",'ERROR_message': "assignment with assignment_id='1' is missing validators entry"}

def test_load_existing_validators_entry_in_assignment_mapper_with_zero_validators(mocker__on_empty_data):
    test_assignment_mapper_json_file_data={'1': {'validators': []}}
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    assert assignment_task_count(1) == {"status":"ERROR", "ERROR_message": "assignment with assignment_id='1' does not contain even a single validator"}

def test_load_missing_assignment_entry_in_assignment_mapper(mocker__on_empty_data):
    test_assignment_mapper_json_file_data={'1': {'validators': ['blsdfsdfsfd.md']}}
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    assert assignment_task_count(2) == {"status":"ERROR", "ERROR_message": "no entry for assignment with assignment_id='2' inside assignment_mapper file"}