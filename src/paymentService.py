import os,json
from systemEntities import User, Payment, print
from mailService import notification_producer
from systemEntities import NotificationType
from userService import set_user_as_paid
from pydantic import BaseModel

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

#!!!!!!!!!!!!!!!!!!!! NOTE:: need to set the payment to systemEntities and just pass it around and update it as needed instead of copying each parameter every time
# in addition need to just automatically convert all flat fields of future payment object into array of ($${{fieldName}}$$, $${{fieldValue}}) tuples to save verbosity of passing each field individually
def initiate_user_payement_procedure(payment:Payment):
    print(f"initiate_user_payement_procedure:: received user payment with following credit api related payment:{payment.dict()}")
    payment_succeeded=get_payment_status()
    if payment_succeeded:
        payment.receipt_index=get_receipt_index()
        set_user_as_paid(payment)
        persist_payment_data(payment)
        produceRecieptMail(payment)
        persistRecieptInPdfFormat(payment)
    else:
        print("initiate_user_payement_procedure:: unimplemented yet, payment unsuccessful, need to convey error in some way,redirection to error page or something")

def get_payment_status():
    print("get_payment_status:: not yet implemented, returning True until it does")
    return True

def persist_payment_data(payment:Payment):
    with open(os.path.join(PAYMENT_DATA_FILES_DIRECTORY,f"{payment.receipt_index}.json"), "w", encoding="utf-8") as f:
        json.dump(payment.dict(), f, indent=4, ensure_ascii=False)

def produceRecieptMail(payment:Payment):
    optional_template_fields=[(f"$${{{{{k}}}}}$$",v) for k,v in payment.model_dump().items()]
    notification_producer(user=payment.user,notification_type=NotificationType.PAYMENT_ACCEPTED,optional_template_fields=optional_template_fields)

def persistRecieptInPdfFormat(payment:Payment):
    print("persistRecieptInPdfFormat:: not yet implemented")
