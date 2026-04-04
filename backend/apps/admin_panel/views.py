import os
import glob
import pandas as pd

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from smartbank.authentication import CSVTokenAuthentication


DATA_DIR  = os.path.join(os.path.dirname(__file__), '../../data')
USERS_CSV = os.path.join(DATA_DIR, 'users.csv')
STMTS_DIR = os.path.join(DATA_DIR, 'statements')

def is_admin(request):
    return request.user.get('role') == 'admin'


class AdminUsersView(APIView):
    authentication_classes = [CSVTokenAuthentication]

    def get(self, request):

        if not is_admin(request):
            return Response(
                {'error': 'Access denied. Admins only.'},
                status=status.HTTP_403_FORBIDDEN
            )

        df = pd.read_csv(USERS_CSV)

        df = df.drop(columns=['password_hash'])

        users = df.to_dict(orient='records')

        return Response(users, status=status.HTTP_200_OK)


class AdminAllTransactionsView(APIView):
    authentication_classes = [CSVTokenAuthentication]

    def get(self, request):

 
        if not is_admin(request):
            return Response(
                {'error': 'Access denied. Admins only.'},
                status=status.HTTP_403_FORBIDDEN
            )

        pattern = os.path.join(STMTS_DIR, 'user_*.csv')
        all_files = glob.glob(pattern)

        if not all_files:
            return Response([], status=status.HTTP_200_OK)

        frames = []
        for filepath in all_files:
            try:
                df = pd.read_csv(filepath)
                if df.empty:
                    continue

                filename = os.path.basename(filepath)          # user_3.csv
                user_id  = filename.replace('user_', '').replace('.csv', '')
                df['user_id'] = user_id

                frames.append(df)

            except Exception:
                continue   

        if not frames:
            return Response([], status=status.HTTP_200_OK)

        combined = pd.concat(frames, ignore_index=True)

        users_df = pd.read_csv(USERS_CSV)[['user_id', 'name']]
        users_df['user_id'] = users_df['user_id'].astype(str)
        combined['user_id'] = combined['user_id'].astype(str)
        combined = combined.merge(users_df, on='user_id', how='left')

        combined = combined.sort_values('date', ascending=False)

        combined = combined.fillna('')

        return Response(combined.to_dict(orient='records'), status=status.HTTP_200_OK)



FRAUD_CSV = os.path.join(DATA_DIR, 'fraud_flags.csv')

class AdminFraudAlertsView(APIView):
    authentication_classes = [CSVTokenAuthentication]

    def get(self, request):

        if not is_admin(request):
            return Response(
                {'error': 'Access denied. Admins only.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            flags_df = pd.read_csv(FRAUD_CSV)
        except Exception:
            return Response([], status=status.HTTP_200_OK)

        if flags_df.empty:
            return Response([], status=status.HTTP_200_OK)

  
        flags_df['resolved'] = flags_df['resolved'].astype(str).str.strip().str.lower()
        unresolved = flags_df[flags_df['resolved'] == 'false']

        if unresolved.empty:
            return Response([], status=status.HTTP_200_OK)

        # ── 4. Join with users.csv to get user name ────────────────
        users_df = pd.read_csv(USERS_CSV)[['user_id', 'name', 'email']]
        users_df['user_id'] = users_df['user_id'].astype(str)
        unresolved = unresolved.copy()
        unresolved['user_id'] = unresolved['user_id'].astype(str)

        merged = unresolved.merge(users_df, on='user_id', how='left')

        merged = merged.fillna('')

        merged = merged.sort_values('flagged_at', ascending=False)

        return Response(merged.to_dict(orient='records'), status=status.HTTP_200_OK)