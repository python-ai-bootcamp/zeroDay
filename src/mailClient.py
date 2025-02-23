import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel, NameEmail, constr
SENDER = "Mr. Python McPythony <sender@zerodaybootcamp.xyz>" # should ALWAYS remain this address, if we switch it might get blocked
SANDBOX_TEMP_ONLY_POSSIBLE_RECIPIENT = "python.ai.bootcamp@outlook.com" # currently until we get out of the amazon SES snadbox we must only send this one!!!!!
SUBJECT_LENGTH=250
AWS_REGION = "eu-north-1"
CHARSET = "UTF-8"

class Email(BaseModel):
    to: NameEmail
    subject: constr(max_length=SUBJECT_LENGTH)
    body_txt: str
    body_html: str

def send_ses_mail(email_to_send: Email):
    client = boto3.client('ses',region_name=AWS_REGION)
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    #Email.to.value # should uncomment this line and remove next one only once we go out of the amazon SES snadbox
                    SANDBOX_TEMP_ONLY_POSSIBLE_RECIPIENT
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
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent, HuRRAH! Message ID:"),
        print(response['MessageId'])