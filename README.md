Steps to run 'Parcerito Chat Boot' 

# The first three steps are required before to run


A. Bash execution
    A.1. python -m venv venv  # this step generate virtual env \
    A.2. venv\Scripts\activate # activate env for windows \
    A.3. pip install fastapi uvicorn psycopg2-binary sqlalchemy pydantic 
## Security
    A.4. pip install python-jose[cryptography] passlib[bcrypt]

B. Run project \
    B.1. -> src.main:app --reload


# Note
It is crucial to have a postgres database with the name: PerficientTest, with user: postgres and password: admin.


