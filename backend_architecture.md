# Backend Architecture — SmartBank System

## Tech Stack
- **Framework**: Django 4.x + Django REST Framework (DRF)
- **Authentication**: Token Authentication (DRF built-in)
- **Database**: CSV files only (no SQLite, no PostgreSQL)
- **ML Libraries**: scikit-learn, pandas, numpy
- **Deployment**: Localhost (can be deployed to Railway or Render)

---

## Project Folder Structure

```
backend/
├── manage.py
├── requirements.txt
├── smartbank/               ← Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── data/                    ← ALL CSV files live here
│   ├── users.csv
│   ├── tokens.csv
│   ├── loans.csv
│   ├── fraud_flags.csv
│   └── statements/          ← Per-user transaction CSVs
│       ├── user_1.csv
│       ├── user_2.csv
│       └── ...
├── apps/
│   ├── auth_app/            ← Login, register, token management
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── csv_db.py        ← CSV read/write helpers for users
│   ├── accounts/            ← Balance, profile
│   │   ├── views.py
│   │   └── urls.py
│   ├── transactions/        ← Transfer, history, DSA logic
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── dsa_structures.py  ← Stack/Queue DSA logic
│   ├── loans/               ← Loan application, ML prediction
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── ml_model.py      ← ML prediction logic
│   └── admin_panel/         ← Admin-only endpoints
│       ├── views.py
│       └── urls.py
└── ml/                      ← ML models and training
    ├── loan_model.pkl        ← Trained loan model (saved)
    ├── fraud_model.pkl       ← Trained fraud model (saved)
    ├── train_loan.py         ← Script to train loan model
    └── train_fraud.py        ← Script to train fraud model
```

---

## CSV Database Design

### `data/users.csv`
```
user_id,name,email,password_hash,cnic,account_number,account_type,balance,role,created_at,is_active
1,Ali Hassan,ali@gmail.com,hashed_pass,3520212345678,12345678901,savings,150000.00,user,2024-01-15,True
2,Admin User,admin@bank.com,hashed_pass,1234512345671,00000000001,admin,0.00,admin,2024-01-01,True
```

### `data/tokens.csv`
```
token,user_id,created_at
abc123xyz,1,2025-03-01 10:00:00
```

### `data/loans.csv`
```
loan_id,user_id,amount,purpose,duration_months,has_collateral,asset_description,status,applied_at,approved_at,ml_score
1,1,500000,home,24,True,House in Lahore,approved,2025-01-10,2025-01-11,0.87
```

### `data/fraud_flags.csv`
```
flag_id,user_id,transaction_id,reason,flagged_at,resolved,severity
1,1,TXN001,Large unusual transfer,2025-02-01,False,high
```

### `data/statements/user_1.csv` (one file per user)
```
transaction_id,date,description,amount,type,balance_after,recipient_account,sender_account
TXN001,2025-03-01,Transfer to Hamza,5000.00,debit,145000.00,98765432101,12345678901
TXN002,2025-03-02,Salary Credit,50000.00,credit,195000.00,,12345678901
```

---

## API Endpoints Summary

| Method | URL | App | Purpose |
|--------|-----|-----|---------|
| POST | `/api/auth/login/` | auth_app | Login → return token |
| POST | `/api/auth/register/` | auth_app | Register new user |
| POST | `/api/auth/logout/` | auth_app | Delete token |
| GET | `/api/account/balance/` | accounts | Get balance + account info |
| GET | `/api/account/profile/` | accounts | Get full profile |
| POST | `/api/transactions/transfer/` | transactions | Transfer money |
| GET | `/api/transactions/history/` | transactions | Get statement |
| POST | `/api/loans/apply/` | loans | Apply + ML prediction |
| GET | `/api/loans/status/` | loans | Check existing loan |
| GET | `/api/admin/users/` | admin_panel | All users list |
| PUT | `/api/admin/loans/{id}/approve/` | admin_panel | Approve/reject loan |
| GET | `/api/admin/fraud-alerts/` | admin_panel | All fraud flags |
| GET | `/api/admin/transactions/` | admin_panel | All transactions |

---

## DSA Concepts in Backend

| DSA Structure | Location | Purpose |
|---------------|----------|---------|
| Stack | `transactions/dsa_structures.py` | Undo last transfer / transaction rollback |
| Queue | `transactions/dsa_structures.py` | Queue pending transactions for processing |
| Linked List | `transactions/dsa_structures.py` | Traverse transaction history |
| Hash Map (dict) | `auth_app/csv_db.py` | Fast user lookup by ID or email |
| Binary Search | `admin_panel/views.py` | Search users by account number |

These DSA implementations will be shown to the teacher as evidence of the assignment.

---

## Authentication Flow

1. Register → password hashed using `hashlib` (no Django auth system)
2. Login → compare hash → generate random token → save in `tokens.csv`
3. Every protected request → read `Authorization: Token abc123` header → look up in `tokens.csv` → get user_id → proceed

### Custom Token Authentication Class:
```python
# smartbank/authentication.py
class CSVTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Token '):
            return None
        token = auth_header.split(' ')[1]
        user = get_user_by_token(token)  # reads tokens.csv + users.csv
        if not user:
            raise AuthenticationFailed('Invalid token')
        return (user, token)
```

---

## Error Response Format

Always return JSON errors in this format:
```json
{ "error": "Descriptive error message here" }
```

Success format:
```json
{ "message": "Success message", "data": { ... } }
```

---

## CORS Setup

Install `django-cors-headers` and allow `http://localhost:5173` (Vite frontend).

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://your-vercel-app.vercel.app"
]
```

---

## Running Locally

```bash
cd backend
pip install -r requirements.txt
python manage.py runserver
```

Backend runs at `http://localhost:8000`