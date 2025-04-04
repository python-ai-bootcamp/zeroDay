from sandboxService import execute_task_as_script_and_validate_text_output

def execute_task(task_file_name :str, kill_timeout: float):
    def validation_func(task_stdout:str)->bool:
       if task_stdout.strip() == 'passing':
           return True
       else:
           return False

    return execute_task_as_script_and_validate_text_output(task_file_name, kill_timeout, validation_func)