# -Monitoring-Tool-for-Webpage

This FastAPI-based application periodically checks the availability and response time of a target website and stores the results in a PostgreSQL database.  
It automatically performs a check every **60 seconds**, calculates uptime statistics, and provides several API endpoints for real-time monitoring.

---

## Features

- Automatic background check every 60 seconds  
- Data stored in PostgreSQL using SQLAlchemy ORM  
- API endpoints for latest records and statistics  
- Configurable target URL via `.env` file  
- Thread-safe in-memory counters for uptime calculation  

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Kwrossait1102/Monitoring-Tool-for-Webpage.git
cd your-repo-name
```

### 2. Install dependencies

Before installing dependencies, you should have already installed **Python 3.10+** and **PostgreSQL** on your device.  
To install all required packages, run the following command in the **root directory of the project**:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Edit the `.env` file in the project root directory:

```ini
# Target webpage for monitoring
TARGET_URL=https://www.uni-stuttgart.de

# PostgreSQL connection string, change **password** to your own password
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/monitor

# Optional debug flag
DEBUG=True
```

## Running this application

Start the FastAPI server with uvicorn (Please run this command in the **root directory of the project**):

```bash
# Run the application locally on port 8000
python -m uvicorn app.main:app --reload --port 8000
```

- After startup, the application will automatically:
- Perform a website availability check every 60 seconds
- Store results in the database
- Provide access to monitoring data through several endpoints

## Running Test

A simple pytest is provided to check that the root API endpoint ("/") responds correctly:

```bash
# Run the test in the **root directory of the project**
pytest -q
```

## Example Output

**GET /**  

```json
{
  "url": "https://www.uni-stuttgart.de",
  "status_code": 200,
  "available": true,
  "latency_ms": 135.42,
  "ttfb_ms": 54.11,
  "response_size_bytes": 18903,
  "consecutive_failures": 0,
  "availability_pct_since_start": 100.0
}
```

## API endpoints

```markdown

| Endpoint | Method | Description |
|-----------|--------|-------------|
| `/` | GET | Perform a manual availability check |
| `/records` | GET | Retrieve recent check records from database |
| `/stats` | GET | View uptime and failure statistics |

```

## License

MIT License © 2025 Qianyu Bu

<!-- End of README -->
