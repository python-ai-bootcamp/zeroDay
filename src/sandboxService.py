import os,subprocess,json
from systemEntities import print
from tempfile import mkstemp
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
    task_file_submission_directory=os.path.dirname(task_file_dir_name)
    #subprocess.call(["docker", "exec", "-t", "task_runner", "mkdir", "-p", task_file_dir_name])
    subprocess.call(["docker", "exec", "-t", "task_runner", "mkdir", "-p", task_file_submission_directory])
    #subprocess.call(["docker", "cp", task_file_name, f"task_runner:{task_file_dir_name}"])
    subprocess.call(["docker", "cp", task_file_dir_name, f"task_runner:{task_file_submission_directory}"])
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


def execute_task_as_module_and_validate_programatically(task_file_name :str, kill_timeout: float, task_module_validation_code:str )-> bool:
    
            ##################################################################################################################
            ##                                                                                                              ##
            ##                                    --- IMPORTANT NOTE:: ---                                                  ##
            ##                                                                                                              ##
            ##  the task_module_validation_code must conform to following contract:                                         ##
            ##      1. it must import the tested module from file named TestedModule.py                                     ##
            ##      2. it must print on its last line a valid json                                                          ##
            ##      3. json must contain a single property {"status":"..."} which can contain only string values PASS/FAIL  ##
            ##                                                                                                              ##
            ##################################################################################################################

    task_file_name=task_file_name.replace('\\','/') 
    task_file_dir_name=os.path.dirname(task_file_name)
    task_file_base_name=os.path.basename(task_file_name)
    task_file_submission_directory=os.path.dirname(task_file_dir_name)
    #subprocess.call(["docker", "exec", "-t", "task_runner", "mkdir", "-p", task_file_dir_name])
    subprocess.call(["docker", "exec", "-t", "task_runner", "mkdir", "-p", task_file_submission_directory])
    #subprocess.call(["docker", "cp", task_file_name, f"task_runner:{task_file_dir_name}"])
    subprocess.call(["docker", "cp", task_file_dir_name, f"task_runner:{task_file_submission_directory}/"])
    subprocess.call(["docker", "exec", "-t", "task_runner", "mv", task_file_name, f"{task_file_dir_name}/TestedModule.py"])
    task_module_validation_code=f"import TestedModule\n{task_module_validation_code}"
    fd, tmp_file_name = mkstemp()
    with os.fdopen(fd, 'w') as f:
        f.write(task_module_validation_code)
        f.flush()
    tmp_file_base_name=os.path.basename(tmp_file_name)
    new_validator_name=f"validator_{task_file_base_name}"
    subprocess.call(["docker", "cp", tmp_file_name, f"task_runner:{task_file_dir_name}"])
    subprocess.call(["docker", "exec", "-t", "task_runner", "mv", f"{task_file_dir_name}/{tmp_file_base_name}", f"{task_file_dir_name}/{new_validator_name}"])
    os.remove(tmp_file_name)
    proc = subprocess.Popen(["docker", "exec", "task_runner", "python", "-u", f"{task_file_dir_name}/{new_validator_name}"],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
    )
    try:
        stdout, stderr = proc.communicate(timeout=kill_timeout)
        stdout=stdout.decode(encoding="utf-8")
        stderr=stderr.decode(encoding="utf-8")
        if stderr == '' :
            try:
                print("---------------validator received following output------------------")
                print(stdout)
                print("--------------------------------------------------------------------")
                validatorJsonResponse=json.loads(stdout.splitlines()[-1])
                if validatorJsonResponse == {"status":"PASS"}:
                    return {"status":"PASS"}
                else:
                    return {**validatorJsonResponse, "status":"FAIL"}
            except:
                return {"status": "FAIL", "FAIL_message":"failed to parse validators last line as json"}
        else:
            return {"status":"FAIL","FAIL_message":"task failed because it printed to STDERR","FAIL_message_stdout":stdout,"FAIL_message_stderr":stderr}
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        stdout=stdout.decode(encoding="utf-8")
        stderr=stderr.decode(encoding="utf-8")
        return {"status":"FAIL","FAIL_message":f"task did not finish executing in required time (kill_timeout={kill_timeout}s)","FAIL_message_stdout":stdout,"FAIL_message_stderr":stderr}
