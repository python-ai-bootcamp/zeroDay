import warnings, os
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain_core")
from systemEntities import print
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
from dataclasses import dataclass, field
from typing import  Literal, Union, List, Dict, cast, Any, overload, Optional
import pandas as pd
from typing import Annotated
import json
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.pregel import Pregel
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import chain
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from llmClient import load_validator_model
from systemEntities import Models
llm = load_validator_model(Models.OPENAI_LANGCHAIN_DEFAULT)

@dataclass
class Answer:
    question: str
    key: Optional[str] = None
    output: Optional[str] = None
    explanation: Optional[str] = None
    is_correct: Optional[bool] = None
    is_partially_correct: Optional[bool] = None
    is_correct_explanation: Optional[str] = None
    answer: Optional[str] = None
    is_cheating: Optional[bool] = None
    is_answer_complete: Optional[bool] = None
    creativity: Optional[int] = None
    correctness: Optional[int] = None
    coverage: Optional[int] = None
    performance: Optional[int] = None
    originality: Optional[int] = None
    likeness_of_cheating: Optional[int] = None

    def __post_init__(self):
        self.is_answer_complete = self.is_complete()
    
    def is_complete(self) -> bool:
        return all([self.question,self.answer, self.key, self.output, self.explanation])
    
class AnswerScoreStructure(BaseModel):
    creativity: int = Field(description="the creativity of the answer", ge=1, le=10)
    correctness: int = Field(description="the correctness of the answer", ge=1, le=10)
    coverage: int = Field(description="the coverage of the answer", ge=1, le=10)
    performance: int = Field(description="the performance of the answer", ge=1, le=10)
    originality: int = Field(description="the originality of the answer", ge=1, le=10)
    likeness_of_cheating: int = Field(description="the likeness of cheating of the answer", ge=1, le=10)

class IncompleteExplinationStructure(BaseModel):
    index: int = Field(description="the index of the answer")
    explanation: str = Field(description="the explanation of why the answer is incomplete")

class QuestionStructure(BaseModel):
    questions: list[str] = Field(description="A list of the main questions from the assignment")

class AnswerStructure(BaseModel):
    question: str = Field(description="question from the assignment")
    answer: str = Field(description="answer from the submission script")
    key: str = Field(description="key from the json output that contains the answer")
    output: str = Field(description="output from the json output")
    explanation: str = Field(description="explanation of how the question, answer and output are related")

class AnswerCorrectStructure(BaseModel):
    is_correct: bool = Field(description="whether the answer is correct or not")
    is_partially_correct: bool = Field(description="whether the answer is partially correct or not")
    explanation: str = Field(description="explanation of how the question, answer and output are related")

class ExtractionError(Exception):
    """Exception raised when there is an error extracting artifacts from a file.
    
    This exception is raised when there are issues reading, decoding, or processing
    files during the artifact extraction process. It provides context about which
    file caused the error and what the specific error was.
    
    Attributes:
        file_name (str): The name of the file that caused the extraction error
        message (str): The specific error message describing what went wrong
    """
    
    def __init__(self, message: str):
        """Initialize the ExtractionError with a descriptive message.
        
        Args:
            message (str): A descriptive message explaining what went wrong during extraction
        """
        self.message = message
        super().__init__(self.message)

class LLMError(Exception):
    """Exception raised when there is an error from the LLM.
    
    This exception is raised when the LLM returns an error or unexpected output.
    """
    def __init__(self, message: str):
        """Initialize the LLMError with a descriptive message.
        
        Args:
            message (str): A descriptive message explaining what went wrong during LLM execution
        """
        self.message = message
        super().__init__(self.message)

@dataclass
class AgentState:
    """
    Represents the state of the agent during its execution.
    """
    assignment_script: str = ""
    submission_script: str = ""
    output_json: str = ""
    answers: List[Answer] = field(default_factory=list)
    current_question_index: int = 0
    agg_score: Dict[str, int] = field(default_factory=lambda: {
        "knowledge": 0,
        "code_quality": 0,
        "authenticity": 0,
        "efficiency": 0
    })
    is_submission_complete: bool = False
    incomplete_explinations: str = field(default_factory=str)
    incorrect_explinations: str = field(default_factory=str)
    cheating_explinations: str = field(default_factory=str)
    is_cheating: bool = False
    is_answer_correct: bool = False


