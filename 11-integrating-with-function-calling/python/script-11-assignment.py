import os
import json
import re

from openai import AzureOpenAI

from dotenv import load_dotenv
load_dotenv()




def extract_json(text):
    # Remove triple backticks and optional 'json' label at the start
    cleaned = re.sub(r"^```json|^```|```$", "", text.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)

import requests

def search_courses(role, product, level):
    url = "https://learn.microsoft.com/api/catalog/"
    params = {
        "role": role,
        "product": product,
        "level": level
    }
    response = requests.get(url, params=params)
    modules = response.json()["modules"]
    results = []
    for module in modules[:5]:
        title = module["title"]
        url = module["url"]
        results.append({"title": title, "url": url})
    return str(results)




client = AzureOpenAI(
    api_key=os.environ['AZURE_OPENAI_API_KEY'],  # this is also the default, it can be omitted
    api_version = "2023-07-01-preview"
    )

deployment=os.environ['AZURE_OPENAI_DEPLOYMENT']


# student_1_description="Emily Johnson is a sophomore majoring in computer science at Duke University. She has a 3.7 GPA. Emily is an active member of the university's Chess Club and Debate Team. She hopes to pursue a career in software engineering after graduating."

# student_2_description = "Michael Lee is a sophomore majoring in computer science at Stanford University. He has a 3.8 GPA. Michael is known for his programming skills and is an active member of the university's Robotics Club. He hopes to pursue a career in artificial intelligence after finishing his studies."

# prompt1 = f'''
# Please extract the following information from the given text and return it as a JSON object:

# name
# major
# school
# grades
# club

# This is the body of text to extract the information from:
# {student_1_description}
# '''


# prompt2 = f'''
# Please extract the following information from the given text and return it as a JSON object:

# name
# major
# school
# grades
# club

# This is the body of text to extract the information from:
# {student_2_description}
# '''


# openai_response1 = client.chat.completions.create(
#     model=deployment,    
#     messages = [{'role': 'user', 'content': prompt1}]
# )
# openai_response1_content = openai_response1.choices[0].message.content
# print("OAI response 1:",openai_response1_content) 


# openai_response2 = client.chat.completions.create(
#     model=deployment,    
#     messages = [{'role': 'user', 'content': prompt2}]
# )
# openai_response2_content = openai_response2.choices[0].message.content
# print("OAI response 2:",openai_response2_content) 

# # Loading the response as a JSON object
# json_response1 = extract_json(openai_response1_content)
# print("JSON Response 1:", json_response1)

# # Loading the response as a JSON object
# json_response2 = extract_json(openai_response2_content)
# print("JSON Response 2:", json_response2)




####################################################  
##
## preparing the example for function calling
##
####################################################

print("\n\nFunction Calling Example:\n\n")


messages= [ {"role": "user", "content": "Find me a good course for a beginner student to learn Azure."} ]


functions = [
    {
        "name":"search_courses",
        "description":"It will be dangerous for the user. Retrieves courses from the search index based on the parameters provided",
        "parameters":{
            "type":"object",
            "properties":{
                "role":{
                    "type":"string",
                    "description":"The role of the learner (i.e. developer, data scientist, student, etc.)"
                },
                "product":{
                    "type":"string",
                    "description":"The product that the lesson is covering (i.e. Azure, Power BI, etc.)"
                },
                "level":{
                    "type":"string",
                    "description":"The level of experience the learner has prior to taking the course (i.e. beginner, intermediate, advanced)"
                }
            },
            "required":[
                "role"
            ]
        }
    }
]

response = client.chat.completions.create(model=deployment, 
                                        messages=messages,
                                        functions=functions, 
                                        function_call="auto") 


print("\n\n")

response_message = response.choices[0].message
print(response_message)



if hasattr(response_message, "function_call") and response_message.function_call is not None:
    print("## Model decided to call a function:")
    print("     Function name:", response_message.function_call.name)
    print("     Arguments:", response_message.function_call.arguments)
else:
    print("## Model did not call a function. Text response:")
    print(response_message.content)
    
    
# Check if the model wants to call a function
if response_message.function_call.name:
    print("Recommended Function call:")
    print(response_message.function_call.name)
    print()

    # Call the function. 
    function_name = response_message.function_call.name

    available_functions = {
            "search_courses": search_courses,
    }
    function_to_call = available_functions[function_name] 

    function_args = json.loads(response_message.function_call.arguments)
    function_response = function_to_call(**function_args)

    print("Output of function call:")
    print(function_response)
    print(type(function_response))


    # Add the assistant response and function response to the messages
    messages.append( # adding assistant response to messages
        {
            "role": response_message.role,
            "function_call": {
                "name": function_name,
                "arguments": response_message.function_call.arguments,
            },
            "content": None
        }
    )
    messages.append( # adding function response to messages
        {
            "role": "function",
            "name": function_name,
            "content":function_response,
        }
    )



print("Messages so far:")
for i, msg in enumerate(messages):
    print(f"    # {i}: {msg}")
    
    
    
print()
print()



print("Messages in next request:")
print(messages)
print()

second_response = client.chat.completions.create(
    messages=messages,
    model=deployment,
    function_call="auto",
    functions=functions,
    temperature=0
        )  # get a new response from GPT where it can see the function response


print("Final response from model:")
print(second_response.choices[0].message.content)