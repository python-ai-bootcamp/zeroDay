import os,subprocess
from typing import Callable, List
from threading import Semaphore

def startDockerContainer(submision_processing_concurrency_semaphore :Semaphore,MAX_SUBMISION_PROCESSING:int):
    print("stopping all conainers with name='task_runner'")
    subprocess.call(["docker", "container", "stop", "task_runner"])
    print("removing all stopped containers")
    subprocess.call(["docker", "container", "prune", "-f"])
    print("force killing container named 'task_runner' if from some reason he remained alive")
    subprocess.call(["docker", "container", "rm", "--force", "task_runner"])
    print("starting container named task_runner from image alpine:python_task_runner in daemon mode")
    subprocess.call(["docker", "run", "-t", "-d", "--name", "task_runner", "alpine:python_task_runner"])
    print("releasing submision_processing_concurrency_semaphore")
    for sem_idx in range(MAX_SUBMISION_PROCESSING):
        submision_processing_concurrency_semaphore.release()

def execute_task_as_script_and_validate_text_output(task_file_name :str, kill_timeout: float, task_output_validation_func:Callable[[str], bool], task_input_arguments:List[str]=[] )-> bool:
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


def execute_task_as_module_and_validate_programatically(task_file_name :str, kill_timeout: float, task_output_validation_func:Callable[[str], bool], task_input_arguments:List[str]=[] )-> bool:
    ##################### NOT YET IMPLEMENTED ####################################
    # basic concept would be to:
    # print the code of the function (if possible, if not just take the code as text filed from validator)
    #   probably possible to get the code of a function inside a module WOOHOO! https://stackoverflow.com/questions/399991/how-do-you-get-python-to-write-down-the-code-of-a-function-it-has-in-memory
    #   not sure about entire module though, might be a problem with validator imports if they exist
    # copy it to docker container
    # execute it instead of the task
    # it will load the file as a module and do what it wants, and at the end returns boolean asnwer which will be parsed as text
    ##################### NOT YET IMPLEMENTED ####################################
    print("not implemented yet")
    return {"status":"FAIL","FAIL_message":"not yet implemented"}
