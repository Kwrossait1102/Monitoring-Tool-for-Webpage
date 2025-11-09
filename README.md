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
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Edit the `.env` file in the project root directory:

```ini
# Target webpage for monitoring
TARGET_URL=https://www.uni-stuttgart.de

# PostgreSQL connection string
DATABASE_URL=postgresql+psycopg://postgres:123456@localhost:5432/monitor

# Optional debug flag
DEBUG=True
```

## Running this application



