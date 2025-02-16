import pytest
from unittest.mock import patch, mock_open
from assignmentOrchestrator import load_data, assignment_passed, previous_assignment_passed, AssignmentSubmission

@patch('os.path.exists')
def test_load_data_on_non_existing_file(mock_input):
    mock_input.return_value=False
    assert load_data() == {}

@pytest.fixture
def mocker_test_load_data_on_existing_file(mocker):
    existing_data = mocker.mock_open(read_data='{"a":2}')
    mocker.patch("builtins.open", existing_data)
    mocker.patch('os.path.exists', return_value=True)
def test_load_data_on_existing_file(mocker_test_load_data_on_existing_file):
    assert load_data() == {"a":2}


def test_assignment_passed_when_no_previous_submissions_exist():
    assert assignment_passed([]) == False
def test_assignment_passed_when_only_FAIL_results_exist():
    assert assignment_passed([{"result":"FAIL"},{"result":"FAIL"},{"result":"FAIL"},{"result":"FAIL"}]) == False
def test_assignment_passed_when_only_single_FAIL_results_exist():
    assert assignment_passed([{"result":"FAIL"}]) == False
def test_assignment_passed_when_only_PASS_results_exist():
    assert assignment_passed([{"result":"PASS"},{"result":"PASS"},{"result":"PASS"},{"result":"PASS"}]) == True
def test_assignment_passed_when_only_single_PASS_results_exist():
    assert assignment_passed([{"result":"PASS"}]) == True
def test_assignment_passed_when_at_least_single_PASS_results_exist():
    assert assignment_passed([{"result":"FAIL"},{"result":"FAIL"},{"result":"FAIL"},{"result":"PASS"}]) == True
    assert assignment_passed([{"result":"PASS"},{"result":"FAIL"},{"result":"FAIL"},{"result":"FAIL"}]) == True
    assert assignment_passed([{"result":"FAIL"},{"result":"PASS"},{"result":"FAIL"},{"result":"PASS"}]) == True
    assert assignment_passed([{"result":"PASS"},{"result":"PASS"},{"result":"FAIL"},{"result":"FAIL"}]) == True
    assert assignment_passed([{"result":"FAIL"},{"result":"PASS"},{"result":"PASS"},{"result":"FAIL"}]) == True




def test_previous_assignment_passed_when_no_hacker_id_exists_and_not_first_assignment_id():
    tested_input={
        "data":{"existingId_1":{},"existingId_2":{}},
        "assignment_submission":AssignmentSubmission(hacker_id="nonExistingId",assignment_id=2,assignment_file="myTask.tar.gz")
    }
    assert previous_assignment_passed(**tested_input) == False
def test_previous_assignment_passed_when_no_hacker_id_exists_and_first_assignment_id():
    tested_input={
        "data":{"existingId_1":{},"existingId_2":{}},
        "assignment_submission":AssignmentSubmission(hacker_id="nonExistingId",assignment_id=1,assignment_file="myTask.tar.gz")
    }
    assert previous_assignment_passed(**tested_input) == True
def test_previous_assignment_passed_when_no_hacker_id_exists_in_empty_data_file_and_not_first_assignment_id():
    tested_input={
        "data":{},
        "assignment_submission":AssignmentSubmission(hacker_id="nonExistingId",assignment_id=2,assignment_file="myTask.tar.gz")
    }
    assert previous_assignment_passed(**tested_input) == False
def test_previous_assignment_passed_when_no_hacker_id_exists_in_empty_data_file_and_first_assignment_id():
    tested_input={
        "data":{},
        "assignment_submission":AssignmentSubmission(hacker_id="nonExistingId",assignment_id=1,assignment_file="myTask.tar.gz")
    }
    assert previous_assignment_passed(**tested_input) == True

def test_previous_assignment_passed_when_hacker_id_exists_and_first_assignment_id():
    tested_input={
        "data":{"existingId_1":{},"existingId_2":{}},
        "assignment_submission":AssignmentSubmission(hacker_id="existingId_1",assignment_id=1,assignment_file="myTask.tar.gz")
    }
    assert previous_assignment_passed(**tested_input) == True

def test_previous_assignment_passed_when_hacker_id_exists_and_previous_assignment_failed():
    tested_input={
        "data":{"existingId_1":{"1":[{"result":"FAIL"},{"result":"FAIL"},{"result":"FAIL"}]},"existingId_2":{}},
        "assignment_submission":AssignmentSubmission(hacker_id="existingId_1",assignment_id=2,assignment_file="myTask.tar.gz")
    }
    assert previous_assignment_passed(**tested_input) == False
def test_previous_assignment_passed_when_hacker_id_exists_and_previous_assignment_failed():
    tested_input={
        "data":{"existingId_1":{"1":[{"result":"FAIL"},{"result":"FAIL"},{"result":"PASS"}]},"existingId_2":{}},
        "assignment_submission":AssignmentSubmission(hacker_id="existingId_1",assignment_id=2,assignment_file="myTask.tar.gz")
    }
    assert previous_assignment_passed(**tested_input) == True
    