@dataclass
class Artifact:
    artifact_type: Literal["assignment", "submission", "output"]
    file_type: Literal['script','asset','records']
    assignment_id: int  
    task_id: int | None      
    file_name: str
    content: str
    def get_artifact_metadata(self):
        return {
            "artifact_type":self.artifact_type,
            "file_type":self.file_type,
            "assignment_id":self.assignment_id,
            "task_id":self.task_id,
            "file_name":self.file_name,
        }
    def matches(self, query: dict[str, Any]) -> bool:
        return all(getattr(self, key) == value for key, value in query.items())

class Artifacts:
    def __init__(self, artifacts: List[Artifact]):
        self.artifacts = artifacts

    @overload
    def get(self, query: dict[str, Any], single: Literal[True]) -> Artifact: ...

    @overload
    def get(self, query: dict[str, Any], single: Literal[False] = False) -> list[Artifact]: ...

    def get(self, query: dict[str, Any], single: bool = False) -> list[Artifact] | Artifact:
        matches = [art for art in self.artifacts if art.matches(query)]
        if single:
            if not matches:
                raise ValueError(f"No artifact found matching query: {query}")
            return matches[0]
        return matches
    def get_tasks(self) -> list[int]:
        return [art.task_id for art in self.artifacts if art.task_id and art.artifact_type=="submission"]
    @property
    def df(self) -> pd.DataFrame:
        return pd.DataFrame([art.__dict__ for art in self.artifacts])

def get_file_attributes(file_name: str, artifact_type:  Literal["assignment", "submission"]) -> tuple[Literal['script','asset','records'], int, int | None]:
    #print(f"mother::get_file_attributes:: analyzing followin file_name:'{file_name}'")
    file_type_map = {".py":"script",".txt":"asset",".json":"records"}
    match artifact_type:
        case "assignment":
            file_type = cast(Literal['script','asset','records'], file_type_map[Path(file_name).suffix])
            task_id=int(Path(file_name).parts[1])
        case "submission":
            file_type = cast(Literal['script','asset','records'], file_type_map[Path(file_name).suffix])
            task_id=int(Path(file_name).parts[5])
    #print(f"mother::get_file_attributes:: file_type='{file_type}'")
    #print(f"mother::get_file_attributes:: assignment_id='{assignment_id}'")
    #print(f"mother::get_file_attributes:: task_id='{task_id}'")
    return file_type, task_id

def get_artifacts(data_location: BytesIO|str, artifact_type:  Literal["assignment", "submission"], assignment_id:int, task_id:int) -> list[Artifact]:
    #print(f"mother::get_artifacts:: received data_location_type={type(data_location)}")
    artifacts = []
    allowed_suffixes=[".py",".json",".txt"]
    if isinstance(data_location, BytesIO):
        with ZipFile(data_location) as zip_file:
            # List all file names
            file_names = zip_file.namelist()
            file_names = [name for name in file_names if Path(name).suffix in allowed_suffixes]
            for file_name in file_names:
                file_type, retrieved_task_id = get_file_attributes(file_name, artifact_type)
                if(retrieved_task_id==task_id):
                    try:
                        artifacts.append(
                            Artifact(
                                artifact_type = artifact_type,
                                file_type = file_type,
                                assignment_id = assignment_id,
                                task_id = task_id,   
                                file_name = file_name,
                                content=zip_file.read(file_name).decode('utf-8')
                            )
                        )
                    except Exception as e:
                        raise ExtractionError(f"Error extracting artifacts from {file_name}: {e}")
    elif isinstance(data_location, str):
        for root, _, files in os.walk(data_location):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in allowed_suffixes:
                    #print(f"mother::get_artifacts:: data_location='{data_location}'")
                    #print(f"mother::get_artifacts:: file_path='{file_path}'")
                    relative_path = os.path.relpath(file_path, data_location)
                    #print(f"mother::relative_path:: relative_path='{relative_path}'")
                    file_type, retrieved_task_id = get_file_attributes(str(file_path).replace("\\", "/"),artifact_type)
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        artifacts.append(Artifact(
                            artifact_type=artifact_type,
                            file_type=file_type,
                            assignment_id=assignment_id,
                            task_id=task_id,
                            file_name=str(relative_path).replace("\\", "/"),
                            content=content
                        ))
                    except Exception as e:
                        raise ExtractionError(f"Error extracting artifact from DIR {file_path}: {e}")

    else:
        raise TypeError(f"Unsupported data_location type: {type(data_location)}")
    return artifacts

