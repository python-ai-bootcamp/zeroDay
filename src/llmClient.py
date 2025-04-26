from openai import OpenAI

API_KEY_FILE="./resources/keys/private_keys/.openAI_api_key.txt"

with open(API_KEY_FILE,"r") as f:
    api_key=f.read().strip()

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