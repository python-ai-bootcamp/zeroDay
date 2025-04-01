from sandboxService import execute_task_as_module_and_validate_programatically

def execute_task(task_file_name :str, kill_timeout: float):
    validation_code='''
import json, TestedModule

testedModule_returns_passing_str_output=TestedModule.returns_passing_str()

if testedModule_returns_passing_str_output=="passing":
    outputDict={"status":"PASS"}
else:
    outputDict={
        "status":"FAIL",
        "FAIL_message":"module method returns_passing_str() did not print expected output",
        "testedModule_returns_passing_str_output":testedModule_returns_passing_str_output
    }

print(json.dumps(outputDict))
'''
    return execute_task_as_module_and_validate_programatically(task_file_name, kill_timeout, validation_code)