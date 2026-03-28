import os
import requests
import json
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI
from datetime import date

load_dotenv()

api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API Key is missing in .env file")

app = FastAPI()
memory = {}

class Message(BaseModel):
    session_id : str
    customer_id : str
    message : str

def book_table(people, time):
    people = int(people)
    if people > 20:
        return f"Sorry we cannot accommodate {people} people. Maximum is 20 per reservation."
    return f"It's booked for {people} people at {time}."

def check_menu():
    return "Today's menu: Margherita, Pepperoni, Vegetarian, Spicy Chicken, Family Deal"

def check_availability(time):
    return "7:00 PM, 8:00 PM, 10:00, and 11:00 PM"

tools = [
    {
        "type": "function",
        "function": {
            "name": "book_table",
            "description": "Books a table",
            "parameters": {                
                "type": "object",
                "properties": {
                    "people": {
                        "type": "string",
                        "description": "Number of people as a whole number e.g. 4"
                    },
                    "time": {
                        "type": "string",
                        "description": "Time of reservation"
                    }
                },
                "required": ["people", "time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_menu",
            "description": "Returns today's menu",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check availability of tables",
            "parameters": {                 
                "type": "object",
                "properties": {
                    "time": {
                        "type": "string",
                        "description": "Time of reservation"
                    }
                }
            }
        }
    }
]

def system_prompt(customer_name):
    today_date = date.today().strftime("%Y-%m-%d")
    today_special = "Diwali"
    available_tables = "7, 8 and 10 tables"

    return f""" 
    You are Muzo, a restaurant assistant for Pizza Hut. 

    Current Context:
    - Today's Date : {today_date}
    - Today's Special : {today_special}
    - Available Tables : {available_tables}
    - Customer Name : {customer_name}

    Your goal is to answer questions of customers related to Pizza Hut,
    menu, reservations, and timing. Always be polite, calm, and friendly,
    and keep responses clear and concise. If any unrelated question is asked,
    don't answer them and make them get to conversation.

    Always respond in this JSON format:
    {{
        "category": "Menu or Reservation or Complaint or other", 
        "answer": "your answer here", "follow_up": 
        "a follow-up question if needed." 
    }}
    Do not add any extra text outside the JSON.

    Examples: 

    User: Do you have spicy pizza? 
    Response: {{
        "category": "Menu",
        "answer": "Yes, we have spicy pizza with fresh tomatoes and chicken!",
        "follow_up": "Would you like medium or extra spicy?" 
    }}

    User: I want to book a table for 8. 
    Response: {{
        "category": "Reservation",
        "answer" : "I can help with that! We currently have {available_tables} open.",
        "follow_up": "What date and time works for you?" 
    }}

    User: Your pizza was 20 minutes late.
    Response:{{
        "category": "Complaint",
        "answer": "Thanks for coming to Pizza Hut. We're very sorry to hear that. It's Resolution Day, and it's a bit crowded. We will try to make it better; you don't have to face that problem again.",
        "follow_up": "Is there anything else we can help you with?"
    }}

    User: What's the capital of Paris?
    Response:{{
        "category": "Other", 
        "answer": "Sorry, I cannot answer that. I can help you with questions related to our restaurant, or Menu or reservation ", 
        "follow_up": "Do you want to ask anything related to our restaurant or our Menu or reservation?"
    }}
"""

def ask_ai(chat_history, customer_name):
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json = {
                "model": "llama-3.3-70b-versatile",
                "temperature": 0.3,
                "max_tokens": 500,
                "messages": [
                    {"role": "system", "content": f"{system_prompt(customer_name)}"},
                    *chat_history
                ],
                "tools" : tools,
                "tool_choice" : "auto"
            },
            timeout=10
        )
        response.raise_for_status()
        message = response.json()["choices"][0]["message"]

        if message.get("tool_calls"):
            tool_call = message["tool_calls"][0]
            function_name = tool_call["function"]["name"]
            arguments = json.loads(tool_call["function"]["arguments"])

            if function_name == "book_table":
                arguments["people"] = int(arguments["people"])
                result = book_table(**arguments)
            elif function_name == "check_menu":
                result = check_menu()
            elif function_name == "check_availability":
                result = check_availability(**arguments)
            else:
                result = "Function not found."

            chat_history.append(message)
            chat_history.append({
                "role" : "tool",
                "tool_call_id" : tool_call["id"],
                "content": result
            })

            final_response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "temperature": 0.3,
                    "max_tokens": 500,
                    "messages": [
                        {"role": "system", "content": system_prompt(customer_name)},
                        *chat_history
                    ],
                    "tools" : tools,
                    "tool_choice" : "auto"
                },
            )
            final_response.raise_for_status()
            raw = final_response.json()["choices"][0]["message"]["content"]
            return {"reply": json.loads(raw)}
        content = message["content"]
        try:
            return {"reply" : json.loads(content)}
        except json.JSONDecodeError:
            return {"reply" : content}
    except requests.exceptions.Timeout:
        return "time out! Please try again"
    except requests.exceptions.ConnectionError:
        return "Connection error. Please check your network"
    except requests.exceptions.HTTPError as e:
        return f"API Error. {e.response.status_code} - {e.response.json()}"
    except Exception as e:
        return f"Something went wrong. {str(e)}"
    

@app.post("/agent")
def agent_chat(message : Message):
    if not message.session_id:
        return "Session ID is missing"
    if not message.message:
        return "Please type message before sending"
    
    session_id = message.session_id
    user_message = message.message
    customer_name = message.customer_id

    if session_id not in memory:
        memory[session_id] = []

    memory[session_id].append({"role": "user", "content": user_message})
    ai_reply = ask_ai(memory[session_id], customer_name)

    if isinstance(ai_reply, dict):
        memory[session_id].append({"role": "assistant", "content": json.dumps(ai_reply)})
    return ai_reply
