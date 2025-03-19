import asyncio,threading,datetime
from systemEntities import User,NotificationType
from mailClient import send_ses_mail, Email
from sys import stdout

notification_queue=[]
NOTIFICATION_CONSUMER_INTERVAL=60

def notification_producer(user:User,notification_type:NotificationType):
    notification_queue.append({"user":user,"notification_type":notification_type})

async def every(__seconds: float, func, *args, **kwargs):
    while True:
        await asyncio.sleep(__seconds)
        func(*args, **kwargs)

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
                email_to_send=Email(to=user.email, subject="Welcome to zeroDayBootcamp, You're Path to Python AI Development", body_txt="what a body", body_html="<html><head></head><body>what a body</body></html>")
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