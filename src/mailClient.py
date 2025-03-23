import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel, NameEmail, constr
SENDER = "Mr. Python McPythony <sender@zerodaybootcamp.xyz>" # should ALWAYS remain this address, if we switch it might get blocked
SANDBOX_TEMP_ONLY_POSSIBLE_RECIPIENTS = ["python.ai.bootcamp@outlook.com", "tal.shachar@tufin.com" ,"micha.vardy@tufin.com" ] # currently until we get out of the amazon SES snadbox we must only send this one!!!!!


SUBJECT_LENGTH=250
AWS_REGION = "eu-north-1"
CHARSET = "UTF-8"

class Email(BaseModel):
    to: NameEmail
    subject: constr(max_length=SUBJECT_LENGTH)
    body_txt: str
    body_html: str

def send_ses_mail(email_to_send: Email):
    print(email_to_send)
    client = boto3.client('ses',region_name=AWS_REGION)
    try:
        if (any(email_to_send.to.email.replace(">","").replace("<","")==x for x in SANDBOX_TEMP_ONLY_POSSIBLE_RECIPIENTS)):
            print(f"{email_to_send.to.email} is inside {SANDBOX_TEMP_ONLY_POSSIBLE_RECIPIENTS}, sending mail in sandbox mode")
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
            raise Exception(f"{email_to_send.to.email} is not inside {SANDBOX_TEMP_ONLY_POSSIBLE_RECIPIENTS}, not sending mail while in sandbox mode")
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent, HuRRAH! Message ID:"),
        print(response['MessageId'])