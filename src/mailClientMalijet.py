from mailjet_rest import Client
import traceback, json
from systemEntities import print, Email

API_KEY_FILE="./resources/keys/private_keys/.malijet_api_key.json"

with open(API_KEY_FILE,"r") as f:
    key_dict = json.load(f)
    api_key=key_dict["key"]
    api_secret=key_dict["secret"]

SENDER ={"Name":"Mr. Python McPythony","Email":"Sender@zerodaybootcamp.xyz"} # should ALWAYS remain this address, if we switch it might get blocked
SANDBOX_TEMP_ONLY_POSSIBLE_RECIPIENTS = ["python.ai.bootcamp@outlook.com", "tal.work.mail@gmail.com", "tal.shachar@tufin.com" ,"micha.vardy@tufin.com", "michavardy@tufin.com", "michavardy@gmail.com" ] # currently until we get out of the amazon SES snadbox we must only send this one!!!!!

class FilteredEmailException(Exception):
    pass

class EmailProviderIssuesException(Exception):
    pass

mailjet = Client(auth=(api_key, api_secret), version='v3.1')

def send_mail(email_to_send: Email):
    try:
        if (any(email_to_send.to.email.replace(">","").replace("<","")==x for x in SANDBOX_TEMP_ONLY_POSSIBLE_RECIPIENTS)):
            print(f"{email_to_send.to.email} is inside {SANDBOX_TEMP_ONLY_POSSIBLE_RECIPIENTS}, sending mail in sandbox mode")
            data = {
                'Messages': [
                                {
                                        "From": SENDER,
                                        "To": [
                                                {
                                                        "Email": email_to_send.to.email,
                                                        "Name": email_to_send.to.name
                                                }
                                        ],
                                        "Subject": email_to_send.subject,
                                        "TextPart": email_to_send.body_txt,
                                        "HTMLPart": email_to_send.body_html
                                }
                        ]
            }
            
            api_response = mailjet.send.create(data=data)

            if not api_response.status_code==200:
                EmailProviderIssuesException(f"{email_to_send.to.email} was not sent because of status_code not 200 (result.status_code='{result.status_code}')")

        else:
            raise FilteredEmailException(f"{email_to_send.to.email} is not inside {SANDBOX_TEMP_ONLY_POSSIBLE_RECIPIENTS}, not sending mail while in sandbox mode")
    except FilteredEmailException as e:
        print(e)
        #print(traceback.format_exc())
        return False
    except EmailProviderIssuesException as e:
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