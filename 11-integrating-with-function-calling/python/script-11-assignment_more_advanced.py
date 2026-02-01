import os
import json
from random import randint
import re

from openai import AzureOpenAI

from dotenv import load_dotenv
load_dotenv()

# override system environment variables for testing purposes
AZURE_OPENAI_ENDPOINT='https://genai-for-beginners-resource.services.ai.azure.com'
AZURE_OPENAI_DEPLOYMENT='gpt-4o'




print("@ Endpoint:",   os.environ.get("AZURE_OPENAI_ENDPOINT"))
print("@ Deployment:", os.environ.get("AZURE_OPENAI_DEPLOYMENT"))
print("Azure OpenAI Function Calling Assignment\n")


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
    
    # print("       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    # print("       @ Searching courses with parameters:")
    # print("       @   + Role:", role)
    # print("       @   + Product:", product)
    # print("       @   + Level:", level)
    # print("       @")
    # print("       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    # print()
    
    
    response = requests.get(url, params=params)
    
    
    modules = response.json()["modules"]
    
    print(f"@ Modules fetched: {len(modules)}, returning top 5.")
    
    results = []
    for i, module in enumerate(modules[:5]):
        title = module["title"]
        url = module["url"]
        print(f"    @{i+1} : {title} - {url[:30]}...")
        results.append({"title": title, "url": url})
    return str(results)

def get_courses_ratings(title, url):
    """
    get a title and its url and return a rating from 1 to 5 stars
    """
    
    return str(randint(1, 5))
        








client = AzureOpenAI(
    api_key=os.environ['AZURE_OPENAI_API_KEY'],  # this is also the default, it can be omitted
    api_version = "2023-07-01-preview"
    )

deployment=os.environ['AZURE_OPENAI_DEPLOYMENT']





####################################################  
##
## preparing the example for function calling
##
####################################################





functions = [
    {
        "name":"search_courses",
        "description":"Retrieves courses from the search index based on the parameters provided",
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
                    "description":"The level of experience the learner has prior to taking the course (i.e. beginner, intermediate, advanced, killer, god)"
                }
            },
            "required":["role"]
        }
    }
    ,
    {
        "name":"get_courses_ratings",
        "description":"Return the rating for a title of a course based on its title and URL, returning a title and its rating from 1 to 5.",
        "parameters":{
            "type":"object",
            "properties":{
                "title":{
                    "type":"string",
                    "description":"The title of the course to evaluate"
                },
                "url":{
                    "type":"string",
                    "description":"The URL of the course to evaluate"
                }
            },
            "required":["title", "url" ]
        }
    }
]



print()
print("##### Function Calling example #####")
print()



print(f"## Number of functions defined: {len(functions)}")
for i, func in enumerate(functions):
    print(f"##{i+1} - ", func["name"])
    print( "      ", func["description"][:80]+"...")
    # print( "      ", func["parameters"])




print()
print()
print()
print()
print("##### Starting conversation loop #####")
print()




####################################################  
##
## conversation loop
##
####################################################


IS_CONVERSATION_OVER = False

messages= []


initial_message = { "role": "system", "content":"You are an expert course recommendation assistant. Help the user find the best courses based on their role, product interest, and experience level. Use the available functions to search for courses and get their ratings. Provide concise and relevant recommendations only related to the selection of courses."}

# messages.append(initial_message)

IS_INITIALIZE = True

while not IS_CONVERSATION_OVER:
    inquiry = input("Enter your inquiry (or 'quit', 'q', 'bye', 'ciao', 'exit', 'sayonara' to exit): \nEnter 'clear' or 'reset' to rest.\nOr press enter for default inquiry.\n> ")
    print()
    
    if inquiry.strip() == "":
        inquiry = "Find me a good course for a beginner student to learn Azure."
        print(inquiry)
        print()

    if inquiry.lower() in ['quit', 'q', 'bye', 'ciao', 'exit', 'sayonara']:
        print("Exiting the conversation. Goodbye!")
        IS_CONVERSATION_OVER = True
        break
    
    if inquiry.lower() in ['clear', 'reset']:
        IS_INITIALIZE = True
        # continue
    
    if IS_INITIALIZE:
        messages = []  # reset messages
        messages.append(initial_message)
        IS_INITIALIZE = False
        
    messages.append({"role": "user", "content": inquiry})
    
    
    response = client.chat.completions.create(model=deployment, 
                                            messages=messages,
                                            functions=functions, 
                                            function_call="auto") 

    print()
    
    response_message = response.choices[0].message


    if hasattr(response_message, "function_call") and response_message.function_call is not None:
        print("## Model decided to call a function:")
        print("##     Function name:", response_message.function_call.name)
        print("##     Arguments:", response_message.function_call.arguments[:50])
        print()
        
        
        print("## Starting function call loop")
        function_call_iteration = 0
        while True:
            function_call_iteration += 1

    
            # Call the function. 
            function_name = response_message.function_call.name
            function_args = response_message.function_call.arguments

    
            print(f"    ### Function Call Iteration: {function_call_iteration} ###")
            print(f"        Name: {function_name}")
            print(f"        Args: {function_args[:80]}")
            print()
        
            
            available_functions = {
                                    "search_courses": search_courses,
                                    "get_courses_ratings": get_courses_ratings,
                                }   
            function_to_call = available_functions[function_name] 

            function_args = json.loads(function_args)
            function_response = function_to_call(**function_args)
        
            print()
            print("    ## Output of function call: ", function_name)
            print("          " + str(function_response)[:100])
            
            
                    
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
            
            # print()
            # print("    Printing messages so far:")
            # for i, msg in enumerate(messages):
            #     print(f"        # {i}: {str(msg)[:100]}...")
            # print()
            
            
            
            
            response = client.chat.completions.create(messages=messages,
                                                    model=deployment,
                                                    function_call="auto",
                                                    functions=functions,
                                                    temperature=0
                                                    )  # get a new response from GPT where it can see the function response
            
            response_message = response.choices[0].message
            if hasattr(response_message, "function_call") and response_message.function_call is not None:
                # if we need another function call, we continue the loop
                
                pass
            else:
                break


    print()
    print("################################################")
    print("## Printing messages so far:")
    for i, msg in enumerate(messages):
        print(f"##        # {i}: {str(msg)[:100]}...")
    print("##")
    print()

    print("## Response from model:")
    print(response_message.content)
    print()
    print()





