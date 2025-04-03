import asyncio,threading,datetime,os
from typing import Tuple
from systemEntities import User,NotificationType
from mailClient import send_ses_mail, Email
from sys import stdout
from configurationService import domain_name, protocol


notification_queue=[]
NOTIFICATION_CONSUMER_INTERVAL=15
MAIL_TEMPLATES_DIR=os.path.join("resources","mailTemplates")

def notification_producer(user:User,notification_type:NotificationType):
    notification_queue.append({"user":user,"notification_type":notification_type})

async def every(__seconds: float, func, *args, **kwargs):
    while True:
        await asyncio.sleep(__seconds)
        func(*args, **kwargs)

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

def send_single_notification(item_to_consume):
    print(f"processing notification of type '{item_to_consume["notification_type"]}'")
    user=item_to_consume["user"]
    subject_template, body_html_template, body_txt_template=load_template_by_notification(item_to_consume["notification_type"])
    subject, body_html, body_txt = substitute_template_variables(subject_template, body_html_template, body_txt_template, user)
    email_to_send=Email(to=user.email, subject=subject, body_txt=body_txt, body_html=body_html)
    send_ses_mail(email_to_send)

def notification_consumer():
    global notification_queue
    timestamp="entered notification_consumer at: "+datetime.datetime.now().isoformat()
    print(timestamp)
    print("current notification_queue::",notification_queue)
    if len(notification_queue)>0:
        item_to_consume=notification_queue.pop(0)
        print("item_to_consume::",item_to_consume)
        match item_to_consume["notification_type"]:
            case NotificationType.CANDIDATE_KID_INTRO:
                send_single_notification(item_to_consume)
            case NotificationType.ASSIGNMENT_SUBMISSION_RESULT_PASSING_WITH_NEXT_ASSIGNMENT_LINK:
                send_single_notification(item_to_consume)
            case NotificationType.ASSIGNMENT_SUBMISSION_RESULT_PASSING_WITHOUT_NEXT_ASSIGNMENT_LINK:
                send_single_notification(item_to_consume)
            case NotificationType.ASSIGNMENT_SUBMISSION_RESULT_FAILING_WITH_ANOTHER_ATTEMPT:
                send_single_notification(item_to_consume)
            case NotificationType.ASSIGNMENT_SUBMISSION_RESULT_FAILING_WITHOUT_ANOTHER_ATTEMPT:
                send_single_notification(item_to_consume)
            case NotificationType.NEW_ASSIGNMENT_ARRIVED:
                print(f"ERROR: '{item_to_consume["notification_type"]}' notification type not yet implemented, not sending mail.")
            case _:
                print(f"ERROR: unimplemented NotificationType '{item_to_consume["notification_type"]}'")

def flush_stdout_workaround():
    stdout.flush()
    
def init_authentication_service():
    ev_loop = asyncio.get_event_loop()
    ev_loop.create_task(every(NOTIFICATION_CONSUMER_INTERVAL, notification_consumer))
    ev_loop.create_task(every(0.1, flush_stdout_workaround))

init_authentication_service()