import os, json, random, string
import mailService
from systemEntities import User,NotificationTemplate

USER_DATA_FILE = os.path.join("./data/","user_data.json")

def load_data(file_type: str = "user"):
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    return []
        
def save_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def random_string():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))

def submit_user(user: User):
    data = load_data()
    user_laready_exists=len(list(filter(lambda existing_user: user.email==existing_user["email"],data)))>0
    if(user_laready_exists):
        return {"status":"ERROR", "ERROR_message":"mail address is already registered"}
    else:
        hacker_id=random_string()
        while len(list(filter(lambda existing_user: existing_user["hacker_id"]==hacker_id,data)))>0:
            hacker_id=random_string()
        user.hacker_id=hacker_id
        new_entry = user.dict()
        data.append(new_entry)
        save_data(data)
        mailService.notification_producer(user=user,notification_type=NotificationTemplate.CANDIDATE_KID_INTRO)
        return {"status":"SAVED", "message": "User saved", "user": new_entry}
