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