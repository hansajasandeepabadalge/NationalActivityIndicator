# National Activity Indicator - Backend

This is the backend for the National Activity Indicator project, built with FastAPI.

## Prerequisites

- Python 3.8 or higher

## Setup

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone <repository-url>
    cd national_activity_indicator/backend
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment**:
    - On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies**:
    Since `requirements.txt` might be empty initially, install the core dependencies directly:
    ```bash
    pip install fastapi uvicorn pydantic-settings
    ```
    
    *If a `requirements.txt` file exists and is populated, you can run:*
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  Create a `.env` file in the `backend` directory. You can copy the example below:

    ```env
    PROJECT_NAME="National Activity Indicator"
    API_V1_STR="/api/v1"
    # DATABASE_URL="sqlite:///./sql_app.db" # Uncomment and set if using a database
    ```

## Running the Application

To start the server, run:

```bash
uvicorn app.main:app --reload
```

The server will start at `http://127.0.0.1:8000`.

## API Documentation

Once the server is running, you can access the interactive API documentation at:

- **Swagger UI**: [http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs)
- **ReDoc**: [http://127.0.0.1:8000/api/v1/redoc](http://127.0.0.1:8000/api/v1/redoc)
