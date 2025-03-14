import pytest
from unittest.mock import patch, mock_open
from assignmentOrchestrator import next_assignment_submission

@patch('assignmentOrchestrator.load_data')
def test_on_empty_file(patched_load_data):
    patched_load_data.return_value={}
    assert next_assignment_submission("non_existing_hacker_id") == {"status": "ERROR", "ERROR_message":f"hacker_id:'non_existing_hacker_id' does not exist"}

@patch('assignmentOrchestrator.load_data')
def test_on_file_with_relevant_hacker_id_and_no_previous_assignments(patched_load_data):
    patched_load_data.return_value={"existing_hacker_id":{}}
    assert next_assignment_submission("existing_hacker_id") == {"assignment_id":1,"submission_id":1}

@patch('assignmentOrchestrator.load_data')
def test_on_file_with_non_relevant_hacker_id_and_no_previous_assignments(patched_load_data):
    patched_load_data.return_value={"existing_hacker_id":{}}
    assert next_assignment_submission("non_existing_hacker_id") == {"status": "ERROR", "ERROR_message":f"hacker_id:'non_existing_hacker_id' does not exist"}

@patch('assignmentOrchestrator.load_data')
def test_on_file_with_existing_assignment_without_submissions(patched_load_data):
    patched_load_data.return_value={"existing_hacker_id":{"1":[]}}
    assert next_assignment_submission("existing_hacker_id") == {'assignment_id': 1, 'submission_id': 1}

@patch('assignmentOrchestrator.load_data')
def test_on_file_with_existing_assignment_with_single_passed_submission(patched_load_data):
    patched_load_data.return_value={"existing_hacker_id":{"1":[{"result":{"status":"PASS"}}]}}
    assert next_assignment_submission("existing_hacker_id") == {'assignment_id': 2, 'submission_id': 1}

@patch('assignmentOrchestrator.load_data')
def test_on_file_with_existing_assignment_with_single_failed_submission(patched_load_data):
    patched_load_data.return_value={"existing_hacker_id":{"1":[{"result":{"status":"FAIL"}}]}}
    assert next_assignment_submission("existing_hacker_id") == {'assignment_id': 1, 'submission_id': 2}

@patch('assignmentOrchestrator.load_data')
def test_on_file_with_existing_assignment_with_two_passing_submissions(patched_load_data):
    patched_load_data.return_value={"existing_hacker_id":{"1":[{"result":{"status":"PASS"}},{"result":{"status":"PASS"}}]}}
    assert next_assignment_submission("existing_hacker_id") == {'assignment_id': 2, 'submission_id': 1}

@patch('assignmentOrchestrator.load_data')
def test_on_file_with_existing_assignment_with_two_failing_submissions(patched_load_data):
    patched_load_data.return_value={"existing_hacker_id":{"1":[{"result":{"status":"FAIL"}},{"result":{"status":"FAIL"}}]}}
    assert next_assignment_submission("existing_hacker_id") == {'assignment_id': 1, 'submission_id': 3}

@patch('assignmentOrchestrator.load_data')
def test_on_file_with_existing_assignment_with_second_submission_passed(patched_load_data):
    patched_load_data.return_value={"existing_hacker_id":{"1":[{"result":{"status":"FAIL"}},{"result":{"status":"PASS"}}]}}
    assert next_assignment_submission("existing_hacker_id") == {'assignment_id': 2, 'submission_id': 1}

@patch('assignmentOrchestrator.load_data')
def test_on_file_with_two_assignments_with_first_assignment_passed_and_second_assignment_without_submissions(patched_load_data):
    patched_load_data.return_value={"existing_hacker_id":{
        "1":[{"result":{"status":"FAIL"}},{"result":{"status":"PASS"}}],
        "2":[]
    }}
    assert next_assignment_submission("existing_hacker_id") == {'assignment_id': 2, 'submission_id': 1}

@patch('assignmentOrchestrator.load_data')
def test_on_file_with_two_assignments_with_first_assignment_passed_and_second_assignment_with_single_passed_submissions(patched_load_data):
    patched_load_data.return_value={"existing_hacker_id":{
        "1":[{"result":{"status":"FAIL"}},{"result":{"status":"PASS"}}],
        "2":[{"result":{"status":"PASS"}}]
    }}
    assert next_assignment_submission("existing_hacker_id") == {'assignment_id': 3, 'submission_id': 1}

@patch('assignmentOrchestrator.load_data')
def test_on_file_with_two_assignments_with_first_assignment_passed_and_second_assignment_with_single_failed_submissions(patched_load_data):
    patched_load_data.return_value={"existing_hacker_id":{
        "1":[{"result":{"status":"FAIL"}},{"result":{"status":"PASS"}}],
        "2":[{"result":{"status":"FAIL"}}]
    }}
    assert next_assignment_submission("existing_hacker_id") == {'assignment_id': 2, 'submission_id': 2}


