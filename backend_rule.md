# Backend Rules — SmartBank System

## Core Rules

1. **No SQLite, no database ORM** — All data is stored in CSV files in the `data/` folder
2. **All CSV operations go through helper functions** — never read/write CSV directly in views
3. **All responses must be JSON** — use DRF `Response()` always
4. **Never return passwords or password hashes** in any response
5. **Every protected view must use `CSVTokenAuthentication`** — no exceptions
6. **Admin-only endpoints must check `user['role'] == 'admin'`** before processing

---

## CSV Helper Pattern (Must Follow)

Never write `pd.read_csv()` directly in views. Use helper functions:

```python
# apps/auth_app/csv_db.py

import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '../../data')

def get_all_users():
    path = os.path.join(DATA_DIR, 'users.csv')
    return pd.read_csv(path)

def get_user_by_email(email):
    df = get_all_users()
    result = df[df['email'] == email]
    if result.empty:
        return None
    return result.iloc[0].to_dict()

def get_user_by_id(user_id):
    df = get_all_users()
    result = df[df['user_id'] == int(user_id)]
    if result.empty:
        return None
    return result.iloc[0].to_dict()

def save_user(user_dict):
    df = get_all_users()
    new_row = pd.DataFrame([user_dict])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(os.path.join(DATA_DIR, 'users.csv'), index=False)

def update_user_balance(user_id, new_balance):
    df = get_all_users()
    df.loc[df['user_id'] == int(user_id), 'balance'] = new_balance
    df.to_csv(os.path.join(DATA_DIR, 'users.csv'), index=False)
```

---

## View Pattern (Copy This)

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class BalanceView(APIView):
    authentication_classes = [CSVTokenAuthentication]

    def get(self, request):
        user = request.user  # dict from CSV: { user_id, name, balance, ... }
        return Response({
            'balance': user['balance'],
            'account_number': user['account_number'],
            'name': user['name']
        })
```

---

## Password Hashing (Use This Exactly)

```python
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed
```

---

## Transaction Safety

When doing a transfer, always update BOTH users atomically (read all → update → write all):

```python
def process_transfer(sender_id, recipient_id, amount):
    df = get_all_users()
    sender_idx = df.index[df['user_id'] == sender_id][0]
    recipient_idx = df.index[df['user_id'] == recipient_id][0]
    
    if df.loc[sender_idx, 'balance'] < amount:
        return False, "Insufficient balance"
    
    df.loc[sender_idx, 'balance'] -= amount
    df.loc[recipient_idx, 'balance'] += amount
    df.to_csv('data/users.csv', index=False)
    return True, "Success"
```

---

## Token Generation

```python
import secrets

def generate_token():
    return secrets.token_hex(32)  # 64-character hex string
```

---

## Requirements.txt

```
django==4.2
djangorestframework==3.14
django-cors-headers==4.3
pandas==2.1
numpy==1.26
scikit-learn==1.3
joblib==1.3
```

---

## Common Mistakes to Avoid

| ❌ Wrong | ✅ Right |
|---------|---------|
| `pd.read_csv()` in views | Use helper functions from `csv_db.py` |
| Return Python dict directly | Use `Response({...})` |
| Store plain password | Always hash with `hash_password()` |
| No authentication on views | Always add `authentication_classes` |
| Catch all exceptions silently | Log errors and return proper error response |

---

## File Naming Convention

- Views: `views.py` inside each app
- URLs: `urls.py` inside each app
- DSA logic: `dsa_structures.py`
- ML logic: `ml_model.py`
- CSV helpers: `csv_db.py`