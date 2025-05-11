
import os,json
MAIL_FILTER_DIRECTORY = os.path.join("./resources","uncommitted_configurations")
MAIL_WHITELIST_FILTER_DATA_FILE = os.path.join(MAIL_FILTER_DIRECTORY, "mail_filter_whitelist.json")
MAIL_BLACKLIST_FILTER_DATA_FILE = os.path.join(MAIL_FILTER_DIRECTORY, "mail_filter_blacklist.json")

def load_data(filename:str):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return []

whitelist:list[str] = [s.lower() for s in load_data(MAIL_WHITELIST_FILTER_DATA_FILE)]
blacklist:list[str] = [s.lower() for s in load_data(MAIL_BLACKLIST_FILTER_DATA_FILE)]
print("mailFilter:: started mail service with following whitelist:",whitelist)
print("mailFilter:: started mail service with following blacklist:",blacklist)

def mailAddressFilter(mail_address:str):
    blacklist:list[str] = [s.lower() for s in load_data(MAIL_BLACKLIST_FILTER_DATA_FILE)]
    mail_address = mail_address.lower()
    if mail_address in blacklist:
        return False
    if whitelist:
        return mail_address in whitelist
    return True