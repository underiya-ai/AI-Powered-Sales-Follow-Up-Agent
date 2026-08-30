## How to Run Locally

Follow these steps to run FollowAI on your local laptop.

### 1. Clone the Repository

```bash
1) git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
2) cd YOUR_REPOSITORY_NAME
3) py -3.11 -m venv env
4) .\env\Scripts\Activate.ps1
5) pip install -r requirements.txt
6) Add the required API keys and configuration values:
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key

LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=AI-Powered Sales Follow-Up Agent

7)  Run the Backend

From the root project directory, run:
uvicorn backend.main:app --reload
8). Open a New Terminal for the Frontend

Keep the backend terminal running.
cd followaifront
9)  Install Frontend Dependencies

Install the required Node.js packages:
npm install
10). Start the Frontend
 npm run dev
11) Open the frontend URL and start using FollowAI.


Local Development Flow

The application runs with two services:

                 FollowAI
                    |
          ┌─────────┴─────────┐
          |                   |
      Frontend             Backend
       React                FastAPI
          |                   |
   localhost:5173       127.0.0.1:8000
                              |
                    AI Sales Pipeline
                              |
             ┌────────────────┼────────────────┐
             |                |                |
         Groq / LLM       LangGraph        LangSmith
             |                |           Observability
        AI Analysis       Agent Flow       & Tracing
                              |
                         Gmail API
                              |
                      Automatic Email
