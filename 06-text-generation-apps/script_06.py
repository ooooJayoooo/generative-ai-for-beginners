import os
import openai

# from openai import AzureOpenAI
# from dotenv import load_dotenv
# load_dotenv()
# client = AzureOpenAI(
#     api_key=os.environ['AZURE_OPENAI_API_KEY'],  # this is also the default, it can be omitted
#     api_version = "2023-05-15"
#     )
# deployment=os.environ['AZURE_OPENAI_DEPLOYMENT']
# print(f"Using deployment: {deployment}")


openai.api_type = 'azure'
openai.api_key = os.environ["OPENAI_API_KEY"]
openai.api_version = '2023-05-15'
# openai.api_base = os.getenv("API_BASE")




prompt = "Complete the following: Once upon a time there was a"
print(f"Prompt: {prompt}")
print("\n---\n")


completion = openai.Completion.create(model="davinci-002", prompt=prompt)
print(completion.choices[0].text)