from systemEntities import User
from mailService import notification_producer
from systemEntities import NotificationType
from collections import OrderedDict
from userService import set_user_as_paid

def initiate_user_payement_procedure(user:User, ClientName:str, ClientLName:str, UserId:str, email:str, phone:str):
    print(f"initiate_user_payement_procedure:: received user {user} with following credit api related details:ClientName:{ClientName}, ClientLName:{ClientLName}, UserId:{UserId}, email:{email}, phone:{phone}")
    print("initiate_user_payement_procedure:: not fully implemented procedure, setting user as paid by default")
    set_user_as_paid(user.hacker_id)
    persistPaymentBooking(user:User, ClientName:str, ClientLName:str, UserId:str, email:str, phone:str)
    produceRecieptMail(user)
    persistRecieptInPdfFormat(user)

def persistPaymentBooking(user:User, ClientName:str, ClientLName:str, UserId:str, email:str, phone:str):
    print("persistRecieptInPdfFormat:: not yet implemented")

def produceRecieptMail(user:User):
    print("produceRecieptMail:: not yet implemented")

def persistRecieptInPdfFormat(user:User):
    print("persistRecieptInPdfFormat:: not yet implemented")

