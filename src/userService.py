import os, json, random, string
from pydantic import BaseModel

USER_DATA_FILE = os.path.join("./data/","user_data.json")

def load_data(file_type: str = "user"):
    if file_type == "user":
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, "r") as f:
                return json.load(f)
        return []
    elif file_type == "assignment":
        if os.path.exists(ASSIGNMENT_DATA_FILE):
            with open(ASSIGNMENT_DATA_FILE, "r") as f:
                return json.load(f)
        return {}
    else:
        raise Exception(f"no data file of type '{file_type}'")
        
def save_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class User(BaseModel):
    email: str
    hacker_id: str
    name: str
    phone: str

def random_string():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))

def submit_user(user: User):
    data = load_data()
    
    # Check if email exists and update
    # for entry in data:
    #     if entry["email"] == user.email:
    #         entry["name"] = user.name
    #         entry["phone"] = user.phone
    #         save_data(data)
    #         return {"message": "User updated", "user": entry}
    
    # Add new user
    hacker_id=random_string()
    while len(list(filter(lambda user: user["hacker_id"]==hacker_id,data)))>0:
        hacker_id=random_string()
    new_entry = user.dict()
    new_entry["hacker_id"]=hacker_id
    data.append(new_entry)
    save_data(data)
    return {"message": "User saved", "user": new_entry}