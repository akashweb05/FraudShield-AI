import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from isolation import detect_anomalies  # your anomaly detection file
import mysql.connector
from dotenv import load_dotenv

# 🔹 Load environment variables from .env
load_dotenv()

app = FastAPI(title="Fraud Detection API")

# 🔹 CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Load embedding model
model = SentenceTransformer(os.getenv("HF_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))

# 🔹 Database configuration from .env
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", "4000")),
    "ssl_ca": os.getenv("CA_PATH", ""),
}

# 🔹 Request schema
class Query(BaseModel):
    text: str
    min_amount: float = 5000


# ---------- Utility functions ----------
def vector_to_sql_str(vector):
    return "[" + ",".join([str(x) for x in vector]) + "]"


def assign_severity(row):
    if row["rule_flag"] == 1 and row["anomaly_flag"] == 1:
        return "High Risk"
    elif row["rule_flag"] == 1:
        return "Medium Risk"
    elif row["anomaly_flag"] == 1:
        return "Suspicious"
    else:
        return "Low Risk"


# ---------- API routes ----------
@app.get("/")
def root():
    return {"message": "Fraud Detection API running"}


@app.post("/search")
def search(query: Query):
    # 1️⃣ Encode query
    query_vector = model.encode(query.text, convert_to_numpy=True)
    vector_str = vector_to_sql_str(query_vector)

    # 2️⃣ Fetch from DB
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    sql = f"""
    SELECT id, account_number, description, amount,
           VEC_COSINE_DISTANCE(embedding_vec, '{vector_str}') AS dist
    FROM transactions
    ORDER BY dist
    LIMIT 20;
    """
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    # 3️⃣ Rule-based flags
    for r in results:
        explanations = []

        if query.text.lower() in r["description"].lower():
            if r["amount"] > query.min_amount:
                explanations.append(f"Amount > {query.min_amount}")
            if "International" in r["description"]:
                explanations.append("Contains 'International'")
            if "Wire Transfer" in r["description"]:
                explanations.append("Contains 'Wire Transfer'")
            if "Bonus Payout" in r["description"]:
                explanations.append("Contains 'Bonus Payout'")

        r["rule_flag"] = 1 if explanations else 0
        r["explanation"] = " & ".join(explanations) if explanations else "No rule triggered"

    # 4️⃣ Anomaly detection
    results_with_anomaly = detect_anomalies(results)

    # 5️⃣ Assign severity
    for r in results_with_anomaly:
        r["severity"] = assign_severity(r)

    return {"results": results_with_anomaly}
