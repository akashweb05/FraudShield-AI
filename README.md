# FraudShield AI

**AI-powered fraud detection system using vector embeddings, rule-based checks, and anomaly detection on TiDB Cloud.**

## Project Structure


FraudShield-AI/
├─ backend/ # FastAPI backend, database embedding scripts, anomaly detection
├─ frontend/ # React.js frontend, demo UI


## Features
- Converts transaction descriptions into **vector embeddings** for semantic search.
- **Rule-based checks** for suspicious amounts, keywords, and patterns.
- **Anomaly detection** with Isolation Forest.
- Assigns **risk severity**: Low, Medium, Suspicious, High.
- Provides a **frontend UI** to query transactions and view results.

## Built With
- **Languages:** Python, JavaScript
- **Backend:** FastAPI, Pydantic
- **Machine Learning:** sentence-transformers, scikit-learn
- **Database:** TiDB Cloud
- **Frontend:** React.js, Tailwind CSS
- **Security:** SSL/TLS for database connections
- **Other Tools:** MySQL Connector, python-dotenv, numpy, pandas

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- TiDB Cloud account
- `.env` file with your database credentials (see `.env.example`)

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Fill in your credentials in .env
python embed_local.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Demo
[coming soon]

## License
This project is licensed under the MIT License.
