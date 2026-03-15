import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE   # ← pip install imbalanced-learn
import joblib
import os

df = pd.read_csv('creditcard.csv')

# ── Feature engineering (same as before) ──────────────────────────────
df['hour']             = (df['Time'] / 3600 % 24).astype(int)
overall_avg            = df['Amount'].mean()
df['amount_vs_avg']    = df['Amount'] / overall_avg
threshold_75           = df['Amount'].quantile(0.75)
df['is_large_transfer'] = (df['Amount'] > threshold_75).astype(int)

FEATURES = ['Amount', 'hour', 'amount_vs_avg', 'is_large_transfer']

X = df[FEATURES]
y = df['Class']

# ── FIX 1: Use ALL fraud cases + more normal cases ─────────────────────
# Before we used only 5000 normal — now use 10000
# More data = better learning
fraud_df  = df[df['Class'] == 1]                        # all 492 fraud
normal_df = df[df['Class'] == 0].sample(n=10000, random_state=42)
balanced_df = pd.concat([fraud_df, normal_df]).sample(frac=1, random_state=42)

X_balanced = balanced_df[FEATURES]
y_balanced = balanced_df['Class']

print(f"Before SMOTE — Fraud: {y_balanced.sum()}, Normal: {len(y_balanced)-y_balanced.sum()}")

# ── FIX 2: SMOTE — artificially creates more fraud examples ───────────
# SMOTE = Synthetic Minority Oversampling Technique
# It looks at existing fraud cases and generates new similar ones
# This gives the model many more fraud patterns to learn from
scaler   = StandardScaler()
X_scaled = scaler.fit_transform(X_balanced)

smote    = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_scaled, y_balanced)

print(f"After  SMOTE — Fraud: {y_resampled.sum()}, Normal: {len(y_resampled)-y_resampled.sum()}")

# ── Train/Test split ───────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X_resampled, y_resampled,
    test_size  = 0.2,
    random_state = 42,
    stratify   = y_resampled
)

# ── FIX 3: Better model settings ──────────────────────────────────────
# class_weight balanced  → penalizes missing fraud more than missing normal
# n_estimators 200       → more trees = more accurate
# max_depth 10           → prevents overfitting
model = RandomForestClassifier(
    n_estimators = 200,       # was 100
    max_depth    = 10,        # new — prevents overfitting
    class_weight = 'balanced',
    random_state = 42,
    min_samples_leaf = 2      # new — smoother decision boundaries
)
model.fit(X_train, y_train)

# ── Evaluate ───────────────────────────────────────────────────────────
y_pred = model.predict(X_test)
print("\n=== Model Performance ===")
print(classification_report(y_test, y_pred, target_names=['Normal', 'Fraud']))

# ── Save ───────────────────────────────────────────────────────────────
joblib.dump({
    'model':    model,
    'scaler':   scaler,
    'features': FEATURES
}, 'fraud_model.pkl')

print("fraud_model.pkl saved!")