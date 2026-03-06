# Sharjeel — Backend Member Context
## Assigned: ML Models (Loan Prediction + Fraud Detection) + Admin API

Read `backend_Architecture.md` and `backend_rule.md` first.

---

## Your Responsibility

- `ml/train_loan.py` — Train loan approval model
- `ml/train_fraud.py` — Train fraud detection model
- `ml/loan_model.pkl` — Saved trained loan model
- `ml/fraud_model.pkl` — Saved trained fraud model
- `apps/loans/ml_model.py` — Load + use ML models in Django
- `apps/loans/views.py` — Loan apply + status API
- `apps/admin_panel/views.py` — Admin API endpoints

---

## ML Part 1: Loan Prediction

### What it does:
Predicts whether a user is eligible for a loan based on their banking history.

### Kaggle Dataset to Download:
**Bank Loan Prediction Dataset**:
https://www.kaggle.com/datasets/vikasukani/loan-eligible-dataset

This has columns like: Gender, Married, Education, Income, LoanAmount, Credit_History, Loan_Status

### Features to use for prediction (input):
- `yearly_balance` — average of user's yearly balance (from statement CSV)
- `transaction_count` — how many transactions user has made
- `avg_transaction_amount` — average transaction amount
- `account_age_days` — days since account created
- `has_collateral` — 1 or 0

### Target (output):
- `eligible` — 1 (approved) or 0 (rejected)

### Training Script (`ml/train_loan.py`):

```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

# Load Kaggle dataset
df = pd.read_csv('loan_data.csv')  # downloaded from Kaggle

# Clean data
df = df.dropna()

# Feature engineering - map our features to Kaggle columns
# Kaggle has: ApplicantIncome, LoanAmount, Credit_History, Loan_Status
# Map: ApplicantIncome → yearly_balance, Credit_History → has_collateral

# Select features
features = ['ApplicantIncome', 'CoapplicantIncome', 'LoanAmount', 
            'Loan_Amount_Term', 'Credit_History']
X = df[features].fillna(0)
y = (df['Loan_Status'] == 'Y').astype(int)

# Train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Print accuracy
print(f"Accuracy: {model.score(X_test, y_test):.2f}")

# Save model
joblib.dump(model, 'loan_model.pkl')
print("Loan model saved!")
```

### Using ML Model in Django (`apps/loans/ml_model.py`):

```python
import joblib
import os
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), '../../ml/loan_model.pkl')

# Load model once when Django starts
loan_model = joblib.load(MODEL_PATH)

def compute_user_features(user_id, amount, has_collateral):
    """
    Read user's statement CSV and compute features for ML model.
    """
    import os
    DATA_DIR = os.path.join(os.path.dirname(__file__), '../../data')
    stmt_path = os.path.join(DATA_DIR, f'statements/user_{user_id}.csv')
    
    try:
        df = pd.read_csv(stmt_path)
        if df.empty:
            # New user with no history
            return {
                'ApplicantIncome': 0,
                'CoapplicantIncome': 0,
                'LoanAmount': amount / 1000,  # Kaggle uses thousands
                'Loan_Amount_Term': 360,
                'Credit_History': 1 if has_collateral else 0
            }
        
        credits = df[df['type'] == 'credit']['amount']
        yearly_income = credits.sum() / max(1, len(df)) * 12  # estimate
        
        return {
            'ApplicantIncome': yearly_income,
            'CoapplicantIncome': 0,
            'LoanAmount': amount / 1000,
            'Loan_Amount_Term': 360,
            'Credit_History': 1 if (has_collateral or yearly_income > 100000) else 0
        }
    except:
        return {
            'ApplicantIncome': 0, 'CoapplicantIncome': 0,
            'LoanAmount': amount / 1000, 'Loan_Amount_Term': 360,
            'Credit_History': 1 if has_collateral else 0
        }

def predict_loan_eligibility(user_id, amount, has_collateral, user_balance):
    """
    Main function called by loan view.
    Returns: ('approved' | 'rejected' | 'pending', score, message)
    """
    # Rule 1: If balance > 1 million → auto eligible
    if float(user_balance) >= 1000000:
        return 'approved', 1.0, 'Congratulations! Based on your excellent account standing, your loan is approved.'
    
    features = compute_user_features(user_id, amount, has_collateral)
    feature_df = pd.DataFrame([features])
    
    # Get probability score
    prob = loan_model.predict_proba(feature_df)[0][1]  # probability of approval
    
    if prob >= 0.6:
        return 'approved', prob, 'Congratulations! Your loan application has been approved.'
    elif has_collateral:
        return 'pending', prob, 'Your application is under review. Since you have collateral, an admin will review your request.'
    else:
        return 'rejected', prob, 'Based on your account history, we cannot approve this loan at this time.'
```

---

## ML Part 2: Fraud Detection

### What it does:
Detects suspicious transactions automatically and flags them.

### Kaggle Dataset to Download:
**Credit Card Fraud Detection**:
https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

