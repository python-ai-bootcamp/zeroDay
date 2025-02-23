import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel, NameEmail, constr
SENDER = "Mr. Python McPythony <sender@zerodaybootcamp.xyz>" # should always remain this address
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
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    #Email.to.value, will be switched to this once we go out of the amazon SES snadbox
                    SANDBOX_TEMP_ONLY_POSSIBLE_RECIPIENT
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': Email.body_txt,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': Email.body_html,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent, HuRRAH! Message ID:"),
        print(response['MessageId'])