def get_test_data(submitted_task_directory: str, assignment_id:int, task_id:int) -> Artifacts: # only  to be used for testing
    artifacts:list[Artifact] = []
    assignment = BytesIO(Path(f'./resources/static/assignment/{str(assignment_id)}/assignment_{str(assignment_id)}.zip').read_bytes())
    #legit_opened_submission_path="./data/submitted_files/concurrency_user_2/2/3/" # for testing only
    artifacts.extend(get_artifacts(data_location=submitted_task_directory, artifact_type="submission", assignment_id=assignment_id, task_id=task_id))
    artifacts.extend(get_artifacts(data_location=assignment, artifact_type="assignment", assignment_id=assignment_id, task_id=task_id))

    artifactsWithoutContent=[artifact.get_artifact_metadata() for artifact in artifacts]
    print(f"mother::get_test_data:: '{json.dumps(artifactsWithoutContent)}'")
    artifacts = Artifacts(artifacts)
    return artifacts

def extract_questions(state: AgentState) -> AgentState:
    prompt_template = PromptTemplate.from_template(
    """
    Input: You are provided with the following:
    
    - Assignment script: {assignment_script}
    - Submission script: {submission_script}
    - Output JSON: {output_json}

    Validation Criteria:

    - There must be exactly {num_questions} questions.
    - Each question must be labeled using only the following keys: {question_key}

    Task:

    - Identify all "TODO" questions in the assignment script—these are marked with the prefix "TODO".
    - For each identified TODO, extract and interpret the core intent of the task.
    - Rephrase each TODO item into a clear, concise, and student-friendly explanation of the required task.
    
    Example Output format:

      "questions": [
        "<rephrased question 1>",
        "<rephrased question 2>",
        ...
      ]
    
    Output Rules:

    - Only include the questions JSON object in the output—no additional text, comments, or formatting.
    - The value of "questions" must be a Python-style list of the rephrased explanations.
    - Each explanation should be concise, clear, and capture the intended task of the original TODO line.

    Example Transformation:
    Original TODO:
    TODO: fill in the info string with the following information and format it correctly.
    Transformed Explanation:
    "Populate the info string using the given details and ensure proper formatting."
    """
    )
    output_parser = JsonOutputParser(pydantic_object=List[QuestionStructure])
    assert prompt_template is not None, "prompt_template is None"
    assert llm is not None, "llm is None"
    assert output_parser is not None, "output_parser is None"
    chain = prompt_template | llm | output_parser
    try:
        keys = [key for key in json.loads(state.output_json).keys()]
        output = chain.invoke({
            "assignment_script": state.assignment_script,
            "submission_script": state.submission_script,
            "output_json": state.output_json,
            "num_questions":len(keys),  
            "question_key":keys
        })
        state.answers = [Answer(question=item) for item in output['questions']] # Extract just the questions
    except Exception as e:
        print(f"Error extracting questions: {e}")
        raise LLMError(f"Error extracting questions: {e}")
    return state

