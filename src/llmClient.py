from openai import OpenAI
from langchain_openai import ChatOpenAI
try:
    from systemEntities import Models
except ImportError:
    from .systemEntities import Models
import os

API_KEY_FILE="./resources/keys/private_keys/.openAI_api_key.txt"
with open(API_KEY_FILE,"r") as f:
    api_key=f.read().strip()
    os.environ["OPENAI_API_KEY"] = api_key

def load_validator_model(model_name:Models):
  #print(f"llmClient::load_validator_model:: entered method")
  match model_name:
    case Models.OPENAI_LANGCHAIN_DEFAULT:
      return ChatOpenAI()
    case Models.OPENAI_gpt_4|Models.OPENAI_gpt_4o|Models.OPENAI_o3_mini|Models.OPENAI_o3:
      return ChatOpenAI(model=model_name.value)
    case _:
        exit("unsupported model initialized")
        

client = OpenAI(
  api_key=api_key
)
open_ai_client=OpenAI(api_key=api_key)

def getClient():
  return open_ai_client

def basicPromptResponse(prompt:str):
   try:
      client=getClient()
      completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
          {"role": "user", "content": prompt}
        ]
      )
      return completion.choices[0].message.content
   except Exception as e:
      print("unexpected response from client.chat.completions.create")