This has: Time, V1-V28 (anonymized features), Amount, Class (0=normal, 1=fraud)

### Training Script (`ml/train_fraud.py`):

```python
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

# Note: creditcard.csv is large (150MB), use a sample
df = pd.read_csv('creditcard.csv').sample(n=50000, random_state=42)

# Features: Amount + time-based features
# For our system, we use: amount, hour_of_day, is_large_transfer
features = ['Amount', 'Time']
X = df[features]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Use Isolation Forest (unsupervised, good for anomaly detection)
model = IsolationForest(contamination=0.01, random_state=42)
model.fit(X_scaled)

joblib.dump({'model': model, 'scaler': scaler}, 'fraud_model.pkl')
print("Fraud model saved!")
```

### Using Fraud Model (`apps/loans/ml_model.py` — add to same file):

```python
fraud_artifacts = joblib.load(os.path.join(os.path.dirname(__file__), '../../ml/fraud_model.pkl'))
fraud_model = fraud_artifacts['model']
fraud_scaler = fraud_artifacts['scaler']

def detect_fraud(user_id, amount, hour_of_day):
    """
    Called after every transaction.
    Returns: (is_fraud: bool, reason: str)
    """
    import numpy as np
    
    # Rule-based checks first (simple, explainable for teacher)
    reasons = []
    
    # Rule 1: Very large transaction
    if amount > 500000:
        reasons.append("Unusually large transaction amount")
    
    # Rule 2: Late night transaction > 100k
    if hour_of_day >= 0 and hour_of_day <= 5 and amount > 100000:
        reasons.append("Large transaction during unusual hours (12AM-5AM)")
    
    # ML check
    features = np.array([[amount, hour_of_day * 3600]])  # match training format
    features_scaled = fraud_scaler.transform(features)
    prediction = fraud_model.predict(features_scaled)  # -1 = anomaly, 1 = normal
    
    if prediction[0] == -1:
        reasons.append("ML model detected anomalous pattern")
    
    is_fraud = len(reasons) > 0
    return is_fraud, '; '.join(reasons) if reasons else ''

def flag_transaction(user_id, transaction_id, reason, severity='medium'):
    """Save fraud flag to fraud_flags.csv"""
    import pandas as pd, os, datetime
    DATA_DIR = os.path.join(os.path.dirname(__file__), '../../data')
    path = os.path.join(DATA_DIR, 'fraud_flags.csv')
    df = pd.read_csv(path)
    new_id = int(df['flag_id'].max()) + 1 if not df.empty else 1
    new_flag = {
        'flag_id': new_id, 'user_id': user_id, 'transaction_id': transaction_id,
        'reason': reason, 'flagged_at': str(datetime.datetime.now()),
        'resolved': False, 'severity': severity
    }
    df = pd.concat([df, pd.DataFrame([new_flag])], ignore_index=True)
    df.to_csv(path, index=False)
```

---

## Loan Views (`apps/loans/views.py`)

### LoanApplyView (POST `/api/loans/apply/`):
```python
# Logic:
# 1. Get user from request.user
# 2. Check if user already has active loan in loans.csv → if yes, return error
# 3. Get: amount, purpose, duration_months, has_collateral, asset_description from request.data
# 4. Call predict_loan_eligibility(user_id, amount, has_collateral, user_balance)
# 5. Save loan record to loans.csv with the status from ML prediction
# 6. Return { status, message }
```

### LoanStatusView (GET `/api/loans/status/`):
```python
# Logic:
# 1. Read loans.csv
# 2. Filter by user_id and status != 'rejected'
# 3. Return latest loan if exists, else { loan: null }
```

---

## Admin Panel Views (`apps/admin_panel/views.py`)

All views here must check `request.user['role'] == 'admin'` first.

**AdminUsersView** (GET `/api/admin/users/`):
- Read users.csv, return all users (exclude password_hash)

**AdminLoanApprovalView** (PUT `/api/admin/loans/{id}/approve/`):
- Read loans.csv → find loan by id
- Update status to 'approved' or 'rejected' based on `request.data['action']`
- Save back to loans.csv

**AdminFraudAlertsView** (GET `/api/admin/fraud-alerts/`):
- Read fraud_flags.csv
- Return all unresolved flags (resolved == False)
- Include user name by joining with users.csv

**AdminAllTransactionsView** (GET `/api/admin/transactions/`):
- Loop through all `data/statements/user_*.csv` files
- Concatenate all into one DataFrame
- Return sorted by date descending (most recent first)

---

## Mohib (Intern) Note
Mohib will observe your code. Make your functions well-commented so he can follow along.

---

## Test Checklist

- [ ] Loan model trains without errors and saves `.pkl`
- [ ] Fraud model trains without errors and saves `.pkl`
- [ ] User with balance > 1M gets auto-approved
- [ ] New user with collateral gets 'pending' status
- [ ] Large night transfer gets flagged
- [ ] Admin can see all fraud flags
- [ ] Admin can approve pending loans
- [ ] All admin endpoints reject non-admin users