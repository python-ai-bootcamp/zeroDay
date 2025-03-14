import pytest
from unittest.mock import patch, mock_open
from assignmentOrchestrator import AssignmentSubmission, execute_validator_on_task_file
from pathlib import Path
import base64,os,shutil,json

gconf={}

always_passing_validator="""def execute_task(task_file_name :str, kill_timeout: float):
    return {"status":"PASS"}
"""

always_failing_validator="""def execute_task(task_file_name :str, kill_timeout: float):
    return {"status":"FAIL","FAIL_message":"face it, your code is shit!"}
"""

always_failing_validator_unique_1="""def execute_task(task_file_name :str, kill_timeout: float):
    return {"status":"FAIL","FAIL_message":"unique_1"}
"""

always_failing_validator_unique_2="""def execute_task(task_file_name :str, kill_timeout: float):
    return {"status":"FAIL","FAIL_message":"unique_2"}
"""

always_failing_validator_unique_3="""def execute_task(task_file_name :str, kill_timeout: float):
    return {"status":"FAIL","FAIL_message":"unique_3"}
"""

always_failing_validator_unique_4="""def execute_task(task_file_name :str, kill_timeout: float):
    return {"status":"FAIL","FAIL_message":"unique_4"}
"""

validator_that_checks_if_file_exists="""import os
def execute_task(task_file_name :str, kill_timeout: float):
    if os.path.isfile(task_file_name):
        return {"status":"PASS"}
    else:
        return {"status":"FAIL","FAIL_message":"file not found"}
"""
validator_that_executes_a_task_file_and_always_passes="""import os,subprocess
def execute_task(task_file_name :str, kill_timeout: float):
    proc = subprocess.Popen(["python","-u", task_file_name],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
    )
    try:
        stdout, stderr = proc.communicate(timeout=kill_timeout)
        stdout=stdout.decode(encoding="utf-8")
        stderr=stderr.decode(encoding="utf-8")
        return {"status":"PASS","PASS_message_stdout":stdout,"PASS_message_stderr":stderr}
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        stdout=stdout.decode(encoding="utf-8")
        stderr=stderr.decode(encoding="utf-8")
        return {"status":"FAIL","FAIL_message":f"task did not finish executing in required time (kill_timeout={kill_timeout}s)","FAIL_message_stdout":stdout,"FAIL_message_stderr":stderr}
"""
validator_that_executes_a_task_file_and_fails_if_prints_sent_to_error_stream="""import os,subprocess
def execute_task(task_file_name :str, kill_timeout: float):
    proc = subprocess.Popen(["python","-u", task_file_name],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
    )
    try:
        stdout, stderr = proc.communicate(timeout=kill_timeout)
        stdout=stdout.decode(encoding="utf-8")
        stderr=stderr.decode(encoding="utf-8")
        if stderr == '' :
            return {"status":"PASS","PASS_message_stdout":stdout,"PASS_message_stderr":stderr}
        else:
            return {"status":"FAIL","FAIL_message":"task failed because it printed to STDERR","FAIL_message_stdout":stdout,"FAIL_message_stderr":stderr}
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        stdout=stdout.decode(encoding="utf-8")
        stderr=stderr.decode(encoding="utf-8")
        return {"status":"FAIL","FAIL_message":f"task did not finish executing in required time (kill_timeout={kill_timeout}s)","FAIL_message_stdout":stdout,"FAIL_message_stderr":stderr}
"""
validator_that_evaluates_stdout_to_determin_result="""import os,subprocess
def execute_task(task_file_name :str, kill_timeout: float):
    proc = subprocess.Popen(["python","-u", task_file_name],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
    )
    try:
        stdout, stderr = proc.communicate(timeout=kill_timeout)
        stdout=stdout.decode(encoding="utf-8")
        stderr=stderr.decode(encoding="utf-8")
        if stderr == '' :
            if stdout.strip() == 'passing':
                return {"status":"PASS"}
            else:
                return {"status":"FAIL","FAIL_message":"task did not print expected output","FAIL_message_stdout":stdout}
        else:
            return {"status":"FAIL","FAIL_message":"task failed because it printed to STDERR","FAIL_message_stdout":stdout,"FAIL_message_stderr":stderr}
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        stdout=stdout.decode(encoding="utf-8")
        stderr=stderr.decode(encoding="utf-8")
        return {"status":"FAIL","FAIL_message":f"task did not finish executing in required time (kill_timeout={kill_timeout}s)","FAIL_message_stdout":stdout,"FAIL_message_stderr":stderr}
"""
task_that_prints_to_stdout_and_stderr="""import sys
sys.stdout.write("i'm STDOUT #1")
sys.stderr.write("i'm STDERR #1")
sys.stdout.write("i'm STDOUT #2")
sys.stderr.write("i'm STDERR #2")
"""
task_that_prints_to_stdout_and_stderr_before_breaching_timeout_with_sleep="""import sys,time 
sys.stdout.write("i'm STDOUT #1")
sys.stderr.write("i'm STDERR #1")
sys.stdout.write("i'm STDOUT #2")
sys.stderr.write("i'm STDERR #2")
time.sleep(10)
"""
task_that_prints_to_stdout_and_stderr_after_breaching_timeout_with_busywait="""import sys
x=1
while True:
    x=x*10
    x=x/10
sys.stdout.write("i'm STDOUT #1")
sys.stderr.write("i'm STDERR #1")
sys.stdout.write("i'm STDOUT #2")
sys.stderr.write("i'm STDERR #2")
"""
task_that_prints_to_stdout_and_stderr_after_breaching_timeout_while_swamping_stdout="""import sys
x=1
while True:
    sys.stdout.write("i'm STDOUT #1")
    sys.stdout.write("i'm STDOUT #2")
"""
task_that_prints_to_stdout_and_stderr_after_breaching_timeout_while_swamping_stderr="""import sys
x=1
while True:
    sys.stderr.write("i'm STDERR #1")
    sys.stderr.write("i'm STDERR #2")
"""
task_that_breaching_timeout_stuck_on_user_input_io="""import sys
sys.stdout.write("please enter input::")
input()

"""
task_that_raises_unexpected_exception="""import sys,time
print("please enter input::")
print("i'm going to sleep now")
sys.stderr.write("ho no!, i forgot the amount of time i need to sleep")
time.sleep()
"""
task_task_with_passing_stdout="""print("passing")"""
task_task_with_failing_stdout="""print("failing")"""

