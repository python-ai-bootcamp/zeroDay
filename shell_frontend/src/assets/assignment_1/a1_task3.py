import sys
from pathlib import Path
sys.path.append(str(Path.cwd()))
import json




def task_3() -> None:
    """
    write a task that takes a string, and target_word and return n characters with the target_word in the middle.
    run this task on the alice_in_wonderland text file and the first time rabbit speaks
    """

    alice_in_wonderland = Path("alice_in_wonderland.txt").read_text(encoding="utf-8", errors="ignore")

    def get_n_characters(text:str, target_word:str, n:int) -> str:
        """
        This function takes a string, a target word, and an integer n.
        It returns n characters with the target word in the middle.
        """
        # TODO: : Complete this function.
        return ""
    

    # TODO: : fill in the variable first_time_rabbit_speaks with the text that the white rabbit speaks for the first time.
    # use the get_n_characters function until you find it, document the processing and result.
    first_time_rabbit_speaks = ""

    # Write the information to a file
    Path("a1_task1.json").write_text(json.dumps({"first_time_rabbit_speaks": first_time_rabbit_speaks}), encoding="utf-8", errors="ignore")
    




    



if __name__ == "__main__":
    task_3()