def extract_answer(state: AgentState) -> AgentState:
    prompt_template = PromptTemplate.from_template(
    """
    You are an expert at evaluating code submissions
    focusing on precise extraction and validation of answers from JSON outputs. 
    Your task is to analyze a student's:
    - submission
    - generated output
    - original assignment's requirements 

    to determine and extract the answer submitted by the student for the specific question specified.

    Input: You are provided with the following:

    - Assignment script: This script contains the original problem statement and possibly expected logic or values.
    ```python
    {assignment_script}
    ```

    - Submission script: This is the student's code attempting to solve the problem.
    ```python
    {submission_script}
    ```

    - Output JSON: This JSON object represents the actual output generated by running the student's submission. 
    The keys in this JSON correspond to the questions asked in the assignment, and their values are the student's computed answers.
    ```json
    {output_json}
    ```

    - Question: This is a rephrased, clear explanation of the specific task or question from the assignment that you need to evaluate.
    please only extract the answer for this specific question
    {question}

    Task:
    1.  **Identify the Relevant Key**: Based on the `Question`, determine the most relevant key within the `Output JSON` that holds the student's answer to this question.
    2.  **Extract the Answer Value**: Retrieve the *exact* value associated with the identified key from the `Output JSON`. This value is the student's answer.
    3.  **Extract the key**: extract the single key from the json output that contains the output associated with the question and answer
    4.  **extract the output**: extract the output from the json output from the key only
    5.  **explanation**: provide a comprehensive explanation for your decision. This explanation MUST:
        * Explicitly state the exact key from the `Output JSON` that contained the answer.
        * Quote the *exact* extracted answer value.
        * Clearly articulate how this extracted answer fulfills or fails to fulfill the requirements of the `Question` and `Assignment script`.

    Output Format: Please provide a JSON object adhering strictly to the following `AnswerStructure` schema. Ensure all fields are populated correctly and the `answer` and `extracted_json_key` are direct, identical extractions from the `Output JSON`.

    ```json
        "question": "{question}", // The question you were asked to evaluate
        "answer": str, // The answer extractedfrom the submission script
        "key": str, // The key from the json output that contains the answer
        "output": str, // The output extracted from the json output from the key only
        "explanation": str // The explanation of how the question, answer and output are related
    ```
    Note:
    Crucial Rule: 
    The question, answer, key, and output fields in your output JSON must be directly verifiable as existing within the provided input and accurately representing the content. 
    DO NOT paraphrase or summarize the question, answer, or output; provide them exactly as found or as they should be presented verbatim.
    """
    )

    output_parser = JsonOutputParser(pydantic_object=AnswerStructure)
    chain = prompt_template | llm | output_parser
    new_answers = []
    for answer in state.answers:
        try:
            extracted_answer = chain.invoke({
                "assignment_script": state.assignment_script,
                "submission_script": state.submission_script,
                "output_json": state.output_json,
                "question": answer.question
            })
            extracted_answer = AnswerStructure(**extracted_answer)
            new_answers.append(
                Answer(
                    question=answer.question, 
                    answer=extracted_answer.answer, 
                    key=extracted_answer.key, 
                    output=extracted_answer.output, 
                    explanation=extracted_answer.explanation
               )
            )
        except Exception as e:
            raise LLMError(f"Error extracting answer for question {answer.question}: {e}")
    state.answers = new_answers
    return state

def check_is_answer_correct(state: AgentState) -> AgentState:
    prompt_template = PromptTemplate.from_template(
    """
    given the following answer and the assignment script, determine if the answer is correct or not
    - assignment script: {assignment_script}
    - question: {question}
    - answer: {answer}
    - output: {output}

    Output Format: Please provide a JSON object adhering strictly to the following `AnswerCorrectStructure` schema. Ensure all fields are populated correctly and the `answer` and `extracted_json_key` are direct, identical extractions from the `Output JSON`.
    ```json
        "is_correct": bool, // Whether the answer is correct or not
        "is_partially_correct": bool, // Whether the answer is partially correct or not
        "explanation": str // The explanation of how the question, answer and output are related
    ```
    judgement criteria:
    - if the answer is correct, the is_correct field should be true and the is_partially_correct field should be false
    - if the answer is wrong, the is_correct field should be false and the is_partially_correct field should be false
    - if the answer is partially correct, the is_correct field should be false and the is_partially_correct field should be true
    
    - the explanation should be a comprehensive explanation for your decision. This explanation MUST:
        * explain why the answer is correct or incorrect
        * explain why the answer is partially correct
        * use answer and output to explain the explanation
    """
    )

    output_parser = JsonOutputParser(pydantic_object=AnswerCorrectStructure)
    chain = prompt_template | llm | output_parser
    new_answers = []
    for answer in state.answers:
        try:
            answer_correct = chain.invoke({
                "assignment_script": state.assignment_script,
                "question": answer.question,
                "answer": answer.answer,
                "output": answer.output
            })
            answer_correct = AnswerCorrectStructure(**answer_correct)
            new_answers.append(
                Answer(
                    question=answer.question, 
                    answer=answer.answer, 
                    key=answer.key, 
                    output=answer.output, 
                    explanation=answer_correct.explanation,
                    is_correct=answer_correct.is_correct,
                    is_partially_correct=answer_correct.is_partially_correct,
                    is_correct_explanation=answer_correct.explanation
                ))
        except Exception as e:
            raise LLMError(f"Error extracting answer for question '{answer.question}': {e}")
    state.answers = new_answers
    return state

