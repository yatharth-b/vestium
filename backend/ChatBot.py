from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from utils import get_photos_from_pinterest, get_rec_from_wardrobe, get_rec_from_web

class ChatBot():
    def __init__(self) -> None:
        self.conversation_history = [{"role": "system", "content": "You are a useful stylist that helps people plan their clothes along with finding them from pinterest\
 (searching from web) and vectordatabases that are finction calls"}]
        
        self.client = OpenAI(api_key = 'abc')

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_photos_from_pinterest",
                    "description": "Give some outfit suggestions on some theme.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                        "theme": {
                            "type": "string", 
                            "description": "The theme user asked the outfit for"
                            }
                        }
                        },
                    "required": ["theme"],
                    },
                },
            {
                "type": "function",
                "function": {
                    "name": "get_rec_from_web",
                    "description": "Give outfit recommendations based on these selected outfits from the INTERNET",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "like_list": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                },
                                "minItems": 1,
                                "maxItems": 10,
                                "description": "list of links that the assistant provided and the user likes"
                            }
                        }
                    }, "required": ["like_list"]
                }
            }, {
                "type": "function",
                "function": {
                    "name": "get_rec_from_wardrobe",
                    "description": "Give outfit recommendations based on these selected outfits that they have (i.e. is in their wardrobe/ closet)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "like_list": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                },
                                "minItems": 1,
                                "maxItems": 10,
                                "description": "list of links that the assistant provided and the user likes"
                            }
                        }
                    }, "required": ["like_list"]
                }
            }
        ]
        
    def get_user_input(self, message):
        message = {"role": "user", "content": message}
        self.conversation_history.extend(message)
        data = self.client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    messages=message,
                    tools=self.tools,
                    )
        return self.act_on_model_output(data)
    
    def act_on_model_output(self, data):
        if data.choices[0].finish_reason == 'tool_calls':
            # Some functional call has to happen
            function = data.choices[0].message.tool_calls[0].function
            if function.name == 'get_photos_from_pinterest':
                theme = json.loads(function.arguments)['theme']
                output = get_photos_from_pinterest(theme)
            elif function.name == 'get_rec_from_web':
                like_list = json.loads(function.arguments)['like_list']
                output = get_rec_from_web(like_list)
            elif function.name == 'get_rec_from_wardrobe':
                like_list = json.loads(function.arguments)['like_list']
                output = get_rec_from_wardrobe(like_list)
            else:
                raise ValueError("Function being called by GPT doesn't exist.")

            string_output = ', '.join(output)
            messages = [{"role": "assistant", "content": string_output}] # Because it is outputting, no need to add history here
            self.conversation_history.extend(messages)
            return output
        else:
            output = data.choices[0].message.content
            messages = [{"role": "assistant", "content": output}]
            self.conversation_history.extend(messages)
            return output


