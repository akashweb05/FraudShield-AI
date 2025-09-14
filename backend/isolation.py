import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_anomalies(transactions):
    """
    transactions: list of dicts from DB
    Returns same list with anomaly_score and anomaly_flag
    """
    if not transactions:
        return []

    # Convert to DataFrame
    df = pd.DataFrame(transactions)

    # Use numeric features for anomaly detection
    # Here: amount + embedding summary (mean embedding) optional
    X = df[['amount']].copy()

    # Train IsolationForest
    clf = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    clf.fit(X)

    # Predict anomaly (-1 = anomaly, 1 = normal)
    anomaly_flags = clf.predict(X)
    # anomaly scores (negative = more anomalous)
    anomaly_scores = clf.decision_function(X)

    df['anomaly_flag'] = (anomaly_flags == -1).astype(int)
    df['anomaly_score'] = -anomaly_scores  # higher = more anomalous

    # Convert back to list of dicts
    return df.to_dict(orient='records')
