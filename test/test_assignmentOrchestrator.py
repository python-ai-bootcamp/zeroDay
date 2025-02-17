import pytest
from unittest.mock import patch, mock_open
from assignmentOrchestrator import load_data, assignment_passed, previous_assignment_passed, AssignmentSubmission, save_data, submit_assignment

@patch('os.path.exists')
def test_load_data_on_non_existing_file(mock_input):
    mock_input.return_value=False
    assert load_data() == {}

@pytest.fixture
def mocker_test_load_data___on_existing_file(mocker):
    existing_data = mocker.mock_open(read_data='{"a":2}')
    mocker.patch("builtins.open", existing_data)
    mocker.patch('os.path.exists', return_value=True)
def test_load_data___on_existing_file(mocker_test_load_data___on_existing_file):
    assert load_data() == {"a":2}


def test_assignment_passed___when_no_previous_submissions_exist():
    assert assignment_passed([]) == False
def test_assignment_passed___when_only_FAIL_results_exist():
    assert assignment_passed([{"result":"FAIL"},{"result":"FAIL"},{"result":"FAIL"},{"result":"FAIL"}]) == False
def test_assignment_passed___when_only_single_FAIL_results_exist():
    assert assignment_passed([{"result":"FAIL"}]) == False
def test_assignment_passed___when_only_PASS_results_exist():
    assert assignment_passed([{"result":"PASS"},{"result":"PASS"},{"result":"PASS"},{"result":"PASS"}]) == True
def test_assignment_passed___when_only_single_PASS_results_exist():
    assert assignment_passed([{"result":"PASS"}]) == True
def test_assignment_passed___when_at_least_single_PASS_results_exist():
    assert assignment_passed([{"result":"FAIL"},{"result":"FAIL"},{"result":"FAIL"},{"result":"PASS"}]) == True
    assert assignment_passed([{"result":"PASS"},{"result":"FAIL"},{"result":"FAIL"},{"result":"FAIL"}]) == True
    assert assignment_passed([{"result":"FAIL"},{"result":"PASS"},{"result":"FAIL"},{"result":"PASS"}]) == True
    assert assignment_passed([{"result":"PASS"},{"result":"PASS"},{"result":"FAIL"},{"result":"FAIL"}]) == True
    assert assignment_passed([{"result":"FAIL"},{"result":"PASS"},{"result":"PASS"},{"result":"FAIL"}]) == True




def test_previous_assignment_passed___when_no_hacker_id_exists_and_not_first_assignment_id():
    tested_input={
        "data":{"existingId_1":{},"existingId_2":{}},
        "assignment_submission":AssignmentSubmission(hacker_id="nonExistingId",assignment_id=2,assignment_file="myTask.tar.gz")
    }
    assert previous_assignment_passed(**tested_input) == False
def test_previous_assignment_passed___when_no_hacker_id_exists_and_first_assignment_id():
    tested_input={
        "data":{"existingId_1":{},"existingId_2":{}},
        "assignment_submission":AssignmentSubmission(hacker_id="nonExistingId",assignment_id=1,assignment_file="myTask.tar.gz")
    }
    assert previous_assignment_passed(**tested_input) == True
def test_previous_assignment_passed___when_no_hacker_id_exists_in_empty_data_file_and_not_first_assignment_id():
    tested_input={
        "data":{},
        "assignment_submission":AssignmentSubmission(hacker_id="nonExistingId",assignment_id=2,assignment_file="myTask.tar.gz")
    }
    assert previous_assignment_passed(**tested_input) == False
def test_previous_assignment_passed___when_no_hacker_id_exists_in_empty_data_file_and_first_assignment_id():
    tested_input={
        "data":{},
        "assignment_submission":AssignmentSubmission(hacker_id="nonExistingId",assignment_id=1,assignment_file="myTask.tar.gz")
    }
    assert previous_assignment_passed(**tested_input) == True
def test_previous_assignment_passed___when_hacker_id_exists_and_first_assignment_id():
    tested_input={
        "data":{"existingId_1":{},"existingId_2":{}},
        "assignment_submission":AssignmentSubmission(hacker_id="existingId_1",assignment_id=1,assignment_file="myTask.tar.gz")
    }
    assert previous_assignment_passed(**tested_input) == True
def test_previous_assignment_passed___when_hacker_id_exists_and_previous_assignment_failed():
    tested_input={
        "data":{"existingId_1":{"1":[{"result":"FAIL"},{"result":"FAIL"},{"result":"FAIL"}]},"existingId_2":{}},
        "assignment_submission":AssignmentSubmission(hacker_id="existingId_1",assignment_id=2,assignment_file="myTask.tar.gz")
    }
    assert previous_assignment_passed(**tested_input) == False
def test_previous_assignment_passed___when_hacker_id_exists_and_previous_assignment_failed():
    tested_input={
        "data":{"existingId_1":{"1":[{"result":"FAIL"},{"result":"FAIL"},{"result":"PASS"}]},"existingId_2":{}},
        "assignment_submission":AssignmentSubmission(hacker_id="existingId_1",assignment_id=2,assignment_file="myTask.tar.gz")
    }
    assert previous_assignment_passed(**tested_input) == True

@pytest.fixture
def mocker_test_submit_assignment___on_empty_data(mocker):
    save_data({})
@patch("assignmentOrchestrator.check_assignment_submission")
def test_submit_assignment___on_empty_data_when_first_assignment_passes_on_first_submission(patched_function, mocker_test_submit_assignment___on_empty_data):
    patched_function.return_value="PASS"
    submission_assignment_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",assignment_file="bla.tar.gz"))
    assert submission_assignment_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 1, 'assignment_file': 'bla.tar.gz', 'submission_id': 1, 'result': 'PASS'}
    assignment_submissions_json=load_data()
    assert assignment_submissions_json == {"nonExistingUser":{"1":[submission_assignment_output]}}
@patch("assignmentOrchestrator.check_assignment_submission")
def test_submit_assignment___on_empty_data_when_first_assignment_passes_on_second_submission(patched_function,mocker_test_submit_assignment___on_empty_data):
    patched_function.return_value="FAIL"
    submission_assignment_output_1=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",assignment_file="bla.tar.gz"))
    assert submission_assignment_output_1 == {'hacker_id': 'nonExistingUser', 'assignment_id': 1, 'assignment_file': 'bla.tar.gz', 'submission_id': 1, 'result': "FAIL"}
    patched_function.return_value="PASS"
    submission_assignment_output_2=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",assignment_file="bla.tar.gz"))
    assert submission_assignment_output_2 == {'hacker_id': 'nonExistingUser', 'assignment_id': 1, 'assignment_file': 'bla.tar.gz', 'submission_id': 2, 'result': "PASS"}
    assignment_submissions_json=load_data()
    assert assignment_submissions_json == {"nonExistingUser":{"1":[submission_assignment_output_1,submission_assignment_output_2]}}
@patch("assignmentOrchestrator.check_assignment_submission")
def test_submit_assignment___on_empty_data_when_second_assignment_submission_passes(patched_function, mocker_test_submit_assignment___on_empty_data):
    patched_function.return_value="PASS"
    submission_assignment_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="2",assignment_file="bla.tar.gz"))
    assert submission_assignment_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 2, 'assignment_file': 'bla.tar.gz', 'submission_id': 1, 'result': 'ERROR', 'ERROR_message': "cannot test assignment (assignment_id=2) until previous assignment (assignment_id=1) passes successfully"}
    assignment_submissions_json=load_data()
    assert assignment_submissions_json == {}
