import os, json, random, string
import mailService
from systemEntities import User,NotificationType

USER_DATA_FILE = os.path.join("./data/","user_data.json")

def load_data():
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
        new_entry["paid_status"]=False
        data.append(new_entry)
        save_data(data)
        mailService.notification_producer(user=user,notification_type=NotificationType.CANDIDATE_KID_INTRO)
        return {"status":"SAVED", "message": "User saved", "user": new_entry}

def get_user(hacker_id:str) -> User:
    data = load_data()
    user=list(filter(lambda existing_user: hacker_id==existing_user["hacker_id"],data))
    if(len(user)>0):
        return {"status":"OK","user":user[0]}
    else:
        return {"status":"ERROR", "ERROR_message":f"user with hacker_id='{hacker_id}' does not exist"}

def user_exists(email:str) -> bool:
    data = load_data()
    user=list(filter(lambda existing_user: email==existing_user["email"],data))
    return len(user)>0

def initiate_user_payement_procedure(hacker_id:str, ClientName:str, ClientLName:str, UserId:str, email:str, phone:str):
    print(f"initiate_user_payement_procedure for user {hacker_id} with following details:ClientName:{ClientName}, ClientLName:{ClientLName}, UserId:{UserId}, email:{email}, phone:{phone}")
    print("unimplemented procedure, setting user as paied by default")
    set_user_as_paid(hacker_id)

def set_user_as_paid(hacker_id:str):
    data = load_data()
    user=list(filter(lambda existing_user: hacker_id==existing_user["hacker_id"],data))
    if(len(user)>0):
        user[0]["paid_status"]=True
    print (data)
    save_data(data)

def is_usr_paied(hacker_id: str):
    return get_user["usr"]["paid_status"]
