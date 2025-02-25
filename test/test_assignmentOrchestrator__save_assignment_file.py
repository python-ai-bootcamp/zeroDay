import pytest
from unittest.mock import patch, mock_open
from assignmentOrchestrator import load_data, AssignmentSubmission, save_data, submit_assignment

#@pytest.fixture
#def mocker_test_submit_assignment___on_empty_data(mocker):
#    save_data({})
#@patch("assignmentOrchestrator.check_assignment_submission")
#def test_submit_assignment___on_empty_data_when_first_assignment_passes_on_first_submission(patched_function, mocker_test_submit_assignment___on_empty_data):
#    patched_function.return_value="PASS"
#    submission_assignment_output=submit_assignment(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",assignment_files=["bla.tar.gz"]))
#    assert submission_assignment_output == {'hacker_id': 'nonExistingUser', 'assignment_id': 1, 'assignment_files': ['bla.tar.gz'], 'submission_id': 1, 'result': 'PASS'}
#    assignment_submissions_json=load_data()
#    assert assignment_submissions_json == {"nonExistingUser":{"1":[submission_assignment_output]}}
