import boto3
import traceback
from systemEntities import print, Email
from mailFilter import mailAddressFilter
from botocore.exceptions import ClientError

SENDER = "Mr. Python McPythony <sender@zerodaybootcamp.xyz>" # should ALWAYS remain this address, if we switch it might get blocked
#SANDBOX_TEMP_ONLY_POSSIBLE_RECIPIENTS = ["python.ai.bootcamp@outlook.com", "tal.shachar@tufin.com" ,"micha.vardy@tufin.com", "michavardy@tufin.com", "michavardy@gmail.com" ] # currently until we get out of the amazon SES snadbox we must only send this one!!!!!

AWS_REGION = "eu-north-1"
CHARSET = "UTF-8"

class FilteredEmailException(Exception):
    pass


def send_mail(email_to_send: Email):
    #print(email_to_send)
    client = boto3.client('ses',region_name=AWS_REGION)
    try:
        #if (any(email_to_send.to.email.replace(">","").replace("<","")==x for x in SANDBOX_TEMP_ONLY_POSSIBLE_RECIPIENTS)):
            #print(f"{email_to_send.to.email} is inside {SANDBOX_TEMP_ONLY_POSSIBLE_RECIPIENTS}, sending mail in sandbox mode")
        if mailAddressFilter(email_to_send.to.email.replace(">","").replace("<","")):
            print(f"{email_to_send.to.email} has successfully passed filters and will be sent")
            response = client.send_email(
                Destination={
                    'ToAddresses': [
                        email_to_send.to.email # should uncomment this line and remove next one only once we go out of the amazon SES snadbox
                        #SANDBOX_TEMP_ONLY_POSSIBLE_RECIPIENT_1,SANDBOX_TEMP_ONLY_POSSIBLE_RECIPIENT_2,SANDBOX_TEMP_ONLY_POSSIBLE_RECIPIENT_3
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': CHARSET,
                            'Data': email_to_send.body_html,
                        },
                        'Text': {
                            'Charset': CHARSET,
                            'Data': email_to_send.body_txt,
                        },
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': email_to_send.subject,
                    },
                },
                Source=SENDER
            )
        else:
            #raise FilteredEmailException(f"{email_to_send.to.email} is not inside {SANDBOX_TEMP_ONLY_POSSIBLE_RECIPIENTS}, not sending mail while in sandbox mode")
            raise FilteredEmailException(f"{email_to_send.to.email} failed mailFilter test, not sending mail")
    except ClientError as e:
        print(e.response['Error']['Message'])
        return False
    except FilteredEmailException as e:
        print(e)
        #print(traceback.format_exc())
        return False
    except Exception as e:
        print("caughed an unexpected exception, please investigate stack")
        print(e)
        print(traceback.format_exc())
        return False
    else:
        print(f"Email sent, with following Message ID:{response['MessageId']}"),
        return True