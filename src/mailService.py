import asyncio,threading,datetime
from systemEntities import User

notification_queue=[]
NOTIFICATION_QUEUE_CONSUMER_INTERVAL=5

def notification_producer(user:User,notificationType:str):
    notification_queue.append({"user":user,"notificationType":notificationType})

async def every(__seconds: float, func, *args, **kwargs):
    while True:
        await asyncio.sleep(__seconds)
        func(*args, **kwargs)

def notification_queue_consumer():
    global notification_queue
    timestamp="entered notification_queue_consumer at: "+datetime.datetime.now().isoformat()
    print(timestamp, flush=True)
    print("current notification_queue::",notification_queue, flush=True)
    if len(notification_queue)>0:
        item_to_consume=notification_queue.pop(0)
        print("item_to_consume::",item_to_consume, flush=True)

    
def init_authentication_service():
    notification_queue_consumer()
    ev_loop = asyncio.get_event_loop()
    ev_loop.create_task(every(NOTIFICATION_QUEUE_CONSUMER_INTERVAL, notification_queue_consumer))

init_authentication_service()