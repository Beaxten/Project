# Tamjeed — Frontend Member Context
## Assigned: App Setup + Dashboard + Transfer + Statement + Loan Apply

Read `front_Architecture.md` and `front_rule.md` first.

---

## Your Responsibility

You own these files:
- `src/App.jsx` — Routing setup for the whole app
- `src/pages/user/Dashboard.jsx` — User home after login
- `src/pages/user/Transfer.jsx` — Send money to another user
- `src/pages/user/Statement.jsx` ← NEW (was Hunain's)
- `src/pages/user/LoanApply.jsx` ← NEW (was Hunain's)
- `src/components/Sidebar.jsx` — Left nav for user panel
- `src/components/Navbar.jsx` — Top bar
- `src/api/accounts.js` — Account-related API calls
- `src/api/transactions.js` — Transaction API calls
- `src/api/loans.js` ← NEW — Loan API calls

---

## File 1: `src/App.jsx`

Set up ALL routes for the entire project here. Other members' pages are imported here.

```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';

// Auth
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';

// User pages
import Dashboard from './pages/user/Dashboard';
import Transfer from './pages/user/Transfer';
import Statement from './pages/user/Statement';
import LoanApply from './pages/user/LoanApply';
import Profile from './pages/user/Profile';

// Admin pages
import AdminDashboard from './pages/admin/AdminDashboard';
import ManageUsers from './pages/admin/ManageUsers';
import LoanApprovals from './pages/admin/LoanApprovals';
import FraudAlerts from './pages/admin/FraudAlerts';
import AllTransactions from './pages/admin/AllTransactions';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* User routes */}
        <Route path="/dashboard" element={<ProtectedRoute role="user"><Dashboard /></ProtectedRoute>} />
        <Route path="/transfer" element={<ProtectedRoute role="user"><Transfer /></ProtectedRoute>} />
        <Route path="/statement" element={<ProtectedRoute role="user"><Statement /></ProtectedRoute>} />
        <Route path="/loan" element={<ProtectedRoute role="user"><LoanApply /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute role="user"><Profile /></ProtectedRoute>} />

        {/* Admin routes */}
        <Route path="/admin" element={<ProtectedRoute role="admin"><AdminDashboard /></ProtectedRoute>} />
        <Route path="/admin/users" element={<ProtectedRoute role="admin"><ManageUsers /></ProtectedRoute>} />
        <Route path="/admin/loans" element={<ProtectedRoute role="admin"><LoanApprovals /></ProtectedRoute>} />
        <Route path="/admin/fraud" element={<ProtectedRoute role="admin"><FraudAlerts /></ProtectedRoute>} />
        <Route path="/admin/transactions" element={<ProtectedRoute role="admin"><AllTransactions /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  );
}
export default App;
```

---

## File 2: `src/api/accounts.js`

```js
import API from './axiosConfig';

export const getBalance = () => API.get('/account/balance/');
export const getUserProfile = () => API.get('/account/profile/');
```

## File 3: `src/api/transactions.js`

```js
import API from './axiosConfig';

export const transferMoney = (data) => API.post('/transactions/transfer/', data);
// data = { recipient_account: string, amount: number, description: string }

export const getTransactionHistory = () => API.get('/transactions/history/');
```

## File 3b (NEW): `src/api/loans.js`

```js
import API from './axiosConfig';

// Apply for a loan
export const applyLoan = (data) => API.post('/loans/apply/', data);
// data = { amount, purpose, duration_months, has_collateral, asset_description }

// Check if user already has a loan
export const getLoanStatus = () => API.get('/loans/status/');
```

---

## File 4: `src/components/Navbar.jsx`

Top bar shown on all user pages.

**Shows:**
- "SmartBank" logo/text on left
- User's name on right  
- Logout button

```jsx
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="bg-blue-700 text-white px-6 py-4 flex justify-between items-center shadow">
      <h1 className="text-xl font-bold">SmartBank</h1>
      <div className="flex items-center gap-4">
        <span className="text-sm">Hello, {user?.name}</span>
        <button onClick={handleLogout}
          className="bg-white text-blue-700 px-3 py-1 rounded font-semibold text-sm hover:bg-blue-100">
          Logout
        </button>
      </div>
    </nav>
  );
};
export default Navbar;
```

---

## File 5: `src/components/Sidebar.jsx`

Left navigation for user panel.

**Links:**
- Dashboard → `/dashboard`
- Transfer → `/transfer`
- Statement → `/statement`
- Apply for Loan → `/loan`
- Profile → `/profile`

Use `NavLink` from React Router so active link gets highlighted.

---

## File 6: `src/pages/user/Dashboard.jsx`

### UI Design:
- Full layout: Navbar on top, Sidebar on left, content on right
- Show account info card: Account Number, Balance (big number)
- Show last 5 transactions in a small table
- Show a "Quick Transfer" button that links to /transfer

### Data to fetch on load:
1. `getBalance()` → returns `{ balance, account_number, name }`
2. `getTransactionHistory()` → returns array, show only last 5

### Account Info Card:
```
Account Number: 1234-5678
Balance:  PKR 1,50,000
Account Holder: Ehtasham Ali
```

### Recent Transactions mini-table columns:
- Date | Description | Amount | Type (Credit/Debit)

### Color coding:
- Credit (money in) → green text
- Debit (money out) → red text

---

## File 7: `src/pages/user/Transfer.jsx`

### UI Design:
- Form card in center
- Field: Recipient Account Number (text input)
- Field: Amount (number input, PKR)
- Field: Description/Note (optional, text)
- "Transfer" button
- Show confirmation step before sending

### Logic (step by step):
1. User fills form and clicks Transfer
2. Show confirmation: "Send PKR 5,000 to account 1234-5678?"
3. User confirms → call `transferMoney({ recipient_account, amount, description })`
4. On success → show "Transfer successful!" and clear form
5. On error → show error message (e.g., "Insufficient balance" or "Account not found")

### Validations:
- Amount must be greater than 0
- Amount cannot exceed current balance (fetch balance first on page load)
- Recipient account cannot be own account number
- Account number format: exactly 11 digits

### After successful transfer:
- Show success banner
- Show option to "View Statement" or "Transfer Again"

---

## Layout Pattern (Use for Dashboard and Transfer)

```jsx
import Navbar from '../../components/Navbar';
import Sidebar from '../../components/Sidebar';

const Dashboard = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          {/* Your page content here */}
        </main>
      </div>
    </div>
  );
};
```

---

## File 8 (NEW): `src/pages/user/Statement.jsx`

### What This Page Does:
Shows the user's full transaction history as a bank statement.

### Data to Fetch:
Call `getTransactionHistory()` from `../../api/transactions` (you already built this).

Returns an array like:
```json
[
  { "id": 1, "date": "2025-03-01", "description": "Transfer to Ali", "amount": 5000, "type": "debit", "balance_after": 145000 },
  { "id": 2, "date": "2025-03-05", "description": "Salary Credit", "amount": 100000, "type": "credit", "balance_after": 245000 }
]
```

### UI Design:
- Page title: "Bank Statement"
- 3 filter buttons: **All** | **Credit** | **Debit** — clicking filters the table
- Table columns: Date | Description | Type | Amount | Balance After
- Credit rows → amount in green text
- Debit rows → amount in red text
- Active filter button highlighted in blue

### Filter Logic:
```jsx
const [filter, setFilter] = useState('all');
const filtered = transactions.filter(t =>
  filter === 'all' ? true : t.type === filter
);
```

### Full Component:
```jsx
import { useState, useEffect } from 'react';
import { getTransactionHistory } from '../../api/transactions';
import Navbar from '../../components/Navbar';
import Sidebar from '../../components/Sidebar';

const Statement = () => {
  const [transactions, setTransactions] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getTransactionHistory()
      .then(res => setTransactions(res.data))
      .catch(() => setError('Failed to load transactions.'))
      .finally(() => setLoading(false));
  }, []);

  const filtered = transactions.filter(t =>
    filter === 'all' ? true : t.type === filter
  );

  const btnClass = (f) =>
    `px-4 py-2 rounded font-semibold text-sm ${filter === f ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-bold text-gray-800">Bank Statement</h1>
            <div className="flex gap-2">
              <button className={btnClass('all')} onClick={() => setFilter('all')}>All</button>
              <button className={btnClass('credit')} onClick={() => setFilter('credit')}>Credit</button>
              <button className={btnClass('debit')} onClick={() => setFilter('debit')}>Debit</button>
            </div>
          </div>

          {loading && <p className="text-center text-gray-500 py-10">Loading...</p>}
          {error && <p className="text-red-500">{error}</p>}

          {!loading && (
            <div className="bg-white rounded-xl shadow overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    {['Date', 'Description', 'Type', 'Amount', 'Balance After'].map(h => (
                      <th key={h} className="px-4 py-3 text-left text-gray-600 font-semibold">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filtered.length === 0 ? (
                    <tr><td colSpan={5} className="text-center py-8 text-gray-400">No transactions found</td></tr>
                  ) : filtered.map(t => (
                    <tr key={t.id} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-3 text-gray-600">{t.date}</td>
                      <td className="px-4 py-3 text-gray-800">{t.description}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded text-xs font-bold ${t.type === 'credit' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                          {t.type.toUpperCase()}
                        </span>
                      </td>
                      <td className={`px-4 py-3 font-semibold ${t.type === 'credit' ? 'text-green-600' : 'text-red-500'}`}>
                        {t.type === 'credit' ? '+' : '-'} PKR {Number(t.amount).toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-gray-600">PKR {Number(t.balance_after).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default Statement;
```

---

## File 9 (NEW): `src/pages/user/LoanApply.jsx`

### What This Page Does:
Lets the user apply for a loan. The backend ML model decides approval.

### On Page Load:
First call `getLoanStatus()`. If user already has an active loan, show their existing loan and hide the form.

### Form Fields:
- Loan Amount (number, PKR)
- Purpose (dropdown: Home, Education, Business, Personal, Medical)
- Duration (dropdown: 6 months, 12 months, 24 months, 36 months)
- Collateral? (Yes / No radio buttons)
- If Yes → Asset Description text input appears

### Result Display:
- Approved → green banner
- Rejected → red banner
- Pending → yellow banner

### Full Component:
```jsx
import { useState, useEffect } from 'react';
import { applyLoan, getLoanStatus } from '../../api/loans';
import Navbar from '../../components/Navbar';
import Sidebar from '../../components/Sidebar';

const LoanApply = () => {
  const [existingLoan, setExistingLoan] = useState(null);
  const [form, setForm] = useState({ amount: '', purpose: 'home', duration_months: '12', has_collateral: false, asset_description: '' });
  const [result, setResult] = useState(null); // { status, message }
  const [loading, setLoading] = useState(false);
  const [checkingLoan, setCheckingLoan] = useState(true);

  useEffect(() => {
    getLoanStatus()
      .then(res => { if (res.data?.loan) setExistingLoan(res.data.loan); })
      .catch(() => {})
      .finally(() => setCheckingLoan(false));
  }, []);

  const handleChange = (e) => {
    const value = e.target.type === 'radio' ? e.target.value === 'true' : e.target.value;
    setForm({ ...form, [e.target.name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const res = await applyLoan(form);
      setResult(res.data);
    } catch (err) {
      setResult({ status: 'error', message: err.response?.data?.error || 'Something went wrong.' });
    } finally {
      setLoading(false);
    }
  };

  const resultColors = {
    approved: 'bg-green-100 border border-green-400 text-green-800',
    rejected: 'bg-red-100 border border-red-400 text-red-800',
    pending: 'bg-yellow-100 border border-yellow-400 text-yellow-800',
    error: 'bg-red-100 border border-red-400 text-red-800',
  };

  if (checkingLoan) return <div className="min-h-screen bg-gray-50"><Navbar /><div className="flex"><Sidebar /><main className="flex-1 p-6"><p>Loading...</p></main></div></div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          <h1 className="text-2xl font-bold text-gray-800 mb-6">Loan Application</h1>

          {existingLoan ? (
            <div className="max-w-lg bg-white rounded-2xl shadow p-6">
              <h2 className="text-lg font-semibold mb-4">Your Active Loan</h2>
              <div className="space-y-2 text-sm">
                <p><span className="text-gray-500">Amount:</span> <strong>PKR {Number(existingLoan.amount).toLocaleString()}</strong></p>
                <p><span className="text-gray-500">Purpose:</span> <strong className="capitalize">{existingLoan.purpose}</strong></p>
                <p><span className="text-gray-500">Duration:</span> <strong>{existingLoan.duration_months} months</strong></p>
                <p><span className="text-gray-500">Status:</span>
                  <span className={`ml-2 px-2 py-1 rounded text-xs font-bold ${existingLoan.status === 'approved' ? 'bg-green-100 text-green-700' : existingLoan.status === 'pending' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}`}>
                    {existingLoan.status.toUpperCase()}
                  </span>
                </p>
              </div>
            </div>
          ) : (
            <div className="max-w-lg bg-white rounded-2xl shadow p-6">
              {result && (
                <div className={`p-4 rounded-lg mb-6 ${resultColors[result.status]}`}>
                  <p className="font-semibold capitalize">{result.status}</p>
                  <p className="text-sm mt-1">{result.message}</p>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-gray-600 text-sm mb-1">Loan Amount (PKR)</label>
                  <input type="number" name="amount" value={form.amount} onChange={handleChange} min="1000" required
                    className="border rounded-lg px-3 py-2 w-full focus:outline-none focus:border-blue-500" placeholder="e.g. 500000" />
                </div>

                <div>
                  <label className="block text-gray-600 text-sm mb-1">Purpose</label>
                  <select name="purpose" value={form.purpose} onChange={handleChange}
                    className="border rounded-lg px-3 py-2 w-full focus:outline-none focus:border-blue-500">
                    {['home', 'education', 'business', 'personal', 'medical'].map(p => (
                      <option key={p} value={p} className="capitalize">{p.charAt(0).toUpperCase() + p.slice(1)}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-gray-600 text-sm mb-1">Duration</label>
                  <select name="duration_months" value={form.duration_months} onChange={handleChange}
                    className="border rounded-lg px-3 py-2 w-full focus:outline-none focus:border-blue-500">
                    {['6', '12', '24', '36'].map(d => <option key={d} value={d}>{d} months</option>)}
                  </select>
                </div>

                <div>
                  <label className="block text-gray-600 text-sm mb-2">Do you have collateral (asset)?</label>
                  <div className="flex gap-6">
                    <label className="flex items-center gap-2">
                      <input type="radio" name="has_collateral" value="true" onChange={handleChange} /> Yes
                    </label>
                    <label className="flex items-center gap-2">
                      <input type="radio" name="has_collateral" value="false" defaultChecked onChange={handleChange} /> No
                    </label>
                  </div>
                </div>

                {form.has_collateral === true && (
                  <div>
                    <label className="block text-gray-600 text-sm mb-1">Asset Description</label>
                    <input type="text" name="asset_description" value={form.asset_description} onChange={handleChange}
                      className="border rounded-lg px-3 py-2 w-full focus:outline-none focus:border-blue-500"
                      placeholder="e.g. House in Lahore" />
                  </div>
                )}

                <button type="submit" disabled={loading}
                  className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50">
                  {loading ? 'Processing...' : 'Apply for Loan'}
                </button>
              </form>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default LoanApply;
```

---

## Test Checklist

- [ ] Dashboard loads and shows real balance from API
- [ ] Last 5 transactions show correctly on dashboard
- [ ] Transfer form validates amount > 0
- [ ] Transfer shows confirmation before sending
- [ ] On transfer success, shows success message
- [ ] Statement page loads all transactions
- [ ] Filter buttons (All/Credit/Debit) work correctly
- [ ] Credit shows green, debit shows red
- [ ] Loan form submits and shows result banner
- [ ] If user already has a loan, form is hidden and existing loan info shows
- [ ] Routing in App.jsx works for all pages