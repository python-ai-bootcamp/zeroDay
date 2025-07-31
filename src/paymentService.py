import os, json, csv, hashlib
from systemEntities import User, Payment, print
from mailService import notification_producer
from systemEntities import NotificationType
from userService import set_user_as_paid
from threading import Lock
from fastapi import BackgroundTasks
from datetime import datetime
import time,zoneinfo

israel_tz = zoneinfo.ZoneInfo("Asia/Jerusalem")
utc_tz = zoneinfo.ZoneInfo("UTC")

try:
    from weasyprint import HTML
    import logging
    logging.getLogger("weasyprint").setLevel(logging.ERROR)
    logging.getLogger('fontTools').setLevel(logging.WARNING)
    logging.getLogger('fontTools.subset').setLevel(logging.WARNING)
    logging.getLogger('fontTools.ttLib').setLevel(logging.WARNING)
    logging.getLogger('fontTools.ttLib.ttFont').setLevel(logging.WARNING)
except ImportError:
    print("WeasyPrint is not installed. Please install it with: pip install weasyprint")
except Exception as e:
    print("caughed an unexpected exception while importing weasyprint, probably missing OS dependencies. please investigate stack")
    print(e)

PAYMENT_DATA_DIRECTORY = os.path.join("./data/", "payment_data")
LAST_RECEIPT_INDEX_FILE = os.path.join(PAYMENT_DATA_DIRECTORY, "last_receipt_index.dat")
PAYMENT_DATA_FILES_DIRECTORY = os.path.join(PAYMENT_DATA_DIRECTORY, "files")
PAYMENT_DATA_CANDIDATE_FILES_DIRECTORY = os.path.join(PAYMENT_DATA_DIRECTORY, "candidate_files")
PAYMENT_DATA_RECEIPTS_DIRECTORY = os.path.join(PAYMENT_DATA_DIRECTORY, "receipts")
PAYMENT_DATA_RECEIPTS_CSV_FILE = os.path.join(PAYMENT_DATA_RECEIPTS_DIRECTORY, "aggregated_payment_data.csv")
PAYMENT_CODES = os.path.join( "./resources","uncommitted_configurations", "payment_codes.json")
os.makedirs(PAYMENT_DATA_FILES_DIRECTORY,exist_ok=True)
os.makedirs(PAYMENT_DATA_CANDIDATE_FILES_DIRECTORY,exist_ok=True)
os.makedirs(PAYMENT_DATA_RECEIPTS_DIRECTORY,exist_ok=True)

def hash_key(key: str) -> str:
    # Create a SHA-256 hash object
    sha256 = hashlib.sha256()
    
    # Update the hash object with the key encoded as bytes
    sha256.update(key.encode('utf-8'))
    
    # Return the hexadecimal representation of the hash
    return sha256.hexdigest()


def get_payment_code_hashes()->list[str]:
    with open(PAYMENT_CODES, "r") as f:
        payment_codes:list[str]= list(json.load(f).keys())
    return [hash_key(payment_code) for payment_code in payment_codes]

def get_amount_per_payment_code(payment_code:str, currency: str):
    with open(PAYMENT_CODES, "r") as f:
        payment_codes= json.load(f)
        if payment_code in payment_codes:
            return payment_codes[payment_code][currency]
        else:
            return payment_codes["regular"][currency]

