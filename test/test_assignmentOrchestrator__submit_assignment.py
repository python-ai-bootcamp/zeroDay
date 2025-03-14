import pytest, base64, os, shutil,json
from unittest.mock import patch, mock_open
from assignmentOrchestrator import load_data, AssignmentSubmission, save_data, submit_assignment

gconf={}

@pytest.fixture
def mocker__on_empty_data(mocker,request):   
    gconf["base_test_directory"]                        =f"./data/testData/assignmentOrchestrator/submit_assignment/{request.node.name}"
    gconf["relative_data_directory"]                    =os.path.join(gconf["base_test_directory"],"data")
    gconf["assignment_data_file_directory"]             =os.path.join(gconf["relative_data_directory"],"assignment_data")
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

    mocker.patch("assignmentOrchestrator.SUBMITTED_FILES_DIR",      gconf["relative_submitted_files_directory"])
    mocker.patch("assignmentOrchestrator.ASSIGNMENT_VALIDATOR_DIR", gconf["relative_validators_directory"])
    mocker.patch("assignmentOrchestrator.ASSIGNMENT_MAPPER_FILE",   gconf["test_assignment_mapper_json_file_location"])
    mocker.patch("assignmentOrchestrator.DATA_FILE_DIRECTORY",      gconf["assignment_data_file_directory"])


@patch("assignmentOrchestrator.check_assignment_submission")
def test__when_first_assignment_passes_on_first_submission(patched_function, mocker__on_empty_data):
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py']}}
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    patched_function.return_value={"status":"PASS"}
    submission_assignment_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert submission_assignment_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 1, 'assignment_files': [base64.b64encode("fakeScriptData".encode('ascii')).decode("utf-8")], 'submission_id': 1, 'result': {"status":"PASS"},'assignment_file_names': ['task_1.py']}
    assignment_submissions_json=load_data()
    assert assignment_submissions_json == {"nonExistingUser":{"1":[submission_assignment_output]}}
@patch("assignmentOrchestrator.check_assignment_submission")
def test__when_first_assignment_passes_on_second_submission(patched_function,mocker__on_empty_data):
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py']}}
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    patched_function.return_value={"status":"FAIL"}
    submission_assignment_output_1=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert submission_assignment_output_1 == {'hacker_id': 'nonExistingUser', 'assignment_id': 1, 'assignment_files': [base64.b64encode("fakeScriptData".encode('ascii')).decode("utf-8")], 'submission_id': 1, 'result': {"status":"FAIL"},'assignment_file_names': ['task_1.py']}
    patched_function.return_value={"status":"PASS"}
    submission_assignment_output_2=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert submission_assignment_output_2 == {'hacker_id': 'nonExistingUser', 'assignment_id': 1, 'assignment_files': [base64.b64encode("fakeScriptData".encode('ascii')).decode("utf-8")], 'submission_id': 2, 'result': {"status":"PASS"},'assignment_file_names': ['task_1.py']}
    assignment_submissions_json=load_data()
    assert assignment_submissions_json == {"nonExistingUser":{"1":[submission_assignment_output_1,submission_assignment_output_2]}}
@patch("assignmentOrchestrator.check_assignment_submission")
def test__when_second_assignment_submission_cannot_be_checked_without_first_assignment_submitted(patched_function, mocker__on_empty_data):
    test_assignment_mapper_json_file_data={'2': {'description': 'description_2.md', 'validators': ['validate_assignment_2_task_1.py']}}
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)    
    patched_function.return_value={"status":"PASS"}
    submission_assignment_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=2,assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert submission_assignment_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 2, 'submission_id': None, 'assignment_files': [base64.b64encode("fakeScriptData".encode('ascii')).decode("utf-8")], 'result':{"status": "ERROR", 'ERROR_message': "cannot test assignment (assignment_id=2) until previous assignment (assignment_id=1) passes successfully"},'assignment_file_names': None}
    assignment_submissions_json=load_data()
    assert assignment_submissions_json == {}
