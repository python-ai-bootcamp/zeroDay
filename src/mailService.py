import asyncio,threading,datetime,os
from systemEntities import User,NotificationType
from mailClient import send_ses_mail, Email
from sys import stdout
from configurationService import domain_name, protocol


notification_queue=[]
NOTIFICATION_CONSUMER_INTERVAL=60
MAIL_TEMPLATES_DIR=os.path.join("resources","mailTemplates")

def notification_producer(user:User,notification_type:NotificationType):
    notification_queue.append({"user":user,"notification_type":notification_type})

async def every(__seconds: float, func, *args, **kwargs):
    while True:
        await asyncio.sleep(__seconds)
        func(*args, **kwargs)

def load_template_by_notification(notification_type:NotificationType):    
    with open(os.path.join(MAIL_TEMPLATES_DIR,notification_type.name+".subject"), "r") as f:
        subject=f.read()
    with open(os.path.join(MAIL_TEMPLATES_DIR,notification_type.name+".body_html"), "r") as f:
        body_html=f.read()
    with open(os.path.join(MAIL_TEMPLATES_DIR,notification_type.name+".body_txt"), "r") as f:
        body_txt=f.read()
    return {"subject":subject,"body_html":body_html,"body_txt":body_txt}

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
                print(f"processing notification of type '{item_to_consume["notification_type"]}'")
                user=item_to_consume["user"]
                notification_template=load_template_by_notification(item_to_consume["notification_type"])
                subject=notification_template["subject"]
                body_txt=notification_template["body_txt"].replace("$${{DOMAIN_NAME}}$$",domain_name).replace("$${{PROTOCOL}}$$",protocol).replace("$${{HACKER_ID}}$$",user.hacker_id).replace("$${{NAME}}$$",user.name)
                body_html=notification_template["body_html"].replace("$${{DOMAIN_NAME}}$$",domain_name).replace("$${{PROTOCOL}}$$",protocol).replace("$${{HACKER_ID}}$$",user.hacker_id).replace("$${{NAME}}$$",user.name)
                email_to_send=Email(to=user.email, subject=subject, body_txt=body_txt, body_html=body_html)
                send_ses_mail(email_to_send)
            case NotificationType.CANDIDATE_PARENT_INTRO:
                print(f"ERROR: to be implemented '{item_to_consume["notification_type"]}'")
            case NotificationType.NEW_ASSIGNMENT_DESCRIPTION:
                print(f"ERROR: to be implemented '{item_to_consume["notification_type"]}'")
            case NotificationType.ASSIGNMENT_SUBMISSION_RESULT:
                print(f"ERROR: to be implemented '{item_to_consume["notification_type"]}'")
            case _:
                print(f"ERROR: unimplemented NotificationType '{item_to_consume["notification_type"]}'")


def flush_stdout_workaround():
    stdout.flush()
    
def init_authentication_service():
    ev_loop = asyncio.get_event_loop()
    ev_loop.create_task(every(NOTIFICATION_CONSUMER_INTERVAL, notification_consumer))
    ev_loop.create_task(every(0.1, flush_stdout_workaround))

init_authentication_service()