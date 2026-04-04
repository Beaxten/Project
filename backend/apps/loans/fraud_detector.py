import os
import datetime
import pandas as pd
import joblib

DATA_DIR   = os.path.join(os.path.dirname(__file__), '../../data')
FRAUD_CSV  = os.path.join(DATA_DIR, 'fraud_flags.csv')
STMTS_DIR  = os.path.join(DATA_DIR, 'statements')
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../../ml/fraud_model.pkl')

# ── Load model once ────────────────────────────────────────────────────
_artifacts = None

def load_model():
    global _artifacts
    if _artifacts is None and os.path.exists(MODEL_PATH):
        _artifacts = joblib.load(MODEL_PATH)
    return _artifacts


def get_user_avg(user_id):
    """Get this user's average debit amount from their statement CSV."""
    stmt_path = os.path.join(STMTS_DIR, f'user_{user_id}.csv')
    try:
        df     = pd.read_csv(stmt_path)
        debits = df[df['type'] == 'debit']['amount'].astype(float)
        return debits.mean() if not debits.empty else 0.0
    except Exception:
        return 0.0


def detect_fraud(user_id, amount, hour_of_day):

    artifacts = load_model()

    user_avg      = get_user_avg(user_id)
    amount_vs_avg = (amount / user_avg) if user_avg > 0 else 1.0
    is_large      = 1 if amount > 100000 else 0

    features = pd.DataFrame([{
        'Amount':           amount,
        'hour':             hour_of_day,
        'amount_vs_avg':    round(amount_vs_avg, 4),
        'is_large_transfer': is_large,
    }])

    if artifacts:
        scaler     = artifacts['scaler']
        model      = artifacts['model']

        scaled     = scaler.transform(features)
        prediction = model.predict(scaled)[0]
        prob       = model.predict_proba(scaled)[0][1]

        is_fraud = bool(prediction == 1)
        reason   = ''

        if is_fraud:
            reason = f'ML fraud score {prob:.0%}'
            if amount > 100000:
                reason += f'; Large transfer PKR {amount:,.0f}'
            if hour_of_day <= 5:
                reason += f'; Unusual hour {hour_of_day}:00 AM'
            if amount_vs_avg > 3:
                reason += f'; {amount_vs_avg:.1f}x above your average'

        return is_fraud, reason

    else:
        print("fraud_model.pkl not found — run ml/train_fraud.py first")
        is_fraud = amount > 100000 or (hour_of_day <= 5 and amount > 100000)
        reason   = 'Rule-based flag (ML model not loaded)' if is_fraud else ''
        return is_fraud, reason

def flag_transaction(user_id, transaction_id, reason, severity='medium'):
    print(f"Saving fraud flag → user:{user_id} txn:{transaction_id} reason:{reason}")

    try:
        df = pd.read_csv(FRAUD_CSV)
    except Exception:
        df = pd.DataFrame(columns=[
            'flag_id','user_id','transaction_id',
            'reason','flagged_at','resolved','severity'
        ])

    new_id   = int(df['flag_id'].max()) + 1 if not df.empty else 1
    new_flag = {
        'flag_id':        new_id,
        'user_id':        user_id,
        'transaction_id': transaction_id,
        'reason':         reason,
        'flagged_at':     str(datetime.datetime.now()),
        'resolved':       False,
        'severity':       severity,
    }
    df = pd.concat([df, pd.DataFrame([new_flag])], ignore_index=True)
    df.to_csv(FRAUD_CSV, index=False)
    print(f"fraud_flags.csv updated — total flags: {len(df)}")