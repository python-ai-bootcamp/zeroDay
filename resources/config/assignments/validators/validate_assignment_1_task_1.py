import os,subprocess
from typing import Callable
from typing import List


def shitty_reusable_validator_code(task_file_name :str, kill_timeout: float, task_output_validation_func:Callable[[str], bool], task_input_arguments:List[str]=[] )-> bool:
    task_file_name=task_file_name.replace('\\','/') #because shitty os.path.join will make strange backslashes instead of forward slashes under windows
    task_file_dir_name=os.path.dirname(task_file_name)
    subprocess.call(["docker", "exec", "-t", "task_runner", "mkdir", "-p", task_file_dir_name])
    subprocess.call(["docker", "cp", task_file_name, f"task_runner:{task_file_dir_name}"])
    #cmd=["docker", "exec", "-t", "task_runner", "python", "-u", task_file_name]+task_input_arguments
    cmd=["docker", "exec", "task_runner", "python", "-u", task_file_name]+task_input_arguments
    proc = subprocess.Popen(cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
    )
    try:
        stdout, stderr = proc.communicate(timeout=kill_timeout)
        stdout=stdout.decode(encoding="utf-8")
        stderr=stderr.decode(encoding="utf-8")
        if stderr == '' :
            if task_output_validation_func(stdout):
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

def execute_task(task_file_name :str, kill_timeout: float):
    def validation_func(task_stdout:str)->bool:
       if task_stdout.strip() == 'passing':
           return True
       else:
           return False

    return shitty_reusable_validator_code(task_file_name, kill_timeout, validation_func)