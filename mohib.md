# Mohib — Backend Member Context (Intern)
## Role: Learn + Support + Testing

Read `backend_Architecture.md` and `backend_rule.md` first.

---

## About Your Role

You are the backend intern. Your job is to:
1. Learn by reading Hamza and Sharjeel's code
2. Write the `requirements.txt` and project setup files
3. Test all API endpoints using a tool called **Postman** or **curl**
4. Write sample test data in CSV files
5. Help document the API

---

## Your Files

- `requirements.txt`
- `README.md` (setup instructions)
- `data/users.csv` (populate with sample data)
- `data/tokens.csv` (create empty with headers)
- `data/loans.csv` (create empty with headers)
- `data/fraud_flags.csv` (create empty with headers)

---

## File 1: `requirements.txt`

```
django==4.2.0
djangorestframework==3.14.0
django-cors-headers==4.3.0
pandas==2.1.0
numpy==1.26.0
scikit-learn==1.3.0
joblib==1.3.0
```

---

## File 2: `README.md`

Write setup instructions:

```markdown
# SmartBank Backend Setup

## Requirements
- Python 3.10+
- pip

## Installation
1. Clone the project
2. Go to backend folder: cd backend
3. Install requirements: pip install -r requirements.txt
4. Run server: python manage.py runserver

## Project runs on: http://localhost:8000
```

---

## File 3: Sample CSV Data

### `data/users.csv` — Create 5 sample users:

```
user_id,name,email,password_hash,cnic,account_number,account_type,balance,role,created_at,is_active
1,Ali Hassan,ali@gmail.com,8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92,3520212345678,12345678901,savings,150000.00,user,2024-01-15,True
2,Sarah Khan,sarah@gmail.com,8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92,4230156789012,98765432101,savings,250000.00,user,2024-02-10,True
3,Ahmed Raza,ahmed@gmail.com,8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92,3320198765432,11122233301,current,1500000.00,user,2023-12-01,True
4,Fatima Noor,fatima@gmail.com,8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92,3630145678901,44455566601,savings,75000.00,user,2024-03-20,True
5,Admin User,admin@smartbank.com,8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92,1234512345671,00000000001,admin,0.00,admin,2024-01-01,True
```

Note: The password hash above is SHA256 of "123456" — so all test accounts use password `123456`.

### `data/tokens.csv` — Start empty:
```
token,user_id,created_at
```

### `data/loans.csv` — Start empty:
```
loan_id,user_id,amount,purpose,duration_months,has_collateral,asset_description,status,applied_at,approved_at,ml_score
```

### `data/fraud_flags.csv` — Start empty:
```
flag_id,user_id,transaction_id,reason,flagged_at,resolved,severity
```

### `data/statements/user_1.csv` — Sample transactions for user 1:
```
transaction_id,date,description,amount,type,balance_after,recipient_account,sender_account
TXN001,2025-01-05,Salary Credit,100000.00,credit,100000.00,,12345678901
TXN002,2025-01-10,Transfer to Sarah,20000.00,debit,80000.00,98765432101,12345678901
TXN003,2025-02-05,Salary Credit,100000.00,credit,180000.00,,12345678901
TXN004,2025-02-15,Grocery Shopping,5000.00,debit,175000.00,,12345678901
TXN005,2025-03-01,Transfer from Ahmed,25000.00,credit,200000.00,,11122233301
TXN006,2025-03-05,Salary Credit,100000.00,credit,300000.00,,12345678901
TXN007,2025-03-10,Rent Payment,50000.00,debit,250000.00,,12345678901
```

Create similar files for users 2, 3, and 4.

---

## How to Test APIs with Postman

1. Download Postman: https://www.postman.com/downloads/
2. Create a new Collection called "SmartBank API"

### Test 1: Register
```
Method: POST
URL: http://localhost:8000/api/auth/register/
Body (JSON):
{
  "name": "Test User",
  "email": "test@gmail.com",
  "password": "123456",
  "cnic": "3520298765432"
}
Expected: { "message": "Registered successfully" }
```

### Test 2: Login
```
Method: POST
URL: http://localhost:8000/api/auth/login/
Body (JSON):
{
  "email": "ali@gmail.com",
  "password": "123456"
}
Expected: { "token": "...", "user": { "id": 1, "name": "Ali Hassan", "role": "user" } }
```

### Test 3: Get Balance (requires token)
```
Method: GET
URL: http://localhost:8000/api/account/balance/
Headers: Authorization: Token <paste token from login>
Expected: { "balance": 150000.0, "account_number": "12345678901", "name": "Ali Hassan" }
```

### Test 4: Transfer
```
Method: POST
URL: http://localhost:8000/api/transactions/transfer/
Headers: Authorization: Token <token>
Body (JSON):
{
  "recipient_account": "98765432101",
  "amount": 5000,
  "description": "Test transfer"
}
Expected: { "message": "Transfer successful", "transaction_id": "..." }
```

---

## Your Learning Tasks

1. Read `backend_Architecture.md` completely — understand the folder structure
2. Understand what CSV is and why we use it instead of a database
3. Read `hamza.md` — understand how authentication works with tokens
4. Read `sharjeel.md` — understand what Machine Learning does here
5. Run all API tests above and write down what works and what doesn't
6. Ask Hamza or Sharjeel if something doesn't work — provide the exact error message

---

## What is SHA256 Password Hash?

When a user sets password "123456", we don't store "123456" directly. We store a scrambled version called a hash. This hash is always the same for the same password, so we can compare — but no one can reverse it back to "123456".

```python
import hashlib
hash = hashlib.sha256("123456".encode()).hexdigest()
# Result: 8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92
```