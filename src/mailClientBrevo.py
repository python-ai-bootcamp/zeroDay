import brevo_python
from brevo_python.rest import ApiException
from pprint import pprint
import traceback
from pydantic import BaseModel, NameEmail, constr
from os import path


API_KEY_FILE="./resources/keys/private_keys/brevo_api_key.txt"

with open(API_KEY_FILE,"r") as f:
    api_key=f.read().strip()

configuration = brevo_python.Configuration()
configuration.api_key['api-key'] = api_key
api_instance = brevo_python.TransactionalEmailsApi(brevo_python.ApiClient(configuration))


SENDER ={"name":"Mr. Python McPythony","email":"Sender@zerodaybootcamp.xyz"} # should ALWAYS remain this address, if we switch it might get blocked
SANDBOX_TEMP_ONLY_POSSIBLE_RECIPIENTS = ["python.ai.bootcamp@outlook.com", "tal.shachar@tufin.com" ,"micha.vardy@tufin.com", "michavardy@tufin.com", "michavardy@gmail.com" ] # currently until we get out of the amazon SES snadbox we must only send this one!!!!!


SUBJECT_LENGTH=250
AWS_REGION = "eu-north-1"
CHARSET = "UTF-8"

class FilteredEmailException(Exception):
    pass

class Email(BaseModel):
    to: NameEmail
    subject: constr(max_length=SUBJECT_LENGTH)
    body_txt: str
    body_html: str

def send_mail(email_to_send: Email):
    try:
        if (any(email_to_send.to.email.replace(">","").replace("<","")==x for x in SANDBOX_TEMP_ONLY_POSSIBLE_RECIPIENTS)):
            print(f"{email_to_send.to.email} is inside {SANDBOX_TEMP_ONLY_POSSIBLE_RECIPIENTS}, sending mail in sandbox mode")
            send_smtp_email = brevo_python.SendSmtpEmail( #https://developers.brevo.com/recipes/send-transactional-emails-in-python    #alternative using the v3 sdk https://developers.brevo.com/reference/sendtransacemail)
                sender=SENDER,
                to=[{"email":email_to_send.to.email,"name":email_to_send.to.name}],
                subject=email_to_send.subject,
                html_content=email_to_send.body_html,
                text_content=email_to_send.body_txt
            )
            api_response = api_instance.send_transac_email(send_smtp_email)
        else:
            raise FilteredEmailException(f"{email_to_send.to.email} is not inside {SANDBOX_TEMP_ONLY_POSSIBLE_RECIPIENTS}, not sending mail while in sandbox mode")
    except ApiException as e:
        print("Exception when calling TransactionalEmailsApi->send_transac_email: %s\n" % e)
        print(traceback.format_exc())
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
        print(f"Email sent, with following Message ID:{api_response}"),
        return True