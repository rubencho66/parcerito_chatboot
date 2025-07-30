# Steps to Run 'Parcerito Chat Boot'

## 1. Setup (Required Before Running)

### A. Bash Execution

1. **Create virtual environment:**
   ```
   python -m venv venv
   ```
2. **Activate environment (Windows):**
   ```
   venv\Scripts\activate
   ```
3. **Install core dependencies:**
   ```
   pip install fastapi uvicorn psycopg2-binary sqlalchemy pydantic pydantic[email] python-dotenv
   ```

#### Security Dependencies

4. **Install security packages:**
   ```
   pip install python-jose[cryptography] passlib[bcrypt]
   ```

#### Langchain and AI

5. **Install AI-related packages:**
   ```
   pip install langgraph langchain[openai] langchain-community openai
   ```

---

## 2. Run the Project

1. **Define environment variables in a `.env` file:**

   - `OPENAI_API_KEY`
   - `SECRET_KEY`
   - `ALGORITHM`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`
   - `CONNECTION`

2. **Start the application:**
   ```
   uvicorn src.main:app --reload
   ```
   _(or use `src.main:app --reload` if supported)_

---

## Note

It is crucial to have a PostgreSQL database named **PerficientTest** with:

- **User:** postgres
- **Password:** admin
