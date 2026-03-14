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