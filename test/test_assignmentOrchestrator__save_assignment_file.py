import pytest
from unittest.mock import patch, mock_open
from assignmentOrchestrator import load_data, AssignmentSubmission, save_data, save_assignment_files
import base64,os,shutil

gconf={}

@pytest.fixture
def mocker__on_empty_data(mocker,request):   
    gconf["base_test_directory"]                        =f"./data/testData/assignmentOrchestrator/save_assignment_files/{request.node.name}"
    gconf["relative_data_directory"]                    =os.path.join(gconf["base_test_directory"],"data")
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
    
def test__check_directory_created(mocker__on_empty_data):
    assignment_file_names=save_assignment_files(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",submission_id="2", assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))]))
    assert os.path.exists(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","2")) == True

def test__check_file_created(mocker__on_empty_data):
    assignment_file_names=save_assignment_files(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",submission_id="2", assignment_files=[base64.b64encode("fakeScriptData_01".encode('ascii')),base64.b64encode("fakeScriptData_02".encode('ascii'))]))
    files_in_dir=os.listdir(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","2"))
    assert files_in_dir== ["task_1.py","task_2.py"]

def test__validate_file_content(mocker__on_empty_data):
    assignment_file_names=save_assignment_files(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",submission_id="2", assignment_files=[base64.b64encode("fakeScriptData_01".encode('ascii')),base64.b64encode("fakeScriptData_02".encode('ascii'))]))
    with open(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","2","task_1.py"), "r") as f:
        assert f.read()=="fakeScriptData_01"
    with open(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","2","task_2.py"), "r") as f:
        assert f.read()=="fakeScriptData_02"

def test__validate_file_content_after_second_submission_for_same_assignment(mocker__on_empty_data):
    assignment_file_names=save_assignment_files(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",submission_id="1", assignment_files=[base64.b64encode("fakeScriptData_01".encode('ascii')),base64.b64encode("fakeScriptData_02".encode('ascii'))]))
    assignment_file_names=save_assignment_files(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",submission_id="2", assignment_files=[base64.b64encode("fakeScriptData_03".encode('ascii')),base64.b64encode("fakeScriptData_04".encode('ascii'))]))
    with open(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1","task_1.py"), "r") as f:
        assert f.read()=="fakeScriptData_01"
    with open(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1","task_2.py"), "r") as f:
        assert f.read()=="fakeScriptData_02"
    with open(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","2","task_1.py"), "r") as f:
        assert f.read()=="fakeScriptData_03"
    with open(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","2","task_2.py"), "r") as f:
        assert f.read()=="fakeScriptData_04"

def test__validate_file_content_on_two_submissions_for_assignment_1_then_one_on_assignment_2(mocker__on_empty_data):
    assignment_file_names=save_assignment_files(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",submission_id="1", assignment_files=[base64.b64encode("fakeScriptData_01".encode('ascii')),base64.b64encode("fakeScriptData_02".encode('ascii'))]))
    assignment_file_names=save_assignment_files(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="1",submission_id="2", assignment_files=[base64.b64encode("fakeScriptData_03".encode('ascii')),base64.b64encode("fakeScriptData_04".encode('ascii'))]))
    assignment_file_names=save_assignment_files(AssignmentSubmission(hacker_id="nonExistingUser",assignment_id="2",submission_id="1", assignment_files=[base64.b64encode("fakeScriptData_05".encode('ascii')),base64.b64encode("fakeScriptData_06".encode('ascii'))]))
    with open(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1","task_1.py"), "r") as f:
        assert f.read()=="fakeScriptData_01"
    with open(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1","task_2.py"), "r") as f:
        assert f.read()=="fakeScriptData_02"
    with open(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","2","task_1.py"), "r") as f:
        assert f.read()=="fakeScriptData_03"
    with open(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","2","task_2.py"), "r") as f:
        assert f.read()=="fakeScriptData_04"
    with open(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","2","1","task_1.py"), "r") as f:
        assert f.read()=="fakeScriptData_05"
    with open(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","2","1","task_2.py"), "r") as f:
        assert f.read()=="fakeScriptData_06"