def answer_scores(state: AgentState) -> AgentState:
    prompt_template = PromptTemplate.from_template(
    """
    You are an expert code evaluator. Evaluate the following submission based on the provided criteria:

    Input:
    - Assignment script: {assignment_script}
    - Question: {question}
    - Student's answer: {answer}
    - Correctness status: {is_correct}
    - Partial correctness: {is_partially_correct}
    - Correctness explanation: {is_correct_explanation}

    
    Evaluation Criteria (Score each from 1-10):

    1. Creativity (1-10):
       - How innovative is the solution approach?
       - Does it show unique problem-solving methods?
       - Does it demonstrate thinking outside the box?

    2. Correctness (1-10):
       - How accurately does it solve the problem?
       - Does it meet all requirements?
       - Are there any logical errors?

    3. Coverage (1-10):
       - How thoroughly does it address the problem?
       - Does it handle edge cases?
       - Is the solution comprehensive?

    4. Performance (1-10):
       - How efficient is the solution?
       - Is the code optimized?
       - Are there any unnecessary operations?

    5. Originality (1-10):
       - How unique is the implementation?
       - Does it avoid common/cliché solutions?
       - Is there evidence of independent thinking?

    6. likeness_of_cheating (1-10):
       - 1: Clearly original work
       - 5: Some similarities to common solutions
       - 10: Strong evidence of copying

    Output Format: 
    Provide a JSON object with scores for each metric (1-10):
    ```json
        "creativity": int,      // Score for innovative approach
        "correctness": int,     // Score for accuracy
        "coverage": int,        // Score for thoroughness
        "performance": int,     // Score for efficiency
        "originality": int,     // Score for uniqueness
        "likeness_of_cheating": int  // Score for originality    
    ```

    note regarding cheating:
    - these are beginer coders that are not allowed to copy paste from LLM output
    - if the code contains advanced concepts that are not within the scope of the assignment, the likeness of cheating should be high
    - if the code contains over relience on comments or doc strings, the likeness of cheating should be high
    - if the code feels like it was written by an AI, the likeness of cheating should be high
    - accusations of cheating should be made with extreme caution, and only when there is clear evidence

    Guidelines:
    - The score should be between 1 and 10
    - default score is 5
    - if the answer demonstrates exceptional metric the score should be 9 or 10
    - if the answer demonstrates poor metric the score should be 1 or 2
    
    Important:
    - only provide the number no other text
    - Consider both the code quality and the approach
    - Be objective and consistent in scoring
    """
    )

    output_parser = JsonOutputParser(pydantic_object=AnswerScoreStructure)
    chain = prompt_template | llm | output_parser
    new_answers = []
    for answer in state.answers:
        try:
            answer_correct = chain.invoke({
                "assignment_script": state.assignment_script,
                "question": answer.question,
                "answer": answer.answer,
                "is_correct": answer.is_correct,
                "is_partially_correct": answer.is_partially_correct,
                "is_correct_explanation": answer.is_correct_explanation
            })
            answer_correct = AnswerScoreStructure(**answer_correct)
            new_answers.append(
                Answer(
                    question=answer.question, 
                    answer=answer.answer, 
                    key=answer.key, 
                    output=answer.output, 
                    explanation=answer.explanation,
                    is_correct=answer.is_correct,
                    is_partially_correct=answer.is_partially_correct,
                    is_correct_explanation=answer.is_correct_explanation,
                    creativity=answer_correct.creativity,
                    correctness=answer_correct.correctness,
                    coverage=answer_correct.coverage,
                    performance=answer_correct.performance,
                    originality=answer_correct.originality,
                    likeness_of_cheating=answer_correct.likeness_of_cheating
                ))
        except Exception as e:
            raise LLMError(f"Error extracting answer for question '{answer.question}': {e}")
    state.answers = new_answers
    return state

