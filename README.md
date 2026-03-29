# Pizza Hut Reservation Agent

An AI-powered restaurant agent for Pizza Hut built with FastAPI and Groq AI.
The agent uses function calling and tool integration to perform real actions
like booking tables, checking the menu, and verifying availability.

## Features

- Function calling — AI executes real actions not just answers questions
- Tool integration — complete two API call cycle for natural responses
- Table booking with validation — maximum 20 people per reservation
- Menu checking — returns today's available items
- Availability checking — checks open time slots
- Structured JSON responses — consistent format for all replies
- Multi-session memory — each customer has separate conversation history
- Dynamic context — today's date and specials injected automatically
- Input validation and comprehensive error handling

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | Backend web framework |
| Groq API | AI language model provider |
| LLaMA 3.3 70B | AI model |
| Pydantic | Data validation |
| python-dotenv | Environment variable management |

## Project Structure
```
pizza-hut-agent/
│
├── .venv/               
├── main.py            
├── .env               
└── requirements.txt   
```

## Setup

1. Clone the repository
```
git clone https://github.com/parkash34/pizza-hut-agent
```

2. Create and activate a virtual environment
```
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies
```
pip install -r requirements.txt
```

4. Create a `.env` file and add your Groq API key
```
API_KEY=your_groq_api_key_here
```

5. Run the server
```
uvicorn main:app --reload
```

## API Endpoint

### POST /agent

**Request:**
```json
{
    "session_id": "user_1",
    "customer_id": "Ahmed",
    "message": "Book a table for 4 at 7 PM"
}
```

**Response:**
```json
{
    "reply": {
        "category": "Reservation",
        "answer": "Your table for 4 people is booked at 7 PM!",
        "follow_up": "Would you like to order anything in advance?"
    }
}
```

## Available Tools

| Tool | Description | Parameters |
|---|---|---|
| `book_table` | Books a table | `people`, `time` |
| `check_menu` | Returns today's menu | None |
| `check_availability` | Checks available time slots | `time` |

## How It Works
```
User sends a message
↓
AI decides which tool to call
↓
Python executes the tool function
↓
Result sent back to AI with tool role
↓
AI generates a natural, friendly response
↓
User receives structured JSON reply
```

## Validation Rules

- Maximum 20 people per reservation
- Session ID required for all requests
- Empty messages are rejected

## Environment Variables
```
API_KEY=your_groq_api_key_here
```

## Notes

- Never commit your `.env` file to GitHub
- Conversation history resets when the server restarts
- Agent only handles Pizza Hut-related questions

## 👤 Author

**Ohm Parkash** — [LinkedIn](https://www.linkedin.com/in/om-parkash34/) · [GitHub](https://github.com/parkash34)
