import os
import uuid
import datetime
import pandas as pd

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from smartbank.authentication import CSVTokenAuthentication
from .dsa_structures import TransactionStack, TransactionQueue, TransactionLinkedList

# ── paths ──────────────────────────────────────────────────────────────
DATA_DIR   = os.path.join(os.path.dirname(__file__), '../../data')
USERS_CSV  = os.path.join(DATA_DIR, 'users.csv')
STMTS_DIR  = os.path.join(DATA_DIR, 'statements')

# ── module-level DSA objects (live for the lifetime of the server) ─────
transfer_stack = TransactionStack()   # tracks last processed transfer
transfer_queue = TransactionQueue()   # queues incoming transfers


# ══════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

def get_user_by_account(account_number):
    """Return user dict from users.csv by account number, or None."""
    df = pd.read_csv(USERS_CSV)
    row = df[df['account_number'].astype(str) == str(account_number)]
    return row.iloc[0].to_dict() if not row.empty else None


def update_balance(user_id, new_balance):
    """Overwrite balance for a single user in users.csv."""
    df = pd.read_csv(USERS_CSV)
    df.loc[df['user_id'] == int(user_id), 'balance'] = round(new_balance, 2)
    df.to_csv(USERS_CSV, index=False)


def append_statement(user_id, transaction_id, description,
                     amount, txn_type, balance_after,
                     recipient_account='', sender_account=''):
    """Add one row to data/statements/user_{id}.csv."""
    stmt_path = os.path.join(STMTS_DIR, f'user_{user_id}.csv')

    new_row = {
        'transaction_id':   transaction_id,
        'date':             datetime.datetime.now().strftime('%Y-%m-%d'),
        'description':      description,
        'amount':           round(float(amount), 2),
        'type':             txn_type,
        'balance_after':    round(float(balance_after), 2),
        'recipient_account': recipient_account,
        'sender_account':   sender_account,
    }

    if os.path.exists(stmt_path):
        df = pd.read_csv(stmt_path)
    else:
        df = pd.DataFrame(columns=new_row.keys())

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(stmt_path, index=False)


def run_fraud_check(user_id, transaction_id, amount):
    try:
        from apps.loans.fraud_detector import detect_fraud, flag_transaction

        hour = datetime.datetime.now().hour
        is_fraud, reason = detect_fraud(user_id, float(amount), hour)

        # ── Temporary: also flag if amount > 100,000 PKR for testing ──
        if not is_fraud and float(amount) > 100000:
            is_fraud = True
            reason   = f'Large transfer PKR {float(amount):,.0f} flagged for review'

        if is_fraud:
            severity = 'high' if float(amount) > 300000 else 'medium'
            flag_transaction(user_id, transaction_id, reason, severity)
            print(f"FRAUD FLAGGED → {transaction_id} | {reason}")  # ← shows in terminal

    except Exception as e:
        print(f"Fraud check error: {e}")   # ← shows exact error in terminal

# ══════════════════════════════════════════════════════════════════════
#  POST /api/transactions/transfer/
# ══════════════════════════════════════════════════════════════════════

class TransferView(APIView):
    authentication_classes = [CSVTokenAuthentication]

    def post(self, request):
        sender = request.user  # dict from CSVTokenAuthentication

        # ── 1. Read input ──────────────────────────────────────────
        recipient_account = str(request.data.get('recipient_account', '')).strip()
        description       = request.data.get('description', 'Transfer').strip() or 'Transfer'

        try:
            amount = float(request.data.get('amount', 0))
        except (ValueError, TypeError):
            return Response(
                {'error': 'Amount must be a number.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ── 2. Validate ────────────────────────────────────────────
        if amount <= 0:
            return Response(
                {'error': 'Amount must be greater than 0.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not recipient_account:
            return Response(
                {'error': 'Recipient account number is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if str(sender['account_number']) == recipient_account:
            return Response(
                {'error': 'You cannot transfer money to your own account.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        recipient = get_user_by_account(recipient_account)
        if not recipient:
            return Response(
                {'error': 'Recipient account not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # ── 3. Check balance ───────────────────────────────────────
        sender_balance = float(sender['balance'])
        if sender_balance < amount:
            return Response(
                {'error': f'Insufficient balance. Your balance is PKR {sender_balance:,.2f}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ── 4. Enqueue the transfer ────────────────────────────────
        transfer_data = {
            'sender_id':          sender['user_id'],
            'sender_account':     sender['account_number'],
            'recipient_id':       recipient['user_id'],
            'recipient_account':  recipient_account,
            'amount':             amount,
            'description':        description,
        }
        transfer_queue.enqueue(transfer_data)

        # ── 5. Dequeue and process ─────────────────────────────────
        job = transfer_queue.dequeue()

        sender_new_balance    = sender_balance - job['amount']
        recipient_new_balance = float(recipient['balance']) + job['amount']

        update_balance(job['sender_id'],    sender_new_balance)
        update_balance(job['recipient_id'], recipient_new_balance)

        # ── 6. Generate transaction ID ─────────────────────────────
        txn_id = 'TXN-' + str(uuid.uuid4()).upper()[:8]

        # ── 7. Write debit to sender's statement ───────────────────
        append_statement(
            user_id            = job['sender_id'],
            transaction_id     = txn_id,
            description        = f"Transfer to {recipient['name']}",
            amount             = job['amount'],
            txn_type           = 'debit',
            balance_after      = sender_new_balance,
            recipient_account  = job['recipient_account'],
            sender_account     = job['sender_account'],
        )

        # ── 8. Write credit to recipient's statement ───────────────
        append_statement(
            user_id            = job['recipient_id'],
            transaction_id     = txn_id,
            description        = f"Transfer from {sender['name']}",
            amount             = job['amount'],
            txn_type           = 'credit',
            balance_after      = recipient_new_balance,
            recipient_account  = job['recipient_account'],
            sender_account     = job['sender_account'],
        )

        # ── 9. Push to stack ───────────────────────────────────────
        transfer_stack.push({
            'transaction_id': txn_id,
            'amount':         job['amount'],
            'recipient':      recipient['name'],
            'time':           datetime.datetime.now().isoformat(),
        })

        # ── 10. Fraud check ────────────────────────────────────────
        run_fraud_check(job['sender_id'], txn_id, job['amount'])

        # ── 11. Return success ─────────────────────────────────────
        return Response({
            'message':        'Transfer successful.',
            'transaction_id': txn_id,
            'amount':         job['amount'],
            'recipient_name': recipient['name'],
            'new_balance':    sender_new_balance,
        }, status=status.HTTP_200_OK)


# ══════════════════════════════════════════════════════════════════════
#  GET /api/transactions/history/
# ══════════════════════════════════════════════════════════════════════

class HistoryView(APIView):
    authentication_classes = [CSVTokenAuthentication]

    def get(self, request):
        user_id   = request.user['user_id']
        stmt_path = os.path.join(STMTS_DIR, f'user_{user_id}.csv')

        # If file doesn't exist yet return empty list
        if not os.path.exists(stmt_path):
            return Response([], status=status.HTTP_200_OK)

        df = pd.read_csv(stmt_path)

        if df.empty:
            return Response([], status=status.HTTP_200_OK)

        # ── Load into Linked List (DSA) ────────────────────────────
        history = TransactionLinkedList()
        # Sort newest first before loading
        df = df.sort_values('date', ascending=False)

        for _, row in df.iterrows():
            history.append(row.to_dict())

        return Response(history.to_list(), status=status.HTTP_200_OK)