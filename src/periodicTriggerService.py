import asyncio
from mailService import notification_consumer
from assignmentOrchestrator import trigger_new_assignment_mail_if_needed
from analyticsService import persist_analytics_events
from sys import stdout

NOTIFICATION_CONSUMER_INTERVAL=15
FLUSH_STDOUT_INTERVAL=0.1
NEW_ASSIGNMENT_MAIL_INTERVAL=3600
PERSIST_ANALYTICS_EVENTS=5

async def every(__seconds: float, func, *args, **kwargs):
    while True:
        await asyncio.sleep(__seconds)
        func(*args, **kwargs)

def flush_stdout_workaround():
    stdout.flush()
    
def init_triggers():
    try:
        #ev_loop = asyncio.get_event_loop() #this one works and tested but making depracation warning in tests
        ev_loop = asyncio.get_running_loop()
        ev_loop.create_task(every(NOTIFICATION_CONSUMER_INTERVAL, notification_consumer))
        ev_loop.create_task(every(FLUSH_STDOUT_INTERVAL, flush_stdout_workaround))
        ev_loop.create_task(every(NEW_ASSIGNMENT_MAIL_INTERVAL, trigger_new_assignment_mail_if_needed))
        ev_loop.create_task(every(PERSIST_ANALYTICS_EVENTS, persist_analytics_events))
    except:
        print("test mode, no event loop necessary")

init_triggers()