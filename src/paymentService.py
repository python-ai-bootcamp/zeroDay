import os,json
from systemEntities import User, print
from mailService import notification_producer
from systemEntities import NotificationType
from collections import OrderedDict
from userService import set_user_as_paid

PAYMENT_DATA_DIRECTORY = os.path.join("./data/", "payment_data")
LAST_RECEIPT_INDEX_FILE = os.path.join(PAYMENT_DATA_DIRECTORY, "last_receipt_index.dat")
PAYMENT_DATA_FILES_DIRECTORY = os.path.join(PAYMENT_DATA_DIRECTORY, "files")
os.makedirs(PAYMENT_DATA_FILES_DIRECTORY,exist_ok=True)

def get_receipt_index():
    if os.path.exists(LAST_RECEIPT_INDEX_FILE):
        with open(LAST_RECEIPT_INDEX_FILE, "r") as f:
            last_receipt_index= int(f.read())
    else:
        last_receipt_index=0

    with open(LAST_RECEIPT_INDEX_FILE, "w") as f:
        f.write(str(last_receipt_index+1))

    return str(last_receipt_index+1).zfill(7)


def initiate_user_payement_procedure(user:User, ClientName:str, ClientLName:str, UserId:str, email:str, phone:str, amount: int):
    print(f"initiate_user_payement_procedure:: received user {user} with following credit api related details:ClientName:{ClientName}, ClientLName:{ClientLName}, UserId:{UserId}, email:{email}, phone:{phone}")
    print("initiate_user_payement_procedure:: not fully implemented procedure, setting user as paid by default")
    payment_succeeded=True
    if payment_succeeded:
        receipt_index=get_receipt_index()
        set_user_as_paid(user.hacker_id, receipt_index)
        persist_payment_data(receipt_index, user, ClientName, ClientLName, UserId, email, phone, amount)
        produceRecieptMail(receipt_index, user, ClientName, ClientLName, UserId, email, phone, amount)
        persistRecieptInPdfFormat(user)
    else:
        print("initiate_user_payement_procedure:: unimplemented yet, payment unsuccessful, need to convey error in some way,redirection to error page or something")

def persist_payment_data(receipt_index: str, user:User, ClientName:str, ClientLName:str, UserId:str, email:str, phone:str, amount:int):
    with open(os.path.join(PAYMENT_DATA_FILES_DIRECTORY,f"{receipt_index}.json"), "w", encoding="utf-8") as f:
        json.dump({"user":user.dict(), "ClientName":ClientName, "ClientLName":ClientLName, "UserId":UserId, "email": email, "phone": phone, "amount":amount}, f, indent=4, ensure_ascii=False)

def produceRecieptMail(receipt_index: str, user:User, ClientName:str, ClientLName:str, UserId:str, email:str, phone:str, amount:int):
    notification_producer(user=user,notification_type=NotificationType.PAYMENT_ACCEPTED,optional_template_fields=[("$${{ClientName}}$$",ClientName),("$${{ClientLName}}$$",ClientLName)])

def persistRecieptInPdfFormat(user:User):
    print("persistRecieptInPdfFormat:: not yet implemented")