@pytest.fixture
def mocker__on_empty_data(mocker,request):   
    gconf["base_test_directory"]                        =f"./data/testData/assignmentOrchestrator/execute_validator_on_task_file/{request.node.name}"
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

    mocker.patch("assignmentOrchestrator.SUBMITTED_FILES_DIR",          gconf["relative_submitted_files_directory"])
    mocker.patch("assignmentOrchestrator.ASSIGNMENT_VALIDATOR_DIR",     gconf["relative_validators_directory"])
    mocker.patch("assignmentOrchestrator.ASSIGNMENT_MAPPER_FILE",       gconf["test_assignment_mapper_json_file_location"])
    gconf["default_validator_timeout"]  = 0.1
    mocker.patch("assignmentOrchestrator.DEFAULT_VALIDATOR_TIMEOUT",    gconf["default_validator_timeout"])

def test__always_passing_validator__on_first_task_first_submission(mocker__on_empty_data):
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py']}}
    validator_script_file_location=os.path.join(gconf["relative_validators_directory"],'validate_assignment_1_task_1.py')
    with open(validator_script_file_location, "w") as validator_f:
        validator_f.write(always_passing_validator)
    assignment_submission=AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py'])
    assignment_submission_directory=os.path.join(gconf["relative_submitted_files_directory"],assignment_submission.hacker_id,str(assignment_submission.assignment_id),str(assignment_submission.submission_id))
    os.makedirs(assignment_submission_directory,exist_ok=True)
    Path(os.path.join(assignment_submission_directory,assignment_submission.assignment_file_names[0])).touch()
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    execute_validator_on_task_file_output=execute_validator_on_task_file(validator_script=validator_script_file_location, task_file_name="task_1.py", assignment_submission=assignment_submission)
    assert execute_validator_on_task_file_output == {'status': 'PASS'}

def test__always_failing_validator__on_first_task_first_submission(mocker__on_empty_data):
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py']}}
    validator_script_file_location=os.path.join(gconf["relative_validators_directory"],'validate_assignment_1_task_1.py')
    with open(validator_script_file_location, "w") as validator_f:
        validator_f.write(always_failing_validator)
    assignment_submission=AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py'])
    assignment_submission_directory=os.path.join(gconf["relative_submitted_files_directory"],assignment_submission.hacker_id,str(assignment_submission.assignment_id),str(assignment_submission.submission_id))
    os.makedirs(assignment_submission_directory,exist_ok=True)
    Path(os.path.join(assignment_submission_directory,assignment_submission.assignment_file_names[0])).touch()
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    execute_validator_on_task_file_output=execute_validator_on_task_file(validator_script=validator_script_file_location, task_file_name="task_1.py", assignment_submission=assignment_submission)
    assert execute_validator_on_task_file_output == {"status":"FAIL","FAIL_message":"face it, your code is shit!"}

