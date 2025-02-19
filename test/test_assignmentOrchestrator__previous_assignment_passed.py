import pytest
from unittest.mock import patch, mock_open
from assignmentOrchestrator import load_data, assignment_passed, previous_assignment_passed, AssignmentSubmission, save_data, submit_assignment

def test_previous_assignment_passed___when_no_hacker_id_exists_and_not_first_assignment_id():
    tested_input={
        "data":{"existingId_1":{},"existingId_2":{}},
        "assignment_submission":AssignmentSubmission(hacker_id="nonExistingId",assignment_id=2,assignment_files=["myTask.tar.gz"])
    }
    assert previous_assignment_passed(**tested_input) == False
def test_previous_assignment_passed___when_no_hacker_id_exists_and_first_assignment_id():
    tested_input={
        "data":{"existingId_1":{},"existingId_2":{}},
        "assignment_submission":AssignmentSubmission(hacker_id="nonExistingId",assignment_id=1,assignment_files=["myTask.tar.gz"])
    }
    assert previous_assignment_passed(**tested_input) == True
def test_previous_assignment_passed___when_no_hacker_id_exists_in_empty_data_file_and_not_first_assignment_id():
    tested_input={
        "data":{},
        "assignment_submission":AssignmentSubmission(hacker_id="nonExistingId",assignment_id=2,assignment_files=["myTask.tar.gz"])
    }
    assert previous_assignment_passed(**tested_input) == False
def test_previous_assignment_passed___when_no_hacker_id_exists_in_empty_data_file_and_first_assignment_id():
    tested_input={
        "data":{},
        "assignment_submission":AssignmentSubmission(hacker_id="nonExistingId",assignment_id=1,assignment_files=["myTask.tar.gz"])
    }
    assert previous_assignment_passed(**tested_input) == True
def test_previous_assignment_passed___when_hacker_id_exists_and_first_assignment_id():
    tested_input={
        "data":{"existingId_1":{},"existingId_2":{}},
        "assignment_submission":AssignmentSubmission(hacker_id="existingId_1",assignment_id=1,assignment_files=["myTask.tar.gz"])
    }
    assert previous_assignment_passed(**tested_input) == True
def test_previous_assignment_passed___when_hacker_id_exists_and_previous_assignment_failed():
    tested_input={
        "data":{"existingId_1":{"1":[{"result":"FAIL"},{"result":"FAIL"},{"result":"FAIL"}]},"existingId_2":{}},
        "assignment_submission":AssignmentSubmission(hacker_id="existingId_1",assignment_id=2,assignment_files=["myTask.tar.gz"])
    }
    assert previous_assignment_passed(**tested_input) == False
def test_previous_assignment_passed___when_hacker_id_exists_and_previous_assignment_passed():
    tested_input={
        "data":{"existingId_1":{"1":[{"result":"FAIL"},{"result":"FAIL"},{"result":"PASS"}]},"existingId_2":{}},
        "assignment_submission":AssignmentSubmission(hacker_id="existingId_1",assignment_id=2,assignment_files=["myTask.tar.gz"])
    }
    assert previous_assignment_passed(**tested_input) == True
def test_previous_assignment_passed___when_hacker_id_exists_and_previous_assignment_does_not_exist():
    tested_input={
        "data":{"existingId_1":{"1":[{"result":"FAIL"},{"result":"FAIL"},{"result":"PASS"}]},"existingId_2":{}},
        "assignment_submission":AssignmentSubmission(hacker_id="existingId_1",assignment_id=3,assignment_files=["myTask.tar.gz"])
    }
    assert previous_assignment_passed(**tested_input) == False