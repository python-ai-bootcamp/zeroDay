import os,json
from systemEntities import User, Payment, print
from mailService import notification_producer
from systemEntities import NotificationType
from userService import set_user_as_paid
from fastapi import BackgroundTasks
import time

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
PAYMENT_DATA_RECEIPTS_DIRECTORY = os.path.join(PAYMENT_DATA_DIRECTORY, "receipts")
os.makedirs(PAYMENT_DATA_FILES_DIRECTORY,exist_ok=True)
os.makedirs(PAYMENT_DATA_RECEIPTS_DIRECTORY,exist_ok=True)

def get_receipt_index():
    if os.path.exists(LAST_RECEIPT_INDEX_FILE):
        with open(LAST_RECEIPT_INDEX_FILE, "r") as f:
            last_receipt_index= int(f.read())
    else:
        last_receipt_index=0

    with open(LAST_RECEIPT_INDEX_FILE, "w") as f:
        f.write(str(last_receipt_index+1))

    return str(last_receipt_index+1).zfill(7)

def initiate_user_payement_procedure(payment:Payment, background_tasks: BackgroundTasks):
    print(f"initiate_user_payement_procedure:: received user payment with following credit api related payment:{payment.dict()}")
    payment_succeeded=get_payment_status()
    if payment_succeeded:
        payment.receipt_index=get_receipt_index()
        set_user_as_paid(payment)
        persist_payment_data(payment)
        produce_reciept_mail(payment)
        background_tasks.add_task(persist_payment_data_in_admissible_formats, payment)
        #persist_payment_data_in_admissible_formats(payment)
    else:
        print("initiate_user_payement_procedure:: unimplemented yet, payment unsuccessful, need to convey error in some way,redirection to error page or something")

def get_payment_status():
    print("get_payment_status:: not yet implemented, returning True until it does")
    return True

def persist_payment_data(payment:Payment):
    with open(os.path.join(PAYMENT_DATA_FILES_DIRECTORY,f"{payment.receipt_index}.json"), "w", encoding="utf-8") as f:
        json.dump(payment.dict(), f, indent=4, ensure_ascii=False)

def produce_reciept_mail(payment:Payment):
    optional_template_fields=[(f"$${{{{{k}}}}}$$",v) for k,v in payment.model_dump().items()]
    notification_producer(user=payment.user,notification_type=NotificationType.PAYMENT_ACCEPTED,optional_template_fields=optional_template_fields)

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