def test__two_tasks_on_first_and_second_assignment_on_first_submission(mocker__on_empty_data):
    test_assignment_mapper_json_file_data={
        '1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py','validate_assignment_1_task_2.py']},
        '2': {'description': 'description_1.md', 'validators': ['validate_assignment_2_task_1.py','validate_assignment_2_task_2.py']},
    }
    validator_script_file_location_assignment_1_task_1=os.path.join(gconf["relative_validators_directory"],'validate_assignment_1_task_1.py')
    validator_script_file_location_assignment_1_task_2=os.path.join(gconf["relative_validators_directory"],'validate_assignment_1_task_2.py')
    validator_script_file_location_assignment_2_task_1=os.path.join(gconf["relative_validators_directory"],'validate_assignment_2_task_1.py')
    validator_script_file_location_assignment_2_task_2=os.path.join(gconf["relative_validators_directory"],'validate_assignment_2_task_2.py')
    with open(validator_script_file_location_assignment_1_task_1, "w") as validator_f:
        validator_f.write(always_failing_validator_unique_1)
    with open(validator_script_file_location_assignment_1_task_2, "w") as validator_f:
        validator_f.write(always_failing_validator_unique_2)
    with open(validator_script_file_location_assignment_2_task_1, "w") as validator_f:
        validator_f.write(always_failing_validator_unique_3)
    with open(validator_script_file_location_assignment_2_task_2, "w") as validator_f:
        validator_f.write(always_failing_validator_unique_4)
        
    os.makedirs(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1"),exist_ok=True)
    os.makedirs(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","2","1"),exist_ok=True)
    Path(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1",'task_1.py')).touch()
    Path(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","1","1",'task_2.py')).touch()
    Path(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","2","1",'task_1.py')).touch()
    Path(os.path.join(gconf["relative_submitted_files_directory"],"nonExistingUser","2","1",'task_2.py')).touch()

    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    assignment_1_submission=AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py','task_2.py'])
    assignment_2_submission=AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=2,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py','task_2.py'])
    execute_validator_on_task_file_assignment_1_task_1_output=execute_validator_on_task_file(validator_script=validator_script_file_location_assignment_1_task_1, task_file_name="task_1.py", assignment_submission=assignment_1_submission)
    assert execute_validator_on_task_file_assignment_1_task_1_output == {"status":"FAIL","FAIL_message":"unique_1"}
    execute_validator_on_task_file_assignment_1_task_2_output=execute_validator_on_task_file(validator_script=validator_script_file_location_assignment_1_task_2, task_file_name="task_2.py", assignment_submission=assignment_1_submission)
    assert execute_validator_on_task_file_assignment_1_task_2_output == {"status":"FAIL","FAIL_message":"unique_2"}
    execute_validator_on_task_file_assignment_2_task_1_output=execute_validator_on_task_file(validator_script=validator_script_file_location_assignment_2_task_1, task_file_name="task_1.py", assignment_submission=assignment_1_submission)
    assert execute_validator_on_task_file_assignment_2_task_1_output == {"status":"FAIL","FAIL_message":"unique_3"}
    execute_validator_on_task_file_assignment_2_task_2_output=execute_validator_on_task_file(validator_script=validator_script_file_location_assignment_2_task_2, task_file_name="task_2.py", assignment_submission=assignment_1_submission)
    assert execute_validator_on_task_file_assignment_2_task_2_output == {"status":"FAIL","FAIL_message":"unique_4"}

def test__validator_checks_if_task_file_exists_in_path(mocker__on_empty_data):
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py']}}
    validator_script_file_location=os.path.join(gconf["relative_validators_directory"],'validate_assignment_1_task_1.py')
    with open(validator_script_file_location, "w") as validator_f:
        validator_f.write(validator_that_checks_if_file_exists)
    assignment_submission=AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py'])
    assignment_submission_directory=os.path.join(gconf["relative_submitted_files_directory"],assignment_submission.hacker_id,str(assignment_submission.assignment_id),str(assignment_submission.submission_id))
    os.makedirs(assignment_submission_directory,exist_ok=True)
    Path(os.path.join(assignment_submission_directory,assignment_submission.assignment_file_names[0])).touch()
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    execute_validator_on_task_file_output=execute_validator_on_task_file(validator_script=validator_script_file_location, task_file_name="task_1.py", assignment_submission=assignment_submission)
    assert execute_validator_on_task_file_output == {'status': 'PASS'}

def test__validator_executes_a_task_returning_stdout_and_stderr_and_passes(mocker__on_empty_data):
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py']}}
    validator_script_file_location=os.path.join(gconf["relative_validators_directory"],'validate_assignment_1_task_1.py')
    with open(validator_script_file_location, "w") as validator_f:
        validator_f.write(validator_that_executes_a_task_file_and_always_passes)
    assignment_submission=AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py'])
    assignment_submission_directory=os.path.join(gconf["relative_submitted_files_directory"],assignment_submission.hacker_id,str(assignment_submission.assignment_id),str(assignment_submission.submission_id))
    os.makedirs(assignment_submission_directory,exist_ok=True)
    with open(os.path.join(assignment_submission_directory,assignment_submission.assignment_file_names[0]),'w') as f:
        f.write(task_that_prints_to_stdout_and_stderr)
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    execute_validator_on_task_file_output=execute_validator_on_task_file(validator_script=validator_script_file_location, task_file_name="task_1.py", assignment_submission=assignment_submission)
    assert execute_validator_on_task_file_output == {'status': 'PASS','PASS_message_stderr': "i'm STDERR #1i'm STDERR #2",'PASS_message_stdout': "i'm STDOUT #1i'm STDOUT #2"}

def test__validator_executes_a_task_printing_before_breach_timeout_with_sleep(mocker__on_empty_data):
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py']}}
    validator_script_file_location=os.path.join(gconf["relative_validators_directory"],'validate_assignment_1_task_1.py')
    with open(validator_script_file_location, "w") as validator_f:
        validator_f.write(validator_that_executes_a_task_file_and_always_passes)
    assignment_submission=AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py'])
    assignment_submission_directory=os.path.join(gconf["relative_submitted_files_directory"],assignment_submission.hacker_id,str(assignment_submission.assignment_id),str(assignment_submission.submission_id))
    os.makedirs(assignment_submission_directory,exist_ok=True)
    with open(os.path.join(assignment_submission_directory,assignment_submission.assignment_file_names[0]),'w') as f:
        f.write(task_that_prints_to_stdout_and_stderr_before_breaching_timeout_with_sleep)
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    execute_validator_on_task_file_output=execute_validator_on_task_file(validator_script=validator_script_file_location, task_file_name="task_1.py", assignment_submission=assignment_submission)
    assert execute_validator_on_task_file_output == {'status': 'FAIL','FAIL_message': f'task did not finish executing in required time (kill_timeout={gconf["default_validator_timeout"]}s)','FAIL_message_stderr': "i'm STDERR #1i'm STDERR #2",'FAIL_message_stdout': "i'm STDOUT #1i'm STDOUT #2"}

def test__validator_executes_a_task_printing_after_breach_timeout_with_busywait(mocker__on_empty_data):
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py']}}
    validator_script_file_location=os.path.join(gconf["relative_validators_directory"],'validate_assignment_1_task_1.py')
    with open(validator_script_file_location, "w") as validator_f:
        validator_f.write(validator_that_executes_a_task_file_and_always_passes)
    assignment_submission=AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py'])
    assignment_submission_directory=os.path.join(gconf["relative_submitted_files_directory"],assignment_submission.hacker_id,str(assignment_submission.assignment_id),str(assignment_submission.submission_id))
    os.makedirs(assignment_submission_directory,exist_ok=True)
    with open(os.path.join(assignment_submission_directory,assignment_submission.assignment_file_names[0]),'w') as f:
        f.write(task_that_prints_to_stdout_and_stderr_after_breaching_timeout_with_busywait)
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    execute_validator_on_task_file_output=execute_validator_on_task_file(validator_script=validator_script_file_location, task_file_name="task_1.py", assignment_submission=assignment_submission)
    assert execute_validator_on_task_file_output == {'status': 'FAIL','FAIL_message': f'task did not finish executing in required time (kill_timeout={gconf["default_validator_timeout"]}s)','FAIL_message_stderr': "",'FAIL_message_stdout': ""}

def test__validator_executes_a_task_breaching_timeout_with_stdout_swamping(mocker__on_empty_data):
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py']}}
    validator_script_file_location=os.path.join(gconf["relative_validators_directory"],'validate_assignment_1_task_1.py')
    with open(validator_script_file_location, "w") as validator_f:
        validator_f.write(validator_that_executes_a_task_file_and_always_passes)
    assignment_submission=AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py'])
    assignment_submission_directory=os.path.join(gconf["relative_submitted_files_directory"],assignment_submission.hacker_id,str(assignment_submission.assignment_id),str(assignment_submission.submission_id))
    os.makedirs(assignment_submission_directory,exist_ok=True)
    with open(os.path.join(assignment_submission_directory,assignment_submission.assignment_file_names[0]),'w') as f:
        f.write(task_that_prints_to_stdout_and_stderr_after_breaching_timeout_while_swamping_stdout)
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    execute_validator_on_task_file_output=execute_validator_on_task_file(validator_script=validator_script_file_location, task_file_name="task_1.py", assignment_submission=assignment_submission)
    assert execute_validator_on_task_file_output["status"] == "FAIL"
    assert execute_validator_on_task_file_output["FAIL_message"] == f'task did not finish executing in required time (kill_timeout={gconf["default_validator_timeout"]}s)'
    assert execute_validator_on_task_file_output["FAIL_message_stderr"] == ''
    assert execute_validator_on_task_file_output["FAIL_message_stdout"].startswith("i'm STDOUT #1i'm STDOUT #2")

def test__validator_executes_a_task_breaching_timeout_with_stderr_swamping(mocker__on_empty_data):
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py']}}
    validator_script_file_location=os.path.join(gconf["relative_validators_directory"],'validate_assignment_1_task_1.py')
    with open(validator_script_file_location, "w") as validator_f:
        validator_f.write(validator_that_executes_a_task_file_and_always_passes)
    assignment_submission=AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py'])
    assignment_submission_directory=os.path.join(gconf["relative_submitted_files_directory"],assignment_submission.hacker_id,str(assignment_submission.assignment_id),str(assignment_submission.submission_id))
    os.makedirs(assignment_submission_directory,exist_ok=True)
    with open(os.path.join(assignment_submission_directory,assignment_submission.assignment_file_names[0]),'w') as f:
        f.write(task_that_prints_to_stdout_and_stderr_after_breaching_timeout_while_swamping_stderr)
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    execute_validator_on_task_file_output=execute_validator_on_task_file(validator_script=validator_script_file_location, task_file_name="task_1.py", assignment_submission=assignment_submission)
    assert execute_validator_on_task_file_output["status"] == "FAIL"
    assert execute_validator_on_task_file_output["FAIL_message"] == f'task did not finish executing in required time (kill_timeout={gconf["default_validator_timeout"]}s)'
    assert execute_validator_on_task_file_output["FAIL_message_stdout"] == ''
    assert execute_validator_on_task_file_output["FAIL_message_stderr"].startswith("i'm STDERR #1i'm STDERR #2")

@pytest.fixture
def suspend_capture(pytestconfig):
    class suspend_guard:
        def __init__(self):
            self.capmanager = pytestconfig.pluginmanager.getplugin('capturemanager')
        def __enter__(self):
            self.capmanager.suspend_global_capture(in_=True)
        def __exit__(self, _1, _2, _3):
            self.capmanager.resume_global_capture()

    yield suspend_guard()

def test__validator_executes_a_task_breaching_timeout_stuck_on_user_input_prompt(mocker__on_empty_data,suspend_capture):
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py']}}
    validator_script_file_location=os.path.join(gconf["relative_validators_directory"],'validate_assignment_1_task_1.py')
    with open(validator_script_file_location, "w") as validator_f:
        validator_f.write(validator_that_executes_a_task_file_and_always_passes)
    assignment_submission=AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py'])
    assignment_submission_directory=os.path.join(gconf["relative_submitted_files_directory"],assignment_submission.hacker_id,str(assignment_submission.assignment_id),str(assignment_submission.submission_id))
    os.makedirs(assignment_submission_directory,exist_ok=True)
    with open(os.path.join(assignment_submission_directory,assignment_submission.assignment_file_names[0]),'w') as f:
        f.write(task_that_breaching_timeout_stuck_on_user_input_io)
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    with suspend_capture:
        execute_validator_on_task_file_output=execute_validator_on_task_file(validator_script=validator_script_file_location, task_file_name="task_1.py", assignment_submission=assignment_submission)
    assert execute_validator_on_task_file_output == {'status': 'FAIL','FAIL_message': f'task did not finish executing in required time (kill_timeout={gconf["default_validator_timeout"]}s)','FAIL_message_stderr': "",'FAIL_message_stdout': "please enter input::"}

def test__validator_executes_a_task_raising_unexpected_exception(mocker__on_empty_data,suspend_capture):
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py']}}
    validator_script_file_location=os.path.join(gconf["relative_validators_directory"],'validate_assignment_1_task_1.py')
    with open(validator_script_file_location, "w") as validator_f:
        validator_f.write(validator_that_executes_a_task_file_and_always_passes)
    assignment_submission=AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py'])
    assignment_submission_directory=os.path.join(gconf["relative_submitted_files_directory"],assignment_submission.hacker_id,str(assignment_submission.assignment_id),str(assignment_submission.submission_id))
    os.makedirs(assignment_submission_directory,exist_ok=True)
    with open(os.path.join(assignment_submission_directory,assignment_submission.assignment_file_names[0]),'w') as f:
        f.write(task_that_raises_unexpected_exception)
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    with suspend_capture:
        execute_validator_on_task_file_output=execute_validator_on_task_file(validator_script=validator_script_file_location, task_file_name="task_1.py", assignment_submission=assignment_submission)
    assert execute_validator_on_task_file_output["status"] == "PASS"
    assert execute_validator_on_task_file_output["PASS_message_stdout"] == "please enter input::\r\ni'm going to sleep now\r\n"
    assert execute_validator_on_task_file_output["PASS_message_stderr"].startswith("ho no!, i forgot the amount of time i need to sleepTraceback (most recent call last):")

def test__validator_that_gives_status_based_on_task_stdout_which_is_correct(mocker__on_empty_data,suspend_capture):
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py']}}
    validator_script_file_location=os.path.join(gconf["relative_validators_directory"],'validate_assignment_1_task_1.py')
    with open(validator_script_file_location, "w") as validator_f:
        validator_f.write(validator_that_evaluates_stdout_to_determin_result)
    assignment_submission=AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py'])
    assignment_submission_directory=os.path.join(gconf["relative_submitted_files_directory"],assignment_submission.hacker_id,str(assignment_submission.assignment_id),str(assignment_submission.submission_id))
    os.makedirs(assignment_submission_directory,exist_ok=True)
    with open(os.path.join(assignment_submission_directory,assignment_submission.assignment_file_names[0]),'w') as f:
        f.write(task_task_with_passing_stdout)
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    with suspend_capture:
        execute_validator_on_task_file_output=execute_validator_on_task_file(validator_script=validator_script_file_location, task_file_name="task_1.py", assignment_submission=assignment_submission)
    assert execute_validator_on_task_file_output == {'status': 'PASS'}

def test__validator_that_gives_status_based_on_task_stdout_which_is_incorrect(mocker__on_empty_data,suspend_capture):
    test_assignment_mapper_json_file_data={'1': {'description': 'description_1.md', 'validators': ['validate_assignment_1_task_1.py']}}
    validator_script_file_location=os.path.join(gconf["relative_validators_directory"],'validate_assignment_1_task_1.py')
    with open(validator_script_file_location, "w") as validator_f:
        validator_f.write(validator_that_evaluates_stdout_to_determin_result)
    assignment_submission=AssignmentSubmission(hacker_id="nonExistingUser",assignment_id=1,submission_id=1, assignment_files=[base64.b64encode("fakeScriptData".encode('ascii'))], assignment_file_names=['task_1.py'])
    assignment_submission_directory=os.path.join(gconf["relative_submitted_files_directory"],assignment_submission.hacker_id,str(assignment_submission.assignment_id),str(assignment_submission.submission_id))
    os.makedirs(assignment_submission_directory,exist_ok=True)
    with open(os.path.join(assignment_submission_directory,assignment_submission.assignment_file_names[0]),'w') as f:
        f.write(task_task_with_failing_stdout)
    with open(gconf["test_assignment_mapper_json_file_location"], 'w') as f:
        json.dump(test_assignment_mapper_json_file_data, f)
    with suspend_capture:
        execute_validator_on_task_file_output=execute_validator_on_task_file(validator_script=validator_script_file_location, task_file_name="task_1.py", assignment_submission=assignment_submission)
    assert execute_validator_on_task_file_output == {'status': 'FAIL','FAIL_message': 'task did not print expected output','FAIL_message_stdout': "failing\r\n"}
