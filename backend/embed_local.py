import time
from sentence_transformers import SentenceTransformer
import mysql.connector
from dotenv import load_dotenv
import os

# ---------- Load Environment Variables ----------
load_dotenv()  # loads .env file if present

MODEL = os.getenv("HF_MODEL", "sentence-transformers/all-MiniLM-L6-v2")  # 384-dim
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "4000"))
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME", "finance")
CA_PATH = os.getenv("CA_PATH")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))
# ------------------------------------------------

print("Loading model:", MODEL)
model = SentenceTransformer(MODEL)  # first run will download model files
print("Model loaded. Encoding dimension:", model.get_sentence_embedding_dimension())

def connect_db():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        ssl_ca=CA_PATH   # TiDB TLS CA file
    )

def format_vector_for_tidb(vec):
    # format floats with '.' decimal and reasonable precision
    return "[" + ",".join(f"{float(x):.10g}" for x in vec.tolist()) + "]"

def fetch_rows_without_embedding(conn, limit):
    cur = conn.cursor()
    cur.execute(
        "SELECT id, IFNULL(description,'') "
        "FROM transactions WHERE embedding_vec IS NULL LIMIT %s",
        (limit,)
    )
    rows = cur.fetchall()
    cur.close()
    return rows

def update_embedding(conn, id, vec_literal):
    cur = conn.cursor()
    cur.execute(
        "UPDATE transactions SET embedding_vec = %s WHERE id = %s",
        (vec_literal, id)
    )
    conn.commit()
    cur.close()

def main():
    conn = connect_db()
    try:
        while True:
            rows = fetch_rows_without_embedding(conn, BATCH_SIZE)
            if not rows:
                print("No more rows to embed. Done.")
                break

            ids = [r[0] for r in rows]
            texts = [r[1] for r in rows]
            print(f"Encoding batch size {len(texts)} ...")
            embeddings = model.encode(
                texts, batch_size=BATCH_SIZE,
                convert_to_numpy=True, show_progress_bar=False
            )

            for idx, emb in zip(ids, embeddings):
                vec_literal = format_vector_for_tidb(emb)
                update_embedding(conn, idx, vec_literal)

            print(f"Updated {len(ids)} rows. Sleeping briefly...")
            time.sleep(0.2)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