def incomplete_explination(state: AgentState) -> AgentState:
    prompt_template = PromptTemplate.from_template(
    """
    You are an expert code evaluator. Analyze the following submission to identify any incomplete aspects of the answer.

    Input:
    - Assignment Requirements: {assignment_script}
    - Student's Submission: {submission_script}
    - Output Data: {output_json}
    - Question: {question}
    - Student's Answer: {answer}
    - Generated Output: {output}
    - Question Index: {index}

    Evaluation Criteria for Completeness:
    1. Required Components:
       - Are all required elements present in the answer?

    2. Output Requirements:
       - Does the output match the expected format?
       - Are all required fields present in the output?

    Output Format:
    Provide a JSON object with:
    ```json
        "index": int,      // The question index
        "explanation": str // A clear, professional explanation of why the answer is incomplete
    ```

    Guidelines for Explanation:
    - Be specific about what is missing or incomplete
    - Reference the assignment requirements
    - Provide constructive feedback
    - Use professional, objective language
    - Focus on the technical aspects of the incompleteness
    """
    )

    output_parser = JsonOutputParser(pydantic_object=IncompleteExplinationStructure)
    chain = prompt_template | llm | output_parser
    incomplete_explinations = []
    for index, answer in enumerate(state.answers):
        try:
            incomplete_explination = chain.invoke({
                "assignment_script": state.assignment_script,
                "submission_script": state.submission_script,
                "output_json": state.output_json,
                "question": answer.question,
                "answer": answer.answer,
                "output": answer.output,
                "index": index  
            })
            incomplete_explination = IncompleteExplinationStructure(**incomplete_explination)
            incomplete_explinations.append(f"Question {index + 1}: {incomplete_explination.explanation}\n")
        except Exception as e:
            raise LLMError(f"Error extracting answer for question '{answer.question}': {e}")
    state.incomplete_explinations = "\n".join(incomplete_explinations)
    return state

def incorrect_explination(state: AgentState) -> AgentState:
    prompt_template = PromptTemplate.from_template(
    """
    You are an expert code evaluator. Analyze the following submission to identify why the answer is incorrect.

    Input:
    - Assignment Requirements: {assignment_script}
    - Student's Submission: {submission_script}
    - Output Data: {output_json}
    - Question: {question}
    - Student's Answer: {answer}
    - Generated Output: {output}
    - Question Index: {index}

    Evaluation Criteria for Incorrectness:
    1. Logical Errors:
       - Are there any logical flaws in the solution?
       - Does the code produce incorrect results?
       - Are there any mathematical or algorithmic errors?

    2. Output Requirements:
       - Does the output match the expected format?
       - Are the values in the output correct?
       - Is the output properly formatted?

    Output Format:
    Provide a JSON object with:
    ```json
        "index": int,      // The question index
        "explanation": str // A clear, professional explanation of why the answer is incorrect
    ```

    Guidelines for Explanation:
    - Be specific about what is incorrect
    - Reference the assignment requirements
    - Provide constructive feedback
    - Use professional, objective language
    - Focus on the technical aspects of the incorrectness
    """
    )

    output_parser = JsonOutputParser(pydantic_object=IncompleteExplinationStructure)
    chain = prompt_template | llm | output_parser
    incorrect_explinations = []
    for index, answer in enumerate(state.answers):
        try:
            incorrect_explanation = chain.invoke({
                "assignment_script": state.assignment_script,
                "submission_script": state.submission_script,
                "output_json": state.output_json,
                "question": answer.question,
                "answer": answer.answer,
                "output": answer.output,
                "index": index  
            })
            incorrect_explanation = IncompleteExplinationStructure(**incorrect_explanation)
            incorrect_explinations.append(f"Question {index + 1}: {incorrect_explanation.explanation}\n")
        except Exception as e:
            raise LLMError(f"Error extracting answer for question '{answer.question}': {e}")
    state.incorrect_explinations = "\n".join(incorrect_explinations)
    return state

