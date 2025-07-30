Steps to run 'Parcerito Chat Boot' 

# The first three steps are required before to run

A. Bash execution
    A.1. python -m venv venv  # this step generate virtual env \
    A.2. venv\Scripts\activate # activate env for windows \
    A.3. pip install fastapi uvicorn psycopg2-binary sqlalchemy pydantic pydantic[email] python-dotenv
## Security
    A.4. pip install python-jose[cryptography] passlib[bcrypt]
## Langchain and AI
    A.5. pip install langgraph langchain[openai] langchain-community

B. Run project \
    B.1. -> Define env variables in a .env file -> Define this ones: OPENAI_API_KEY, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, CONNECTION
    B.2. -> src.main:app --reload or uvicorn src.main:app --reload


# Note
It is crucial to have a postgres database with the name: PerficientTest, with user: postgres and password: admin.