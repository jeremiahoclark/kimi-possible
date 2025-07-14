from typing import *
 
import json
 
from openai import OpenAI
 
 
client = OpenAI(
    api_key="MOONSHOT_API_KEY", # Replace MOONSHOT_API_KEY with the API Key you obtained from the Kimi Open Platform
    base_url="https://api.moonshot.ai/v1",
)
 
tools = [
	{
		"type": "function", # The field type is agreed upon, and currently supports function as a value
		"function": { # When type is function, use the function field to define the specific function content
			"name": "search", # The name of the function, please use English letters, numbers, plus hyphens and underscores as the function name
			"description": """ 
				Search for content on the internet using a search engine.
 
				When your knowledge cannot answer the user's question, or the user requests you to perform an online search, call this tool. Extract the content the user wants to search from the conversation as the value of the query parameter.
				The search results include the title of the website, the website address (URL), and a brief introduction to the website.
			""", # Introduction to the function, write the specific function here, as well as the usage scenario, so that the Kimi large language model can correctly choose which functions to use
			"parameters": { # Use the parameters field to define the parameters accepted by the function
				"type": "object", # Fixed use type: object to make the Kimi large language model generate a JSON Object parameter
				"required": ["query"], # Use the required field to tell the Kimi large language model which parameters are required
				"properties": { # The specific parameter definitions are in properties, and you can define multiple parameters
					"query": { # Here, the key is the parameter name, and the value is the specific definition of the parameter
						"type": "string", # Use type to define the parameter type
						"description": """
							The content the user wants to search for, extracted from the user's question or chat context.
						""" # Use description to describe the parameter so that the Kimi large language model can better generate the parameter
					}
				}
			}
		}
	},
	{
		"type": "function", # The field type is agreed upon, and currently supports function as a value
		"function": { # When type is function, use the function field to define the specific function content
			"name": "crawl", # The name of the function, please use English letters, numbers, plus hyphens and underscores as the function name
			"description": """
				Get the content of a webpage based on the website address (URL).
			""", # Introduction to the function, write the specific function here, as well as the usage scenario, so that the Kimi large language model can correctly choose which functions to use
			"parameters": { # Use the parameters field to define the parameters accepted by the function
				"type": "object", # Fixed use type: object to make the Kimi large language model generate a JSON Object parameter
				"required": ["url"], # Use the required field to tell the Kimi large language model which parameters are required
				"properties": { # The specific parameter definitions are in properties, and you can define multiple parameters
					"url": { # Here, the key is the parameter name, and the value is the specific definition of the parameter
						"type": "string", # Use type to define the parameter type
						"description": """
							The website address (URL) of the content to be obtained, which can usually be obtained from the search results.
						""" # Use description to describe the parameter so that the Kimi large language model can better generate the parameter
					}
				}
			}
		}
	}
]
 
 
def search_impl(query: str) -> List[Dict[str, Any]]:
    """
    search_impl uses a search engine to search for query. Most mainstream search engines (such as Bing) provide API calls. You can choose
    your preferred search engine API and place the website title, link, and brief introduction information from the return results in a dict to return.
 
    This is just a simple example, and you may need to write some authentication, validation, and parsing code.
    """
    r = httpx.get("https://your.search.api", params={"query": query})
    return r.json()
 
 
def search(arguments: Dict[str, Any]) -> Any:
    query = arguments["query"]
    result = search_impl(query)
    return {"result": result}
 
 
def crawl_impl(url: str) -> str:
    """
    crawl_url gets the content of a webpage based on the url.
 
    This is just a simple example. In actual web scraping, you may need to write more code to handle complex situations, such as asynchronously loaded data; and after obtaining
    the webpage content, you can clean the webpage content according to your needs, such as retaining only the text or removing unnecessary content (such as advertisements).
    """
    r = httpx.get(url)
    return r.text
 
 
def crawl(arguments: dict) -> str:
    url = arguments["url"]
    content = crawl_impl(url)
    return {"content": content}
 
 
# Map each tool name and its corresponding function through tool_map so that when the Kimi large language model returns tool_calls, we can quickly find the function to execute
tool_map = {
    "search": search,
    "crawl": crawl,
}
 
messages = [
    {"role": "system",
     "content": "You are Kimi, an artificial intelligence assistant provided by Moonshot AI. You are better at conversing in Chinese and English. You provide users with safe, helpful, and accurate answers. At the same time, you will refuse to answer any questions involving terrorism, racial discrimination, pornography, and violence. Moonshot AI is a proper noun and should not be translated into other languages."},
    {"role": "user", "content": "Please search for Context Caching online and tell me what it is."}  # Request Kimi large language model to perform an online search in the question
]
 
finish_reason = None
 
 
# Our basic process is to ask the Kimi large language model questions with the user's question and tools. If the Kimi large language model returns finish_reason: tool_calls, we execute the corresponding tool_calls,
# and submit the execution results in the form of a message with role=tool back to the Kimi large language model. The Kimi large language model then generates the next content based on the tool_calls results:
#
#   1. If the Kimi large language model believes that the current tool call results can answer the user's question, it returns finish_reason: stop, and we exit the loop and print out message.content;
#   2. If the Kimi large language model believes that the current tool call results cannot answer the user's question and needs to call the tool again, we continue to execute the next tool_calls in the loop until finish_reason is no longer tool_calls;
#
# During this process, we only return the result to the user when finish_reason is stop.
 
while finish_reason is None or finish_reason == "tool_calls":
    completion = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=messages,
        temperature=0.3,
        tools=tools,  # <-- We submit the defined tools to the Kimi large language model through the tools parameter
    )
    choice = completion.choices[0]
    finish_reason = choice.finish_reason
    if finish_reason == "tool_calls": # <-- Determine whether the current return content contains tool_calls
        messages.append(choice.message) # <-- We add the assistant message returned to us by the Kimi large language model to the context so that the Kimi large language model can understand our request next time
        for tool_call in choice.message.tool_calls: # <-- tool_calls may be multiple, so we use a loop to execute them one by one
            tool_call_name = tool_call.function.name
            tool_call_arguments = json.loads(tool_call.function.arguments) # <-- arguments is a serialized JSON Object, and we need to deserialize it with json.loads
            tool_function = tool_map[tool_call_name] # <-- Quickly find which function to execute through tool_map
            tool_result = tool_function(tool_call_arguments)
 
            # Construct a message with role=tool using the function execution result to show the result of the tool call to the model;
            # Note that we need to provide the tool_call_id and name fields in the message so that the Kimi large language model
            # can correctly match the corresponding tool_call.
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call_name,
                "content": json.dumps(tool_result), # <-- We agree to submit the tool call result to the Kimi large language model in string format, so we use json.dumps to serialize the execution result into a string here
            })
 
print(choice.message.content) # <-- Here, we return the reply generated by the model to the user