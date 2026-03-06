# Hamza — Backend Member Context
## Assigned: Django API + CSV Database + DSA Logic + Core Banking

Read `backend_Architecture.md` and `backend_rule.md` first.

---

## Your Responsibility

You are the core backend developer. You build the foundation everyone else depends on.

Your files:
- `smartbank/settings.py` — Django config
- `smartbank/urls.py` — Root URL config
- `smartbank/authentication.py` — Custom CSV token auth
- `apps/auth_app/` — Login, register, logout
- `apps/accounts/` — Balance, profile endpoints
- `apps/transactions/` — Transfer + history + DSA
- All `data/*.csv` files — Create and maintain CSV database structure

---

## Step 1: Django Project Setup

### `smartbank/settings.py` key additions:
```python
INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'apps.auth_app',
    'apps.accounts',
    'apps.transactions',
    'apps.loans',
    'apps.admin_panel',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # MUST be first
    'django.middleware.common.CommonMiddleware',
    # ... rest of middleware
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'smartbank.authentication.CSVTokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [],
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]
```

---

## Step 2: CSV Database Initialization

Create these CSV files in `data/` folder with correct headers.

### `data/users.csv` — Download from Kaggle:
Use this dataset as base user data: https://www.kaggle.com/datasets/shivamb/bank-customer-churn-modelling
Adapt the columns to match this schema. Add fake Pakistani names, CNIC, account numbers.

Required columns:
```
user_id,name,email,password_hash,cnic,account_number,account_type,balance,role,created_at,is_active
```

Start with at least 10 sample users + 1 admin user.

### `data/tokens.csv`:
```
token,user_id,created_at
```
(Start empty, rows added on login)

### `data/loans.csv`:
```
loan_id,user_id,amount,purpose,duration_months,has_collateral,asset_description,status,applied_at,approved_at,ml_score
```

### `data/fraud_flags.csv`:
```
flag_id,user_id,transaction_id,reason,flagged_at,resolved,severity
```

### Create statement folder + sample files:
For each sample user, create `data/statements/user_{id}.csv`:
```
transaction_id,date,description,amount,type,balance_after,recipient_account,sender_account
```

---

## Step 3: Custom Authentication (`smartbank/authentication.py`)

```python
import pandas as pd
import os
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')

def get_user_by_token(token):
    tokens_path = os.path.join(DATA_DIR, 'tokens.csv')
    users_path = os.path.join(DATA_DIR, 'users.csv')
    
    try:
        tokens_df = pd.read_csv(tokens_path)
        row = tokens_df[tokens_df['token'] == token]
        if row.empty:
            return None
        user_id = int(row.iloc[0]['user_id'])
        
        users_df = pd.read_csv(users_path)
        user_row = users_df[users_df['user_id'] == user_id]
        if user_row.empty:
            return None
        return user_row.iloc[0].to_dict()
    except:
        return None

class CSVTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Token '):
            return None
        token = auth_header.split(' ')[1]
        user = get_user_by_token(token)
        if not user:
            raise AuthenticationFailed('Invalid or expired token.')
        return (user, token)
```

---

## Step 4: Auth App (`apps/auth_app/`)

### `apps/auth_app/csv_db.py` — CSV helper functions:

```python
import pandas as pd, os, hashlib, secrets

DATA_DIR = os.path.join(os.path.dirname(__file__), '../../data')
USERS_CSV = os.path.join(DATA_DIR, 'users.csv')
TOKENS_CSV = os.path.join(DATA_DIR, 'tokens.csv')

def hash_password(pwd): return hashlib.sha256(pwd.encode()).hexdigest()
def verify_password(pwd, h): return hash_password(pwd) == h
def generate_token(): return secrets.token_hex(32)

def get_user_by_email(email):
    df = pd.read_csv(USERS_CSV)
    r = df[df['email'] == email]
    return r.iloc[0].to_dict() if not r.empty else None

def get_user_by_id(uid):
    df = pd.read_csv(USERS_CSV)
    r = df[df['user_id'] == int(uid)]
    return r.iloc[0].to_dict() if not r.empty else None

def email_exists(email):
    df = pd.read_csv(USERS_CSV)
    return not df[df['email'] == email].empty

def create_user(name, email, password, cnic):
    df = pd.read_csv(USERS_CSV)
    new_id = int(df['user_id'].max()) + 1
    import random, datetime
    account_number = str(random.randint(10000000000, 99999999999))
    new_user = {
        'user_id': new_id, 'name': name, 'email': email,
        'password_hash': hash_password(password), 'cnic': cnic,
        'account_number': account_number, 'account_type': 'savings',
        'balance': 0.0, 'role': 'user',
        'created_at': datetime.datetime.now().strftime('%Y-%m-%d'),
        'is_active': True
    }
    df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
    df.to_csv(USERS_CSV, index=False)
    # Create empty statement file
    stmt_path = os.path.join(DATA_DIR, f'statements/user_{new_id}.csv')
    pd.DataFrame(columns=['transaction_id','date','description','amount','type','balance_after','recipient_account','sender_account']).to_csv(stmt_path, index=False)
    return new_user

def save_token(token, user_id):
    import datetime
    df = pd.read_csv(TOKENS_CSV)
    new_row = {'token': token, 'user_id': user_id, 'created_at': str(datetime.datetime.now())}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(TOKENS_CSV, index=False)

def delete_token(token):
    df = pd.read_csv(TOKENS_CSV)
    df = df[df['token'] != token]
    df.to_csv(TOKENS_CSV, index=False)
```

