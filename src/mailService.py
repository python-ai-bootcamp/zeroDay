import asyncio,datetime,os, json
from typing import Tuple
from systemEntities import User, NotificationType, print
#from mailClientSes import send_mail, Email
from mailClientBrevo import send_mail, Email
from configurationService import domain_name, protocol
from pydantic import BaseModel

MAIL_TEMPLATES_DIR=os.path.join("resources","mailTemplates")
MAIL_QUEUE_DATA_FILE = os.path.join("./data/","notification_queue_data.json")
UNDELIVERED_MAIL_DATA_FILE = os.path.join("./data/","notification_queue_undelivered_data.json")
MAX_DELIVERY_ATTEMPTS = 3

class Notification(BaseModel):
    notification_type: NotificationType
    user: User
    send_attempt_counter: int = 0

def load_notification_queue_data():
    if os.path.exists(MAIL_QUEUE_DATA_FILE):
        with open(MAIL_QUEUE_DATA_FILE, "r") as f:
            return [Notification.model_validate(notification) for notification in json.load(f)]
    return []

def load_undelivered_notification_data():
    if os.path.exists(UNDELIVERED_MAIL_DATA_FILE):
        with open(UNDELIVERED_MAIL_DATA_FILE, "r") as f:
            return [Notification.model_validate(notification) for notification in json.load(f)]
    return []

notification_queue:list[Notification]=load_notification_queue_data()

def save_notification_queue_data():
    print("saving following notification_queue data::",notification_queue)
    with open(MAIL_QUEUE_DATA_FILE, "w") as f:
        json.dump([notification.dict() for notification in notification_queue], f, indent=4)

def save_undelivered_notification_data(data):
    print("saving following undelivered_notification data::",data)
    with open(UNDELIVERED_MAIL_DATA_FILE, "w") as f:
        json.dump([notification.dict() for notification in data], f, indent=4)

def notification_producer(user:User,notification_type:NotificationType):
    notification_queue.append(Notification(user=user,notification_type=notification_type))
    save_notification_queue_data()

def load_template_by_notification(notification_type:NotificationType):    
    with open(os.path.join(MAIL_TEMPLATES_DIR,notification_type.name+".subject"), "r") as f:
        subject_template=f.read()
    with open(os.path.join(MAIL_TEMPLATES_DIR,notification_type.name+".body_html"), "r") as f:
        body_html_template=f.read()
    with open(os.path.join(MAIL_TEMPLATES_DIR,notification_type.name+".body_txt"), "r") as f:
        body_txt_template=f.read()
    return subject_template, body_html_template, body_txt_template

def substitute_template_variables(subject_template:str,body_html_template:str,body_txt_template:str, user:User)->Tuple[str,str,str]:
    subject=subject_template\
        .replace("$${{DOMAIN_NAME}}$$",domain_name)\
        .replace("$${{PROTOCOL}}$$",protocol)\
        .replace("$${{HACKER_ID}}$$",user.hacker_id)\
        .replace("$${{NAME}}$$",user.name)
    body_html=body_html_template\
        .replace("$${{DOMAIN_NAME}}$$",domain_name)\
        .replace("$${{PROTOCOL}}$$",protocol)\
        .replace("$${{HACKER_ID}}$$",user.hacker_id)\
        .replace("$${{NAME}}$$",user.name)
    body_txt=body_txt_template\
        .replace("$${{DOMAIN_NAME}}$$",domain_name)\
        .replace("$${{PROTOCOL}}$$",protocol)\
        .replace("$${{HACKER_ID}}$$",user.hacker_id)\
        .replace("$${{NAME}}$$",user.name)
    return subject, body_html, body_txt

def send_single_notification(item_to_consume:Notification):
    global notification_queue
    print(f"processing notification of type '{item_to_consume.notification_type}'")
    user=item_to_consume.user
    subject_template, body_html_template, body_txt_template=load_template_by_notification(item_to_consume.notification_type)
    subject, body_html, body_txt = substitute_template_variables(subject_template, body_html_template, body_txt_template, user)
    email_to_send=Email(to=user.email, subject=subject, body_txt=body_txt, body_html=body_html)
    send_succeeded=send_mail(email_to_send)
    if not send_succeeded:
       item_to_consume.send_attempt_counter=item_to_consume.send_attempt_counter+1
       notification_queue.append(item_to_consume)
    save_notification_queue_data()

def notification_consumer():
    global notification_queue
    if len(notification_queue)>0:
        timestamp="entered notification_consumer at: "+datetime.datetime.now().isoformat()
        print(timestamp)
        print("current notification_queue::",notification_queue)
        item_to_consume=notification_queue.pop(0)
        if item_to_consume.send_attempt_counter<MAX_DELIVERY_ATTEMPTS:
            print("item_to_consume::",item_to_consume)
            match item_to_consume.notification_type:
                case NotificationType.PAYMENT_ACCEPTED:
                    print(f"ERROR: '{item_to_consume.notification_type}' notification type not yet implemented, not sending mail.")
                case _:
                    send_single_notification(item_to_consume)
        else:
            save_notification_queue_data()
            data=load_undelivered_notification_data()
            data.append(item_to_consume)
            save_undelivered_notification_data(data)
