
from io import BytesIO
import os
from pathlib import Path
from zipfile import ZipFile
from dataclasses import dataclass
from typing import List

@dataclass
class AssignmentFile:
    file_path: str
    data: str

@dataclass
class DataAndStructure:
    assignment_data: List[AssignmentFile]
    submission_data: List[AssignmentFile]

def get_data_and_structure(submitted_task_directory: str, assignment_id:int, task_id:int) -> DataAndStructure: # only  to be used for testing
    assignment_data_and_structure = get_assignment_data_and_structure(assignment_id) 
    submission_data_and_structure = get_submission_data_and_structure(submitted_task_directory)
    return DataAndStructure(
        assignment_data=assignment_data_and_structure,
        submission_data=submission_data_and_structure
    )

def get_assignment_data_and_structure(assignment_id:int) -> List[AssignmentFile]:
    """
    Extracts all files from the assignment ZIP and returns a list of objects
    containing file_path and data for each file.
    
    Args:
        assignment_id: The ID of the assignment
        
    Returns:
        List of AssignmentFile objects, each containing file_path and data
    """
    zip_path = Path(f'./resources/static/assignment/{str(assignment_id)}/assignment_{str(assignment_id)}.zip')
    assignment_files = []
    
    with ZipFile(zip_path, 'r') as zip_file:
        # Get all file names in the ZIP
        file_names = zip_file.namelist()
        
        for file_name in file_names:
            # Skip directories
            if file_name.endswith('/'):
                continue
                
            try:
                # Read file content and decode as UTF-8
                file_data = zip_file.read(file_name).decode('utf-8')
                assignment_files.append(
                    AssignmentFile(file_path=file_name, data=file_data)
                )
            except UnicodeDecodeError:
                # If file is binary or can't be decoded, skip it or handle differently
                # For now, we'll skip binary files
                continue
            except Exception as e:
                print(f"Error reading file {file_name} from assignment ZIP: {e}")
                continue
    
    return assignment_files

def get_submission_data_and_structure(submitted_task_directory: str) -> List[AssignmentFile]:
    """
    Extracts all files from the submission directory and returns a list of objects
    containing file_path and data for each file.
    
    Args:
        submitted_task_directory: The directory path containing submitted files
        
    Returns:
        List of AssignmentFile objects, each containing file_path and data
    """
    submission_files = []
    submission_path = Path(submitted_task_directory)
    
    if not submission_path.exists():
        print(f"Warning: Submission directory does not exist: {submitted_task_directory}")
        return submission_files
    
    # Walk through the directory and read all files
    for root, _, files in os.walk(submission_path):
        for file in files:
            file_path = Path(root) / file
            try:
                # Read file content as UTF-8
                file_data = file_path.read_text(encoding='utf-8')
                # Get relative path from the submission directory
                relative_path = os.path.relpath(file_path, submission_path)
                submission_files.append(
                    AssignmentFile(file_path=str(relative_path).replace('\\', '/'), data=file_data)
                )
            except UnicodeDecodeError:
                # Skip binary files
                continue
            except Exception as e:
                print(f"Error reading file {file_path} from submission directory: {e}")
                continue
    
    return submission_files

    

def execute_task(task_file_name :str, kill_timeout: float):
    print(f"father::execute_task:: task_file_name='{task_file_name}'")
    submitted_task_directory=os.path.dirname(task_file_name)
    print(f"father::execute_task:: submitted_task_directory='{submitted_task_directory}'")
    assignment_id=int(Path(submitted_task_directory).parts[3])
    task_id=int(Path(submitted_task_directory).parts[5])
    print(f"father::execute_task:: assignment_id='{assignment_id}'")
    print(f"father::execute_task:: task_id='{task_id}'")
    data_and_structure = get_data_and_structure(submitted_task_directory, assignment_id, task_id)
    

if __name__ == "__main__":
    execute_task('./data/submitted_files/concurrency_user_2/1/3/1/a1_task1.py',10)
    #test mode execution:
    #enter project root (zeroDay) directory
    #execute following:
    #python resources/config/assignments/validators/validator_example_05__noDocker__pureCode__mother_testable.py