def cheating_explination(state: AgentState) -> AgentState:
    prompt_template = PromptTemplate.from_template(
    """
    You are an expert code evaluator. Analyze the following submission to identify potential academic integrity concerns.

    Input:
    - Assignment Requirements: {assignment_script}
    - Student's Submission: {submission_script}
    - Output Data: {output_json}
    - Question: {question}
    - Student's Answer: {answer}
    - Generated Output: {output}
    - Question Index: {index}

    Evaluation Criteria for Academic Integrity:
    1. Code Complexity:
       - Does the code contain concepts beyond the assignment scope?
       - Is there evidence of advanced programming techniques not covered in class?
       - Are there sophisticated optimizations that seem out of place?

    2. Documentation Patterns:
       - Is there excessive or overly detailed documentation?
       - Do comments seem to be copied from external sources?
       - Are there inconsistencies between code and comments?

    3. Implementation Style:
       - Does the coding style match the student's previous work?
       - Are there sudden improvements in code quality?
       - Is there evidence of AI-generated code patterns?

    Output Format:
    Provide a JSON object with:
    ```json
        "index": int,      // The question index
        "explanation": str // A clear, professional explanation of academic integrity concerns
    ```

    Guidelines for Explanation:
    - Be extremely cautious in making accusations
    - Focus on specific evidence rather than assumptions
    - Use professional, objective language
    - Consider the student's level and course context
    - Provide specific examples of concerning patterns
    """
    )

    output_parser = JsonOutputParser(pydantic_object=IncompleteExplinationStructure)
    chain = prompt_template | llm | output_parser
    cheating_explinations = []
    for index, answer in enumerate(state.answers):
        try:
            cheating_explanation = chain.invoke({
                "assignment_script": state.assignment_script,
                "submission_script": state.submission_script,
                "output_json": state.output_json,
                "question": answer.question,
                "answer": answer.answer,
                "output": answer.output,
                "index": index  
            })
            cheating_explanation = IncompleteExplinationStructure(**cheating_explanation)
            cheating_explinations.append(f"Question {index + 1}: {cheating_explanation.explanation}\n")
        except Exception as e:
            raise LLMError(f"Error extracting answer for question '{answer.question}': {e}")
    state.cheating_explinations = "\n".join(cheating_explinations)
    return state

def check_submission_complete(state: AgentState) -> AgentState:
    check_not_none = [state.assignment_script, state.submission_script, state.output_json]
    answer_checks = [answer.is_answer_complete for answer in state.answers]
    if all(check_not_none) and all(answer_checks):
        state.is_submission_complete = True
    else:
        state.is_submission_complete = False
    return state

def check_submission_complete_condition(state: AgentState) -> bool:
    return state.is_submission_complete

def check_answer_correct_condition(state: AgentState) -> Literal["correct", "incorrect", "cheating"]:
    if state.is_cheating:
        return "cheating"
    if state.is_answer_correct:
        return "correct"
    else:
        return "incorrect"

