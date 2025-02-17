import pytest
from unittest.mock import patch, mock_open
from assignmentOrchestrator import load_data, assignment_passed, previous_assignment_passed, AssignmentSubmission, save_data, submit_assignment

@patch('os.path.exists')
def test_load_data___on_non_existing_file(mock_input):
    mock_input.return_value=False
    assert load_data() == {}

@pytest.fixture
def mocker_test_load_data___on_existing_file(mocker):
    existing_data = mocker.mock_open(read_data='{"a":2}')
    mocker.patch("builtins.open", existing_data)
    mocker.patch('os.path.exists', return_value=True)
def test_load_data___on_existing_file(mocker_test_load_data___on_existing_file):
    assert load_data() == {"a":2}