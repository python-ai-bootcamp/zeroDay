import json
from llmClient import basicPromptResponse 
def execute_task(task_file_name :str, kill_timeout: float):
    print(f"validator::execute_task::task_file_name='{task_file_name}'")
    with open(task_file_name, 'r', encoding='utf-8') as f:
        task_file_content = f.read()
    
    task_description="""
code should create a function named 'returns_passing_str', this function should return a string with a value of 'passing'"""
    response_format='''
answer me using only valid JSON formatted text of the following structure:
{"status":<statusString>, "FAIL_MESSAGE":Optional<failMessageString>}
status:<statusString> - is a mandatory key with one of the following values:
    "PASS" (if the code achieved the described task)
    "FAIL" (if the code did not achive the described task)
FAIL_MESSAGE:Optional<failMessageString> - an optional string value, set only if code did not achieve the described task explaining why
''' 
    prompt=f"""given the following task description:
"{task_description}"
evaluate if the following python code acheived the described task:
---code start---
{task_file_content}
---code end---
{response_format}
"""
    
    llm_text_response=basicPromptResponse(prompt)
    llm_json_response=json.loads(llm_text_response)
    return llm_json_response
 