def create_agent_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    graph.add_node("extract_questions", extract_questions)
    graph.add_node("extract_answer", extract_answer)
    graph.add_node("check_submission_complete",check_submission_complete)
    graph.add_node("incomplete_explination", incomplete_explination)
    graph.add_node("check_is_answer_correct", check_is_answer_correct)
    graph.add_node("answer_scores", answer_scores)
    graph.add_node("incorrect_explination", incorrect_explination)
    graph.add_node("cheating_explination", cheating_explination)
    graph.set_entry_point("extract_questions")
    graph.add_edge("extract_questions", "extract_answer")
    graph.add_edge("extract_answer", "check_submission_complete")
    graph.add_edge("check_is_answer_correct", "answer_scores")
    graph.add_conditional_edges(
        "check_submission_complete",
        check_submission_complete_condition,
        {
            True: "check_is_answer_correct",
            False: "incomplete_explination"
        }
    )
    
    graph.add_conditional_edges(
        "answer_scores",
        check_answer_correct_condition,
        {
            "correct": END,
            "incorrect": "incorrect_explination",
            "cheating": "cheating_explination"
        }
    )
    
    # Add edges for explanation flow
    graph.add_edge("incomplete_explination", END)
    graph.add_edge("incorrect_explination", END)
    graph.add_edge("cheating_explination", END)
    

    return graph

def run_agent_for_task(artifacts: Artifacts) -> AgentState:
    initial_state = AgentState(
        assignment_script = artifacts.get({"artifact_type": "assignment", "file_type": "script"}, single=True).content,
        submission_script = artifacts.get({"artifact_type": "submission", "file_type": "script"}, single=True).content,
        output_json = artifacts.get({"artifact_type": "submission", "file_type": "records"}, single=True).content,
        answers = [],
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
    return cast(AgentState, runnable.invoke(initial_state))

def execute_task(task_file_name :str, kill_timeout: float):
    #print(f"mother::execute_task:: task_file_name='{task_file_name}'")
    submitted_task_directory=os.path.dirname(task_file_name)
    
    print(f"mother::execute_task:: submitted_task_directory='{submitted_task_directory}'")
    assignment_id=int(Path(submitted_task_directory).parts[3])
    task_id=int(Path(submitted_task_directory).parts[5])
    
    print(f"mother::execute_task:: assignment_id='{assignment_id}'")
    print(f"mother::execute_task:: task_id='{task_id}'")

    artifacts = get_test_data(submitted_task_directory, assignment_id, task_id)

    validation_state = run_agent_for_task(artifacts)
    #breakpoint()
    #print(f"execute_task:: validation_state.keys()                      ='{validation_state.keys()                    }'")
    #print(f"execute_task:: validation_state['agg_score']                ='{validation_state['agg_score']              }'")
    #print(f"execute_task:: validation_state['is_answer_correct']        ='{validation_state['is_answer_correct']      }'")
    #print(f"execute_task:: validation_state['incorrect_explinations']   ='{validation_state['incorrect_explinations'] }'")
    #print(f"execute_task:: validation_state['is_submission_complete']   ='{validation_state['is_submission_complete'] }'")
    #print(f"execute_task:: validation_state['incomplete_explinations']  ='{validation_state['incomplete_explinations']}'")
    #print(f"execute_task:: validation_state['is_cheating']              ='{validation_state['is_cheating']            }'")
    #print(f"execute_task:: validation_state['cheating_explinations']    ='{validation_state['cheating_explinations']  }'")
    #dict_keys(['assignment_script', 'submission_script', 'output_json', 'answers', 'current_question_index', 'agg_score', 'is_submission_complete', 'incomplete_explinations', 'incorrect_explinations', 'cheating_explinations', 'is_cheating', 'is_answer_correct'])
    validator_response = {
        "agg_score": validation_state['agg_score'],
        "status": "PASS" if validation_state['is_answer_correct'] else "FAIL",
        "is_answer_correct": validation_state['is_answer_correct'],
        "is_submission_complete": validation_state['is_submission_complete'],
        "is_cheating": validation_state['is_cheating'],
        **({"status_fail_explenation":  validation_state['incorrect_explinations']}  if not validation_state['is_answer_correct'] else {}),
        **({"incomplete_explinations":  validation_state['incomplete_explinations']} if not validation_state['is_submission_complete'] else {}),
        **({"cheating_explinations":    validation_state['cheating_explinations']}   if validation_state['is_cheating'] else {}),
    }
    return validator_response