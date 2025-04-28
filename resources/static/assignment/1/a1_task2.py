import socket
import os
import sys
from pathlib import Path
import json
sys.path.append(str(Path.cwd()))

def task_2()-> None:
    """
    This task analyzes the text of "Alice in Wonderland" and extracts specific information:
    
    Tasks:
    1. Count the number of times the word "king" appears in the text, regardless of case.
    2. Find and extract a sentence that contains the word "hatter" near the middle of the sentence 
       and limit the sentence to 200 characters.
    3. Count the total number of words in the text.
    
    The results are saved as a JSON dictionary to a file called "alice_in_wonderland_questions.txt" with the keys:
    - "number_of_times_king": <int>
    - "sentence_with_hatter": <str>
    - "words_in_text": <int>
    """
    alice_in_wonderland = Path("alice_in_wonderland.txt").read_text(encoding="utf-8", errors="ignore")
    
    # TODO: : fill in the variable number_of_times_king with the number of times the word "king" appears in the text file both upper and lower case.
    number_of_times_king = 0
    
    # TODO: : fill in the variable sentence_with_hatter with a 200 character sentence that contains the word hatter in the middle.
    sentence_with_hatter = ""

    # TODO: : fill in the variable words_in_text with the number of words in the text file.
    words_in_text = 0

    # Write the information to a file
    Path("a1_task2.json").write_text(json.dumps({
        "number_of_times_king":number_of_times_king, 
        "sentence_with_hatter":sentence_with_hatter,
        "words_in_text":words_in_text
        }), encoding="utf-8", errors="ignore")
    
if __name__ == "__main__":
    task_2()