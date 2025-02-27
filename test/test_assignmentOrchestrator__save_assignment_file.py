import pytest
from unittest.mock import patch, mock_open
from assignmentOrchestrator import load_data, AssignmentSubmission, save_data, save_assignment_files
import base64,os,shutil

relative_data_directory="./data/testData/data"

@pytest.fixture
def mocker_test_submit_assignment___on_empty_data(mocker):   
    shutil.rmtree(relative_data_directory)
    mocker.patch("assignmentOrchestrator.SUBMITTED_FILES_DIR", os.path.join(relative_data_directory,"submitted_files"))

def test_save_assignment_file___on_empty_data__check_directory_created(mocker_test_submit_assignment___on_empty_data):
    assignment_file_names=save_assignment_files(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",submission_id="2", assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert os.path.exists(os.path.join(relative_data_directory,"submitted_files","nonExistingUser","1","2")) == True

def test_save_assignment_file___on_empty_data__check_file_created(mocker_test_submit_assignment___on_empty_data):
    assignment_file_names=save_assignment_files(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",submission_id="2", assignment_files=[base64.b64encode("fakeScriptData_01".encode('ascii')),base64.b64encode("fakeScriptData_02".encode('ascii'))]))
    files_in_dir=os.listdir(os.path.join(relative_data_directory,"submitted_files","nonExistingUser","1","2"))
    assert files_in_dir== ["task_1.py","task_2.py"]

def test_save_assignment_file___on_empty_data__validate_file_content(mocker_test_submit_assignment___on_empty_data):
    assignment_file_names=save_assignment_files(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",submission_id="2", assignment_files=[base64.b64encode("fakeScriptData_01".encode('ascii')),base64.b64encode("fakeScriptData_02".encode('ascii'))]))
    with open(os.path.join(relative_data_directory,"submitted_files","nonExistingUser","1","2","task_1.py"), "r") as f:
        assert f.read()=="fakeScriptData_01"
    with open(os.path.join(relative_data_directory,"submitted_files","nonExistingUser","1","2","task_2.py"), "r") as f:
        assert f.read()=="fakeScriptData_02"

def test_save_assignment_file___on_empty_data__validate_file_content_after_second_submission_for_same_assignment(mocker_test_submit_assignment___on_empty_data):
    assignment_file_names=save_assignment_files(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",submission_id="1", assignment_files=[base64.b64encode("fakeScriptData_01".encode('ascii')),base64.b64encode("fakeScriptData_02".encode('ascii'))]))
    assignment_file_names=save_assignment_files(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",submission_id="2", assignment_files=[base64.b64encode("fakeScriptData_03".encode('ascii')),base64.b64encode("fakeScriptData_04".encode('ascii'))]))
    with open(os.path.join(relative_data_directory,"submitted_files","nonExistingUser","1","1","task_1.py"), "r") as f:
        assert f.read()=="fakeScriptData_01"
    with open(os.path.join(relative_data_directory,"submitted_files","nonExistingUser","1","1","task_2.py"), "r") as f:
        assert f.read()=="fakeScriptData_02"
    with open(os.path.join(relative_data_directory,"submitted_files","nonExistingUser","1","2","task_1.py"), "r") as f:
        assert f.read()=="fakeScriptData_03"
    with open(os.path.join(relative_data_directory,"submitted_files","nonExistingUser","1","2","task_2.py"), "r") as f:
        assert f.read()=="fakeScriptData_04"

def test_save_assignment_file___on_empty_data__validate_file_content_after_second_submission_for_first_assignment_followed_by_second_assignment(mocker_test_submit_assignment___on_empty_data):
    assignment_file_names=save_assignment_files(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",submission_id="1", assignment_files=[base64.b64encode("fakeScriptData_01".encode('ascii')),base64.b64encode("fakeScriptData_02".encode('ascii'))]))
    assignment_file_names=save_assignment_files(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",submission_id="2", assignment_files=[base64.b64encode("fakeScriptData_03".encode('ascii')),base64.b64encode("fakeScriptData_04".encode('ascii'))]))
    assignment_file_names=save_assignment_files(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="2",submission_id="1", assignment_files=[base64.b64encode("fakeScriptData_05".encode('ascii')),base64.b64encode("fakeScriptData_06".encode('ascii'))]))
    with open(os.path.join(relative_data_directory,"submitted_files","nonExistingUser","1","1","task_1.py"), "r") as f:
        assert f.read()=="fakeScriptData_01"
    with open(os.path.join(relative_data_directory,"submitted_files","nonExistingUser","1","1","task_2.py"), "r") as f:
        assert f.read()=="fakeScriptData_02"
    with open(os.path.join(relative_data_directory,"submitted_files","nonExistingUser","1","2","task_1.py"), "r") as f:
        assert f.read()=="fakeScriptData_03"
    with open(os.path.join(relative_data_directory,"submitted_files","nonExistingUser","1","2","task_2.py"), "r") as f:
        assert f.read()=="fakeScriptData_04"
    with open(os.path.join(relative_data_directory,"submitted_files","nonExistingUser","2","1","task_1.py"), "r") as f:
        assert f.read()=="fakeScriptData_05"
    with open(os.path.join(relative_data_directory,"submitted_files","nonExistingUser","2","1","task_2.py"), "r") as f:
        assert f.read()=="fakeScriptData_06"