### `apps/auth_app/views.py`:

**LoginView** (POST `/api/auth/login/`):
- Receive `{ email, password }`
- Get user by email → verify password
- Generate token → save to tokens.csv
- Return `{ token, user: { id, name, email, role } }`

**RegisterView** (POST `/api/auth/register/`):
- Receive `{ name, email, password, cnic }`
- Check email not already used
- Call `create_user()`
- Return `{ message: "Registered successfully" }`

**LogoutView** (POST `/api/auth/logout/`):
- Delete token from tokens.csv
- Return `{ message: "Logged out" }`

---

## Step 5: Accounts App (`apps/accounts/`)

**BalanceView** (GET `/api/account/balance/`):
- Return `{ balance, account_number, name }`

**ProfileView** (GET `/api/account/profile/`):
- Return all user fields EXCEPT `password_hash`

---

## Step 6: Transactions App + DSA (`apps/transactions/`)

### DSA Structures (`apps/transactions/dsa_structures.py`)

This is the most important part for your DSA assignment. Implement these:

#### Stack (for transaction rollback/undo):
```python
class TransactionStack:
    """
    LIFO Stack to track recent transactions.
    Used for: showing last transaction, potential undo feature.
    DSA Concept: Stack (Last In First Out)
    """
    def __init__(self):
        self._data = []
    
    def push(self, transaction):
        self._data.append(transaction)
    
    def pop(self):
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self._data.pop()
    
    def peek(self):
        return self._data[-1] if not self.is_empty() else None
    
    def is_empty(self):
        return len(self._data) == 0
    
    def size(self):
        return len(self._data)
```

#### Queue (for processing pending transfers):
```python
class TransactionQueue:
    """
    FIFO Queue for processing transfers in order.
    DSA Concept: Queue (First In First Out)
    """
    def __init__(self):
        self._data = []
    
    def enqueue(self, transaction):
        self._data.append(transaction)
    
    def dequeue(self):
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self._data.pop(0)
    
    def is_empty(self):
        return len(self._data) == 0
    
    def size(self):
        return len(self._data)
```

#### Linked List (for traversing transaction history):
```python
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class TransactionLinkedList:
    """
    Singly Linked List for iterating transaction history.
    DSA Concept: Linked List
    """
    def __init__(self):
        self.head = None
    
    def append(self, transaction):
        new_node = Node(transaction)
        if not self.head:
            self.head = new_node
            return
        curr = self.head
        while curr.next:
            curr = curr.next
        curr.next = new_node
    
    def to_list(self):
        result = []
        curr = self.head
        while curr:
            result.append(curr.data)
            curr = curr.next
        return result
    
    def search(self, transaction_id):
        curr = self.head
        while curr:
            if curr.data.get('transaction_id') == transaction_id:
                return curr.data
            curr = curr.next
        return None
```

### Transfer View (POST `/api/transactions/transfer/`):

```python
# Logic step by step:
# 1. Get sender (request.user from auth)
# 2. Validate: amount > 0, recipient_account exists, not same account
# 3. Check sender balance >= amount
# 4. Use TransactionQueue to enqueue the transfer
# 5. Process: deduct from sender, add to recipient in users.csv
# 6. Generate transaction_id (UUID)
# 7. Append to sender's statement CSV (type: debit)
# 8. Append to recipient's statement CSV (type: credit)
# 9. Push to TransactionStack for tracking
# 10. Run fraud check (import from Sharjeel's ml_model.py)
# 11. Return success response
```

### History View (GET `/api/transactions/history/`):
- Read `data/statements/user_{id}.csv`
- Load into TransactionLinkedList
- Return `.to_list()` as JSON array

---

## Kaggle Datasets for Users CSV

Download this dataset and adapt it:
- **Bank Customer Data**: https://www.kaggle.com/datasets/shivamb/bank-customer-churn-modelling
  - Has: CustomerID, Surname, Balance, NumOfProducts, etc.
  - Adapt to add: Pakistani names, CNIC format, email addresses

Manually add a few rows to have realistic Pakistani names and data.

---

## Test Checklist

- [ ] Register creates user + statement CSV + hashed password
- [ ] Login returns token stored in tokens.csv
- [ ] Logout deletes token
- [ ] Balance endpoint returns correct balance
- [ ] Transfer deducts and adds balance correctly
- [ ] Transfer writes to both statement CSVs
- [ ] History reads from statement CSV and returns sorted list
- [ ] Stack push/pop/peek work correctly
- [ ] Queue enqueue/dequeue work correctly
- [ ] Linked list append/traverse/search work correctly