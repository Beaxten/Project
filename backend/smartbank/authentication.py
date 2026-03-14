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