@patch("assignmentOrchestrator.check_assignment_submission")
def test__when_third_assignment_submission_cannot_be_checked_without_second_assignment_submitted(patched_function, mocker__on_empty_data):
    test_assignment_mapper_json_file_data={
        '1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py']},
        '3': {'description': 'description_3.md', 'validators': ['validate_assignment_3_task_1.py']}
    }
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)   
    patched_function.return_value={"status":"PASS"}
    submission_assignment_1_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert submission_assignment_1_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 1, 'assignment_files': [base64.b64encode("fakeScriptData".encode('ascii')).decode("utf-8")], 'submission_id': 1, 'result': {"status":"PASS"},'assignment_file_names': ['task_1.py']}
    submission_assignment_3_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=3,assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert submission_assignment_3_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 3, 'submission_id': None, 'assignment_files': [base64.b64encode("fakeScriptData".encode('ascii')).decode("utf-8")], 'result':{"status": "ERROR", 'ERROR_message': "cannot test assignment (assignment_id=3) until previous assignment (assignment_id=2) passes successfully"},'assignment_file_names': None}
    assignment_submissions_json=load_data()
    assert assignment_submissions_json == {"nonExistingUser":{"1":[submission_assignment_1_output]}}

@patch("assignmentOrchestrator.check_assignment_submission")
def test__when_third_assignment_submission_cant_check_without_second_assignment_submitted_and_passed(patched_function, mocker__on_empty_data):
    test_assignment_mapper_json_file_data={
        '1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py']},
        '2': {'description': 'description_2.md', 'validators': ['validate_assignment_2_task_1.py']},
        '3': {'description': 'description_3.md', 'validators': ['validate_assignment_3_task_1.py']}
    }
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)   
    patched_function.return_value={"status":"PASS"}
    submission_assignment_1_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert submission_assignment_1_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 1, 'assignment_files': [base64.b64encode("fakeScriptData".encode('ascii')).decode("utf-8")], 'submission_id': 1, 'result': {"status":"PASS"},'assignment_file_names': ['task_1.py']}
    patched_function.return_value={"status":"FAIL"}
    submission_assignment_2_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=2,assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert submission_assignment_2_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 2, 'assignment_files': [base64.b64encode("fakeScriptData".encode('ascii')).decode("utf-8")], 'submission_id': 1, 'result': {"status":"FAIL"},'assignment_file_names': ['task_1.py']}
    patched_function.return_value={"status":"PASS"}
    submission_assignment_3_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=3,assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert submission_assignment_3_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 3, 'submission_id': None, 'assignment_files': [base64.b64encode("fakeScriptData".encode('ascii')).decode("utf-8")], 'result':{"status": "ERROR", 'ERROR_message': "cannot test assignment (assignment_id=3) until previous assignment (assignment_id=2) passes successfully"},'assignment_file_names': None}
    assignment_submissions_json=load_data()
    assert assignment_submissions_json == {"nonExistingUser":{"1":[submission_assignment_1_output],"2":[submission_assignment_2_output]}}

@patch("assignmentOrchestrator.check_assignment_submission")
def test__when_second_assignment_passes_on_first_submission_after_first_assignment_already_passed(patched_function, mocker__on_empty_data):
    test_assignment_mapper_json_file_data={
        '1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py']},
        '2': {'description': 'description_2.md', 'validators': ['validate_assignment_2_task_1.py']}
    }
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)   
    patched_function.return_value={"status":"PASS"}
    submission_assignment_1_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert submission_assignment_1_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 1, 'assignment_files': [base64.b64encode("fakeScriptData".encode('ascii')).decode("utf-8")], 'submission_id': 1, 'result': {"status":"PASS"},'assignment_file_names': ['task_1.py']}
    patched_function.return_value={"status":"PASS"}
    submission_assignment_2_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=2,assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert submission_assignment_2_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 2, 'assignment_files': [base64.b64encode("fakeScriptData".encode('ascii')).decode("utf-8")], 'submission_id': 1, 'result': {"status":"PASS"},'assignment_file_names': ['task_1.py']}
    assignment_submissions_json=load_data()
    assert assignment_submissions_json == {"nonExistingUser":{"1":[submission_assignment_1_output],"2":[submission_assignment_2_output]}}

