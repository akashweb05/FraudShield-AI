import random
import datetime
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()  # loads .env file if present

# ------------------ DB Config ------------------
MODEL = os.getenv("HF_MODEL", "sentence-transformers/all-MiniLM-L6-v2")  # 384-dim
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "4000"))
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME", "finance")
CA_PATH = os.getenv("CA_PATH")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))
# ------------------------------------------------

accounts = [f"ACC{100+i}" for i in range(1, 51)]  # 50 accounts

categories = {
    "Payment": ["Payment to Vendor X", "Payment to Contractor Z", "Bill Payment", "Rent Payment"],
    "Income": ["Salary Credit", "Bonus Payout", "Freelance Income"],
    "Shopping": ["Amazon Shopping", "Online Shopping Flipkart", "Groceries at Walmart", "Electronics Purchase"],
    "Transfer": ["International Transfer", "Wire Transfer International", "Transfer to Foreign Account"],
    "Transport": ["Uber Ride Payment", "Lyft Ride", "Train Ticket"],
    "Entertainment": ["Netflix Subscription", "Spotify Premium", "Movie Ticket"],
}

def random_transaction():
    account = random.choice(accounts)
    category = random.choice(list(categories.keys()))
    description = random.choice(categories[category])
    amount = round(random.uniform(10, 20000), 2)
    days_ago = random.randint(0, 60)
    date = (datetime.date.today() - datetime.timedelta(days=days_ago)).isoformat()
    return (account, date, description, category, amount)

def insert_transactions(n=100):
    conn = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        ssl_ca=CA_PATH
    )
    cursor = conn.cursor()

    sql = """
    INSERT INTO transactions (account_number, transaction_date, description, category, amount)
    VALUES (%s, %s, %s, %s, %s)
    """

    for _ in range(n):
        txn = random_transaction()
        cursor.execute(sql, txn)

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Inserted {n} transactions into TiDB")

if __name__ == "__main__":
    insert_transactions(200)  # insert 200 rows
