from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
from dataclasses import dataclass, field
from typing import Any, Literal, Union, List, Dict
import pandas as pd
from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END
from langgraph.pregel import Pregel
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import chain
from langchain_openai import ChatOpenAI
import json
from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
load_dotenv()
llm = ChatOpenAI()  # Use a suitable model


@dataclass
class AgentState:
    """
    Represents the state of the agent during its execution.
    """
    assignment_script: str = ""
    submission_script: str = ""
    output_json: str = ""
    current_question_index: int = 0
    questions: List[str] = field(default_factory=list) # added questions to state
    agg_score: Dict[str, int] = field(default_factory=lambda: {
        "knowledge": 0,
        "code_quality": 0,
        "authenticity": 0,
        "efficiency": 0
    })

@dataclass
class Artifact:
    artifact_type: Literal["assignment", "submission", "output"]
    file_type: Literal['script','asset','records']
    assignment_id: int  
    task_id: Union[int|None]      
    file_name: str
    content: str      

def get_file_attributes(file_name: str) -> tuple[str, int, int]:
    file_type_map = {".py":"script",".txt":"asset",".json":"records"}
    if Path(file_name).parts[0] == Path(file_name).parts[1]:
        file_name = "/".join(Path(file_name).parts[1:])
    file_type = file_type_map[Path(file_name).suffix]
    assignment_id=int(Path(file_name).parts[0].split('_')[-1])
    task_id = None
    if file_type == "script":
        task_id=int(Path(file_name).parts[1])
    return file_type, assignment_id, task_id

def get_artifacts(io: BytesIO, artifact_type:  Literal["assignment", "submission", "output"]) -> list[Artifact]:
    artifacts = []
    with ZipFile(io) as zip_file:
        # List all file names
        file_names = zip_file.namelist()
        file_names = [name for name in file_names if Path(name).suffix in [".py",".json",".txt"]]
        for file_name in file_names:
            file_type, assignment_id, task_id = get_file_attributes(file_name)
            try:
                artifacts.append(
                    Artifact(
                        artifact_type = artifact_type,
                        file_type = file_type,
                        assignment_id = assignment_id,
                        task_id = task_id,   
                        file_name = file_name,
                        content=zip_file.read(file_name) 
                    )
                )
            except Exception as e:
                breakpoint()
    return artifacts

def get_test_data() -> list[Artifact]: # only  to be used for testing
    artifacts = []
    assignment = BytesIO(Path('resources/static/assignments/assignment_1.zip').read_bytes())
    submission = BytesIO(Path('resources/_content/submissions/submission_1.zip').read_bytes())
    artifacts.extend(get_artifacts(io=assignment, artifact_type="assignment"))
    artifacts.extend(get_artifacts(io=submission, artifact_type="submission"))
    artifacts.extend(get_artifacts(io=submission, artifact_type="output"))
    #df = pd.DataFrame([art.__dict__ for art in artifacts])
    return artifacts

class QuestionStructure(BaseModel):
    questions: list[str] = Field(description="A list of the main questions from the assignment")

def extract_questions(state: AgentState) -> AgentState:

    prompt_template = PromptTemplate.from_template(
    """
    Input:
    -----
    Given the following assignment script:
    {assignment_script}
    
    And the corresponding submission script:
    {submission_script}
    
    And the output JSON:
    {output_json}

    validation:
    ----------
    there should only be {num_questions}
    
    Details:
    --------
    - Identify all questions explicitly marked with the prefix "TODO" within the assignment script.
    - For each identified "TODO" question, interpret its underlying intent and rephrase it into a concise, easy-to-understand explanation of the task being asked.
    - Return these rephrased explanations as a JSON object with the single key "questions".
    - The value associated with this key must be a Python list containing the rephrased explanations of each "TODO" question found in the assignment script.
    - Ensure that the output contains only this JSON object, with no additional text or explanations.
    - The list within the "questions" key should exclusively include these clear and concise explanations of the "TODO" questions.
    
    Example of desired transformation:
    If the "TODO" question is: "TODO: fill in the info string with the following information and format it correctly:"
    The rephrased explanation should be something like: "Populate an information string using provided details and adhere to a specific formatting."
    """
    )
    output_parser = JsonOutputParser(pydantic_object=List[QuestionStructure])

    chain = prompt_template | llm | output_parser
    try:
        output = chain.invoke({
            "assignment_script": state.assignment_script.decode(),
            "submission_script": state.submission_script.decode(),
            "output_json": state.output_json.decode(),
            "num_questions":1 # finish this
        })
        state.questions = [item for item in output['questions']] # Extract just the questions
        print("Extracted Questions:", state.questions)
    except Exception as e:
        print(f"Error extracting questions: {e}")
        breakpoint() # To inspect the error
    breakpoint()
    return state

def create_agent_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    graph.add_node("extract_questions", extract_questions)
    graph.set_entry_point("extract_questions")
    graph.add_edge("extract_questions", END)
    return graph

def run_agent_for_task(task_artifacts: List[Artifact]) -> AgentState:
    
    assignment_artifact = [art for art in task_artifacts if art.artifact_type == "assignment"][0]
    submission_artifact = [art for art in task_artifacts if art.artifact_type == "submission"][0]
    output_artifact = [art for art in task_artifacts if art.artifact_type == "output"][0]
    initial_state = AgentState(
        assignment_script = assignment_artifact.content ,
        submission_script =submission_artifact.content,
        output_json = output_artifact.content,
        questions = [],
        current_question_index = 1,
        agg_score= {
            "knowledge": 0,
            "code_quality": 0,
            "authenticity": 0,
            "efficiency": 0
        },
        )
        

    agent_graph = create_agent_graph()
    runnable = agent_graph.compile()
    return runnable.invoke(initial_state)


def run_agent(artifacts: List[Artifact]) -> AgentState:
    tasks = set([art.task_id for art in artifacts if art.task_id])
    for task_id in tasks:
        task_artifacts = [art for art in artifacts if art.task_id == task_id]
        final_state = run_agent_for_task(task_artifacts)
        #df = pd.DataFrame([art.__dict__ for art in task_artifacts])
        breakpoint()


    

if __name__ == "__main__":
    data = get_test_data()
    state = run_agent(data)
