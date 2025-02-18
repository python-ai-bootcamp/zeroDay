import pytest
from unittest.mock import patch, mock_open
from assignmentOrchestrator import load_data, assignment_passed, previous_assignment_passed, AssignmentSubmission, save_data, submit_assignment

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
def test_submit_assignment___when_first_assignment_passes_on_second_submission(patched_function,mocker_test_submit_assignment___on_empty_data):
    patched_function.return_value="FAIL"
    submission_assignment_output_1=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",assignment_file="bla.tar.gz"))
    assert submission_assignment_output_1 == {'hacker_id': 'nonExistingUser', 'assignment_id': 1, 'assignment_file': 'bla.tar.gz', 'submission_id': 1, 'result': "FAIL"}
    patched_function.return_value="PASS"
    submission_assignment_output_2=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",assignment_file="bla.tar.gz"))
    assert submission_assignment_output_2 == {'hacker_id': 'nonExistingUser', 'assignment_id': 1, 'assignment_file': 'bla.tar.gz', 'submission_id': 2, 'result': "PASS"}
    assignment_submissions_json=load_data()
    assert assignment_submissions_json == {"nonExistingUser":{"1":[submission_assignment_output_1,submission_assignment_output_2]}}
@patch("assignmentOrchestrator.check_assignment_submission")
def test_submit_assignment___on_empty_data_when_second_assignment_submission_cannot_be_checked_without_first_assignment_submitted(patched_function, mocker_test_submit_assignment___on_empty_data):
    patched_function.return_value="PASS"
    submission_assignment_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="2",assignment_file="bla.tar.gz"))
    assert submission_assignment_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 2, 'assignment_file': 'bla.tar.gz', 'result': 'ERROR', 'ERROR_message': "cannot test assignment (assignment_id=2) until previous assignment (assignment_id=1) passes successfully"}
    assignment_submissions_json=load_data()
    assert assignment_submissions_json == {}
@patch("assignmentOrchestrator.check_assignment_submission")
def test_submit_assignment___on_empty_data_when_third_assignment_submission_cannot_be_checked_without_second_assignment_submitted(patched_function, mocker_test_submit_assignment___on_empty_data):
    patched_function.return_value="PASS"
    submission_assignment_1_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",assignment_file="bla.tar.gz"))
    assert submission_assignment_1_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 1, 'assignment_file': 'bla.tar.gz', 'submission_id': 1, 'result': 'PASS'}
    submission_assignment_3_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="3",assignment_file="bla.tar.gz"))
    assert submission_assignment_3_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 3, 'assignment_file': 'bla.tar.gz', 'result': 'ERROR', 'ERROR_message': "cannot test assignment (assignment_id=3) until previous assignment (assignment_id=2) passes successfully"}
    assignment_submissions_json=load_data()
    assert assignment_submissions_json == {"nonExistingUser":{"1":[submission_assignment_1_output]}}

@patch("assignmentOrchestrator.check_assignment_submission")
def test_submit_assignment___on_empty_data_when_third_assignment_submission_cannot_be_checked_without_second_assignment_submitted_and_passed(patched_function, mocker_test_submit_assignment___on_empty_data):
    patched_function.return_value="PASS"
    submission_assignment_1_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",assignment_file="bla.tar.gz"))
    assert submission_assignment_1_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 1, 'assignment_file': 'bla.tar.gz', 'submission_id': 1, 'result': 'PASS'}
    patched_function.return_value="FAIL"
    submission_assignment_2_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="2",assignment_file="bla.tar.gz"))
    assert submission_assignment_2_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 2, 'assignment_file': 'bla.tar.gz', 'submission_id': 1, 'result': 'FAIL'}
    patched_function.return_value="PASS"
    submission_assignment_3_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="3",assignment_file="bla.tar.gz"))
    assert submission_assignment_3_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 3, 'assignment_file': 'bla.tar.gz', 'result': 'ERROR', 'ERROR_message': "cannot test assignment (assignment_id=3) until previous assignment (assignment_id=2) passes successfully"}
    assignment_submissions_json=load_data()
    assert assignment_submissions_json == {"nonExistingUser":{"1":[submission_assignment_1_output],"2":[submission_assignment_2_output]}}

@patch("assignmentOrchestrator.check_assignment_submission")
def test_submit_assignment___when_second_assignment_passes_on_first_submission_after_first_assignment_already_passed(patched_function, mocker_test_submit_assignment___on_empty_data):
    patched_function.return_value="PASS"
    submission_assignment_1_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",assignment_file="bla.tar.gz"))
    assert submission_assignment_1_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 1, 'assignment_file': 'bla.tar.gz', 'submission_id': 1, 'result': "PASS"}
    patched_function.return_value="PASS"
    submission_assignment_2_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="2",assignment_file="bla.tar.gz"))
    assert submission_assignment_2_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 2, 'assignment_file': 'bla.tar.gz', 'submission_id': 1, 'result': "PASS"}
    assignment_submissions_json=load_data()
    assert assignment_submissions_json == {"nonExistingUser":{"1":[submission_assignment_1_output],"2":[submission_assignment_2_output]}}