_persistency_lock=Lock()
def load_csv():
    data = []
    if os.path.exists(PAYMENT_DATA_RECEIPTS_CSV_FILE):
        with open(PAYMENT_DATA_RECEIPTS_CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    return data

def save_csv(data):
    fieldnames = set()
    for row in data:
        fieldnames.update(row.keys())
    fieldnames = sorted(fieldnames)
    with open(PAYMENT_DATA_RECEIPTS_CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def append_row(data, new_row):
    data.append(new_row)

def get_receipt_index():
    if os.path.exists(LAST_RECEIPT_INDEX_FILE):
        with open(LAST_RECEIPT_INDEX_FILE, "r") as f:
            last_receipt_index= int(f.read())
    else:
        last_receipt_index=0

    with open(LAST_RECEIPT_INDEX_FILE, "w") as f:
        f.write(str(last_receipt_index+1))

    return str(last_receipt_index+1).zfill(7)
def payment_notification_flow(payment_candidate_uuid:str, payment_notify_details: dict, background_tasks: BackgroundTasks):
    enrich_payment_candidate_data(payment_candidate_uuid, payment_notify_details, "payment_notify_url_data")
    if(payment_notify_details["processor_response_code"]=="000"):
        file_path = os.path.join(PAYMENT_DATA_CANDIDATE_FILES_DIRECTORY, f"{payment_candidate_uuid}.json")
        # Read existing JSON
        with open(file_path, "r", encoding="utf-8") as f:
            payment_candidate_data = json.load(f)
        required_amount=str(get_amount_per_payment_code(payment_code=payment_candidate_data["paymentCode"], currency=payment_candidate_data["currencyName"]))
        paid_amount=payment_notify_details["sum"]
        if(required_amount==paid_amount):
            payment=Payment.model_validate(payment_candidate_data)
            initiate_user_payement_procedure(payment, background_tasks)
            print(f"paymentService::payment_notification_flow:: payment successfull for {payment_candidate_uuid=}")
        else:
            print(f"paymentService::payment_notification_flow:: {required_amount=} is not equal to {paid_amount=}")
    else:
        print(f"paymentService::payment_notification_flow:: {payment_candidate_uuid=} failed payment attempt with {payment_notify_details["processor_response_code"]=}")

def initiate_user_payement_procedure(payment:Payment, background_tasks: BackgroundTasks):
    print(f"paymentService::initiate_user_payement_procedure:: received user payment with following credit api related payment:{payment.model_dump()}")
    payment.receipt_index=get_receipt_index()
    payment.amount=get_amount_per_payment_code(payment.paymentCode, payment.currencyName)
    set_user_as_paid(payment)
    persist_payment_data(payment)
    produce_reciept_mail(payment)
    background_tasks.add_task(persist_payment_data_in_admissible_formats, payment)

def persist_payment_data(payment:Payment):
    with open(os.path.join(PAYMENT_DATA_FILES_DIRECTORY,f"{payment.receipt_index}.json"), "w", encoding="utf-8") as f:
        json.dump(payment.model_dump(), f, indent=4, ensure_ascii=False)

def persist_payment_candidate_data(payment:Payment):
    print("paymentService::persist_payment_candidate_data:: entered entered with payment=",payment)
    with open(os.path.join(PAYMENT_DATA_CANDIDATE_FILES_DIRECTORY,f"{payment.payment_candidate_uuid}.json"), "w", encoding="utf-8") as f:
        json.dump(payment.model_dump(), f, indent=4, ensure_ascii=False)

def enrich_payment_candidate_data(payment_candidate_uuid:str, additional_payment_data: dict, entry_name:str):    
    print(f"paymentService::enrich_payment_candidate_data:: entered entered with {payment_candidate_uuid=} and {additional_payment_data=}")
    file_path = os.path.join(PAYMENT_DATA_CANDIDATE_FILES_DIRECTORY, f"{payment_candidate_uuid}.json")
    # Read existing JSON
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Add or overwrite the 'additional_payment_data' field
    data[entry_name] = additional_payment_data
    # Write back to the same file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_hacker_id_from_candidate(payment_candidate_uuid:str):
    file_path = os.path.join(PAYMENT_DATA_CANDIDATE_FILES_DIRECTORY, f"{payment_candidate_uuid}.json") 
    with open(file_path, "r", encoding="utf-8") as f:
        candidate_data = json.load(f)
    return candidate_data["user"]["hacker_id"]

def produce_reciept_mail(payment:Payment):
    payment_dict=payment.model_dump()
    currency_name_to_symbol_mapper={"USD":"$", "EUR":"€", "NIS":"₪", "GBP":"£"}
    payment_dict["currencySymbol"]=currency_name_to_symbol_mapper[payment_dict["currency_name"]] 
    optional_template_fields=[(f"$${{{{{k}}}}}$$",v) for k,v in payment_dict.items()]
    notification_producer(user=payment.user,notification_type=NotificationType.PAYMENT_ACCEPTED,optional_template_fields=optional_template_fields)
    paying_user_for_mail=payment.user.model_dump()
    paying_user_for_mail["name"]=f"{payment.ClientName} {payment.ClientLName}"
    paying_user_for_mail["email"]=payment.email
    paying_user_for_mail=User.model_validate(paying_user_for_mail)
    notification_producer(user=paying_user_for_mail,notification_type=NotificationType.PAYMENT_ACCEPTED,optional_template_fields=optional_template_fields)

def persist_payment_data_in_admissible_formats(payment:Payment):
    with open(os.path.join("resources","mailTemplates",f"{NotificationType.PAYMENT_ACCEPTED}.body_html"), "r",encoding="utf-8") as f:
        receipt_html_template=f.read()
    optional_template_fields=[(f"$${{{{{k}}}}}$$",v) for k,v in payment.model_dump().items()]
    for replacement_tuple in optional_template_fields:
        receipt_html_template=receipt_html_template.replace(replacement_tuple[0],str(replacement_tuple[1]))
    
    receipt_file_name=os.path.join(PAYMENT_DATA_RECEIPTS_DIRECTORY,f"{payment.receipt_index}_{payment.UserId}_{payment.ClientName}_{payment.ClientLName}")
    
    with open(f"{receipt_file_name}.html", "w", encoding="utf-8") as f:
        f.write(receipt_html_template)
        
    if 'HTML' in globals():
        print("detected correctly installed weasyprint dependency, issuing pdf receipt")
        start_time = time.time()
        HTML(string=receipt_html_template).write_pdf(f"{receipt_file_name}.pdf")
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Time taken to generate PDF: {elapsed_time:.4f} seconds")
    else:
        print("did not detect correctly installed weasyprint dependency, not issuing pdf receipt")
    try:
        _persistency_lock.acquire()
        data = load_csv()
        minimal_data_for_persist=payment.model_dump()
        minimal_data_for_persist["application_user"]=minimal_data_for_persist["user"]["hacker_id"]
        del minimal_data_for_persist["user"]
        append_row(data, minimal_data_for_persist)
        save_csv(data)
    finally:
        _persistency_lock.release()


    