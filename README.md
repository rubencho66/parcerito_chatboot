# Steps to Run 'Parcerito Chat Boot'

## 1. Setup (Required Before Running)

### A. Bash Execution

1. **Create virtual environment:**

   ```bash
   python -m venv venv
   ```

2. **Activate environment (Windows):**

   ```bash
   venv\Scripts\activate
   ```

3. **Install core dependencies:**

   ```bash
   pip install fastapi uvicorn psycopg2-binary sqlalchemy pydantic pydantic[email] python-dotenv
   ```

### Security Dependencies

1. **Install security packages:**

   ```bash
   pip install python-jose[cryptography] passlib[bcrypt]
   ```

### Langchain and AI

1. **Install AI-related packages:**

   ```bash
   pip install langgraph langchain[openai] langchain-community openai
   ```

2. **Install torch for local models with GPU**

   ```bash
   pip install sentence_transformers torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

---

## 2. Run the Project

1. **Define environment variables in a `.env` file:**

   - `OPENAI_API_KEY`
   - `SECRET_KEY`
   - `ALGORITHM`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`
   - `CONNECTION`
   - `USE_LOCAL_MODEL`
   - `LOCAL_MODEL_NAME`
   - `LOCAL_LLM_BASE_URL`
   - `LOCAL_LLM_API_KEY`

2. **Start the application:**

   ```bash
   uvicorn src.main:app --reload
   ```

   _(or use `src.main:app --reload` if supported)_

---

## Note

It is crucial to have a PostgreSQL database named **PerficientTest** with:

- **User:** postgres
- **Password:** admin