@patch("assignmentOrchestrator.check_assignment_submission")
def test__when_third_assignment_submission_attempt_fails_and_forth_breaches_default_submission_limit(patched_function, mocker__on_empty_data):
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py']}}
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)   
    patched_function.return_value={"status":"FAIL"}
    submission_1_assignment_1_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert submission_1_assignment_1_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 1, 'assignment_files': [base64.b64encode("fakeScriptData".encode('ascii')).decode("utf-8")], 'submission_id': 1, 'result': {"status":"FAIL"},'assignment_file_names': ['task_1.py']}
    submission_2_assignment_1_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert submission_2_assignment_1_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 1, 'assignment_files': [base64.b64encode("fakeScriptData".encode('ascii')).decode("utf-8")], 'submission_id': 2, 'result': {"status":"FAIL"},'assignment_file_names': ['task_1.py']}
    submission_3_assignment_1_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert submission_3_assignment_1_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 1, 'assignment_files': [base64.b64encode("fakeScriptData".encode('ascii')).decode("utf-8")], 'submission_id': 3, 'result': {"status":"FAIL"},'assignment_file_names': ['task_1.py']}
    submission_4_assignment_1_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert submission_4_assignment_1_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 1, 'assignment_files': [base64.b64encode("fakeScriptData".encode('ascii')).decode("utf-8")], 'submission_id': 4, 'result': {"status":"ERROR","ERROR_message":"cannot test assignment (assignment_id=1) because submission attempts (4) passed the allowed max_submissions (max_submissions=3)"},'assignment_file_names': None}
    assignment_submissions_json=load_data()
    assert assignment_submissions_json == {"nonExistingUser":{"1":[submission_1_assignment_1_output,submission_2_assignment_1_output,submission_3_assignment_1_output]}}

@patch("assignmentOrchestrator.check_assignment_submission")
def test__when_third_second_submission_attempt_fails_and_third_breaches_custom_submission_limit(patched_function, mocker__on_empty_data):
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py'],"max_submissions":2}}
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)   
    patched_function.return_value={"status":"FAIL"}
    submission_1_assignment_1_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert submission_1_assignment_1_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 1, 'assignment_files': [base64.b64encode("fakeScriptData".encode('ascii')).decode("utf-8")], 'submission_id': 1, 'result': {"status":"FAIL"},'assignment_file_names': ['task_1.py']}
    submission_2_assignment_1_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert submission_2_assignment_1_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 1, 'assignment_files': [base64.b64encode("fakeScriptData".encode('ascii')).decode("utf-8")], 'submission_id': 2, 'result': {"status":"FAIL"},'assignment_file_names': ['task_1.py']}
    submission_3_assignment_1_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert submission_3_assignment_1_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 1, 'assignment_files': [base64.b64encode("fakeScriptData".encode('ascii')).decode("utf-8")], 'submission_id': 3, 'result': {"status":"ERROR","ERROR_message":"cannot test assignment (assignment_id=1) because submission attempts (3) passed the allowed max_submissions (max_submissions=2)"},'assignment_file_names': None}
    assignment_submissions_json=load_data()
    assert assignment_submissions_json == {"nonExistingUser":{"1":[submission_1_assignment_1_output,submission_2_assignment_1_output]}}


def test__missing_assignment_id_entry_in_assignement_mapper(mocker__on_empty_data):
    test_assignment_mapper_json_file_data={'2': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py'],"max_submissions":2}}
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)   
    submission_1_assignment_1_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert submission_1_assignment_1_output == {'status': 'ERROR', 'ERROR_message': "missing assignment_id=1 in assignment_mapper file"}


def test__missing_validators_entry_in_assignment_id_entry_in_assignement_mapper(mocker__on_empty_data):
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md'}}
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)   
    submission_1_assignment_1_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert submission_1_assignment_1_output == {'status': 'ERROR', 'ERROR_message': "missing validators entry for assignment_id=1 in assignment_mapper file"}


def test__zero_validations_exist_in_assignement_mapper_for_assignment_id(mocker__on_empty_data):
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': []}}
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)   
    submission_1_assignment_1_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert submission_1_assignment_1_output == {'status': 'ERROR', 'ERROR_message': "no validators mapped for assignment_id=1 in assignment_mapper file"}
