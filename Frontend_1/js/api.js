const API_BASE = 'http://127.0.0.1:8000';

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Token ${localStorage.getItem('token')}`
  };
}

async function apiLogin(email, password) {
  const res = await fetch(`${API_BASE}/api/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  return res.json();
}

async function apiRegister(name, email, password, cnic) {
  const res = await fetch(`${API_BASE}/api/auth/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password, cnic })
  });
  return res.json();
}

async function apiGetBalance() {
  const res = await fetch(`${API_BASE}/api/account/balance/`, { headers: authHeaders() });
  return res.json();
}

async function apiGetProfile() {
  const res = await fetch(`${API_BASE}/api/account/profile/`, { headers: authHeaders() });
  return res.json();
}

async function apiTransfer(recipient_account, amount, description) {
  const res = await fetch(`${API_BASE}/api/transactions/transfer/`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ recipient_account, amount, description })
  });
  return res.json();
}

async function apiGetHistory() {
  const res = await fetch(`${API_BASE}/api/transactions/history/`, { headers: authHeaders() });
  return res.json();
}

async function apiApplyLoan(data) {
  const res = await fetch(`${API_BASE}/api/loans/apply/`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(data)
  });
  return res.json();
}

async function apiGetLoanStatus() {
  const res = await fetch(`${API_BASE}/api/loans/status/`, { headers: authHeaders() });
  return res.json();
}

async function apiAdminGetUsers() {
  const res = await fetch(`${API_BASE}/api/admin/users/`, { headers: authHeaders() });
  return res.json();
}

async function apiAdminGetTransactions() {
  const res = await fetch(`${API_BASE}/api/admin/transactions/`, { headers: authHeaders() });
  return res.json();
}

async function apiAdminGetFraudAlerts() {
  const res = await fetch(`${API_BASE}/api/admin/fraud-alerts/`, { headers: authHeaders() });
  return res.json();
}

async function apiAdminLoanAction(loanId, action) {
  const res = await fetch(`${API_BASE}/api/admin/loans/${loanId}/approve/`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify({ action })
  });
  return res.json();
}
