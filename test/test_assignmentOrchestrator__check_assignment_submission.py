import pytest
from unittest.mock import patch, mock_open, Mock
from pathlib import Path
from assignmentOrchestrator import AssignmentSubmission, check_assignment_submission
import base64,os,shutil,json

gconf={}

@pytest.fixture
def mocker__on_empty_data(mocker,request):   
    gconf["base_test_directory"]                        =f"./data/testData/assignmentOrchestrator/check_assignment_submission/{request.node.name}"
    gconf["relative_data_directory"]                    =os.path.join(gconf["base_test_directory"],"data")
    gconf["assignment_data_file"]                       =os.path.join(gconf["relative_data_directory"],"assignment_data.json")
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

    mocker.patch("assignmentOrchestrator.DATA_FILE",                gconf["assignment_data_file"])
    mocker.patch("assignmentOrchestrator.SUBMITTED_FILES_DIR",      gconf["relative_submitted_files_directory"])
    mocker.patch("assignmentOrchestrator.ASSIGNMENT_VALIDATOR_DIR", gconf["relative_validators_directory"])
    mocker.patch("assignmentOrchestrator.ASSIGNMENT_MAPPER_FILE",   gconf["test_assignment_mapper_json_file_location"])
        

@patch('assignmentOrchestrator.execute_validator_on_task_file')
def test__single_validator_on_single_task_file__all_passed(patched_execute_validator_on_task_file,mocker__on_empty_data):
    patched_execute_validator_on_task_file.return_value={"status":"PASS"}
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py']}}
    os.makedirs(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1"),exist_ok=True)
    Path(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1",'task_1.py')).touch()
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    check_assignment_submission_output=check_assignment_submission(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py']))
    assert check_assignment_submission_output == {'collected_results': [{'status': 'PASS','task_idx': 1}],'status': 'PASS'}

@patch('assignmentOrchestrator.execute_validator_on_task_file')
def test__two_validator_on_two_task_file__all_passed(patched_execute_validator_on_task_file,mocker__on_empty_data):
    patched_execute_validator_on_task_file.return_value={"status":"PASS"}
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py','validate_assignment_1_task_2.py']}}
    os.makedirs(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1"),exist_ok=True)
    Path(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1",'task_1.py')).touch()
    Path(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1",'task_2.py')).touch()
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    check_assignment_submission_output=check_assignment_submission(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py','task_2.py']))
    assert check_assignment_submission_output == {'collected_results': [{'status': 'PASS','task_idx': 1},{'status': 'PASS','task_idx': 2}],'status': 'PASS'}

@patch('assignmentOrchestrator.execute_validator_on_task_file')
def test__two_validator_on_two_task_file__first_passed_second_failed(patched_execute_validator_on_task_file,mocker__on_empty_data):
    patched_execute_validator_on_task_file.side_effect=({"status":"PASS"},{"status":"FAIL","FAIL_message":"face it, your code is shit!"})
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py','validate_assignment_1_task_2.py']}}
    os.makedirs(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1"),exist_ok=True)
    Path(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1",'task_1.py')).touch()
    Path(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1",'task_2.py')).touch()
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    check_assignment_submission_output=check_assignment_submission(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py','task_2.py']))
    assert check_assignment_submission_output == {'collected_results': [{'status': 'PASS','task_idx': 1},{'FAIL_message': 'face it, your code is shit!','status': 'FAIL','task_idx': 2}],'status': 'FAIL'}#

@patch('assignmentOrchestrator.execute_validator_on_task_file')
def test__two_validator_on_two_task_file__first_failed_second_passed(patched_execute_validator_on_task_file,mocker__on_empty_data):
    patched_execute_validator_on_task_file.side_effect=({"status":"FAIL","FAIL_message":"face it, your code is shit!"},{"status":"PASS"})
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py','validate_assignment_1_task_2.py']}}
    os.makedirs(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1"),exist_ok=True)
    Path(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1",'task_1.py')).touch()
    Path(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1",'task_2.py')).touch()
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    check_assignment_submission_output=check_assignment_submission(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py','task_2.py']))
    assert check_assignment_submission_output == {'collected_results': [{'FAIL_message': 'face it, your code is shit!','status': 'FAIL','task_idx': 1},{'status': 'PASS','task_idx': 2}],'status': 'FAIL'}#

@patch('assignmentOrchestrator.execute_validator_on_task_file')
def test__three_validators_on_three_task_file___pass_fail_pass(patched_execute_validator_on_task_file,mocker__on_empty_data):
    patched_execute_validator_on_task_file.side_effect=({"status":"PASS"},{"status":"FAIL","FAIL_message":"face it, your code is shit!"},{"status":"PASS"})
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py','validate_assignment_1_task_2.py','validate_assignment_1_task_3.py']}}
    os.makedirs(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1"),exist_ok=True)
    Path(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1",'task_1.py')).touch()
    Path(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1",'task_2.py')).touch() 
    Path(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1",'task_3.py')).touch() 
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    check_assignment_submission_output=check_assignment_submission(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py','task_2.py','task_3.py']))
    assert check_assignment_submission_output == {'collected_results': [{'status': 'PASS','task_idx': 1},{'FAIL_message': 'face it, your code is shit!','status': 'FAIL','task_idx': 2},{'status': 'PASS','task_idx': 3}],'status': 'FAIL'}#

@patch('assignmentOrchestrator.execute_validator_on_task_file')
def test__three_validators_on_three_task_file__fail_pass_fail(patched_execute_validator_on_task_file,mocker__on_empty_data):
    patched_execute_validator_on_task_file.side_effect=({"status":"FAIL","FAIL_message":"face it, your code is shit!"},{"status":"PASS"},{"status":"FAIL","FAIL_message":"face it, your code is shit!"})
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py','validate_assignment_1_task_2.py','validate_assignment_1_task_3.py']}}
    os.makedirs(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1"),exist_ok=True)
    Path(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1",'task_1.py')).touch()
    Path(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1",'task_2.py')).touch() 
    Path(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1",'task_3.py')).touch() 
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    check_assignment_submission_output=check_assignment_submission(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py','task_2.py','task_3.py']))
    assert check_assignment_submission_output == {'collected_results': [{'FAIL_message': 'face it, your code is shit!','status': 'FAIL','task_idx': 1},{'status': 'PASS','task_idx': 2},{'FAIL_message': 'face it, your code is shit!','status': 'FAIL','task_idx': 3}],'status': 'FAIL'}#

@patch('assignmentOrchestrator.execute_validator_on_task_file')
def test__three_validators_on_three_task_file__pass_pass_fail(patched_execute_validator_on_task_file,mocker__on_empty_data):
    patched_execute_validator_on_task_file.side_effect=({"status":"PASS"},{"status":"PASS"},{"status":"FAIL","FAIL_message":"face it, your code is shit!"})
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py','validate_assignment_1_task_2.py','validate_assignment_1_task_3.py']}}
    os.makedirs(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1"),exist_ok=True)
    Path(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1",'task_1.py')).touch()
    Path(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1",'task_2.py')).touch() 
    Path(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1",'task_3.py')).touch() 
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    check_assignment_submission_output=check_assignment_submission(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py','task_2.py','task_3.py']))
    assert check_assignment_submission_output == {'collected_results': [{'status': 'PASS','task_idx': 1},{'status': 'PASS','task_idx': 2},{'FAIL_message': 'face it, your code is shit!','status': 'FAIL','task_idx': 3}],'status': 'FAIL'}#

@patch('assignmentOrchestrator.execute_validator_on_task_file')
def test__two_validator_on_one_task_file__error_no_task_when_task_passes(patched_execute_validator_on_task_file,mocker__on_empty_data):
    patched_execute_validator_on_task_file.return_value={"status":"PASS"}
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py','validate_assignment_1_task_2.py']}}
    os.makedirs(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1"),exist_ok=True)
    Path(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1",'task_1.py')).touch()
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    check_assignment_submission_output=check_assignment_submission(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py']))
    assert check_assignment_submission_output == {'collected_results': [{'status': 'PASS','task_idx': 1},{'ERROR_message': 'missing task (task_2.py) in assignment',  'status': 'ERROR','task_idx': 2, }],'status': 'ERROR'}#

@patch('assignmentOrchestrator.execute_validator_on_task_file')
def test__two_validator_on_one_task_file__error_no_task_when_task_fails(patched_execute_validator_on_task_file,mocker__on_empty_data):
    patched_execute_validator_on_task_file.return_value={"status":"FAIL"}
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py','validate_assignment_1_task_2.py']}}
    os.makedirs(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1"),exist_ok=True)
    Path(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1",'task_1.py')).touch()
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    check_assignment_submission_output=check_assignment_submission(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py']))
    assert check_assignment_submission_output == {'collected_results': [{'status': 'FAIL','task_idx': 1},{'ERROR_message': 'missing task (task_2.py) in assignment',  'status': 'ERROR','task_idx': 2, }],'status': 'ERROR'}#

