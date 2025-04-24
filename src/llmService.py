from openai import OpenAI
import inspect
import sys



if __name__ == "__main__":
    print(inspect.getsource(sys.modules[__name__]))


API_KEY_FILE="./resources/keys/private_keys/.openAI_api_key.txt"

with open(API_KEY_FILE,"r") as f:
    api_key=f.read().strip()

client = OpenAI(
  api_key=api_key
)

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": "write a short poem  (less than 5 lines) about Tal changing his mind and agreeing with on Micha's idea to use LLM in order to test zeroDay project assignments. please make it less gay than previous prompts"}
  ]
)

print(completion.choices[0].message.content);
