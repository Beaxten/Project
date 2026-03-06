# Admin Panel Pages — Frontend Context
## These pages are built by Tamjeed (AdminDashboard) and Ehtasham (supporting)

Read `front_Architecture.md` and `front_rule.md` first.

---

## Admin Layout

All admin pages use the same layout but with an Admin Sidebar (different links from user sidebar).

### Admin Sidebar links:
- Dashboard → `/admin`
- Manage Users → `/admin/users`
- Loan Approvals → `/admin/loans`
- Fraud Alerts → `/admin/fraud`
- All Transactions → `/admin/transactions`

---

## File 1: `src/api/admin.js`

```js
import API from './axiosConfig';

export const getAllUsers = () => API.get('/admin/users/');
export const getAllLoans = () => API.get('/admin/loans/');
export const approveLoan = (loanId, action) =>
  API.put(`/admin/loans/${loanId}/approve/`, { action }); // action: 'approved' or 'rejected'
export const getFraudAlerts = () => API.get('/admin/fraud-alerts/');
export const getAllTransactions = () => API.get('/admin/transactions/');
```

---

## File 2: `src/pages/admin/AdminDashboard.jsx`

### UI Design:
- 4 stat cards at top:
  - Total Users (number)
  - Total Transactions Today (number)
  - Pending Loans (number)
  - Active Fraud Flags (number)
- Quick links to each admin section

### Data to fetch:
All 4 stats come from combining API calls:
- `getAllUsers()` → count
- `getAllLoans()` → filter status === 'pending' → count
- `getFraudAlerts()` → count unresolved
- `getAllTransactions()` → filter today's date → count

```jsx
// Stat card component
const StatCard = ({ title, value, color }) => (
  <div className={`bg-white rounded-lg shadow p-6 border-l-4 ${color}`}>
    <p className="text-gray-500 text-sm">{title}</p>
    <p className="text-3xl font-bold text-gray-800">{value}</p>
  </div>
);

// Colors: border-blue-500, border-green-500, border-yellow-500, border-red-500
```

---

## File 3: `src/pages/admin/ManageUsers.jsx`

### UI Design:
- Table with all users
- Columns: ID | Name | Email | Account Number | Balance | Role | Status
- Search bar to filter by name or email

### Data:
Fetch from `getAllUsers()`. Returns array of user objects.

### Features:
- Search: filter users by name as user types in search box
- Show balance in PKR format: `PKR ${balance.toLocaleString()}`
- Show role badge: user = blue, admin = red

```jsx
const [search, setSearch] = useState('');
const filtered = users.filter(u =>
  u.name.toLowerCase().includes(search.toLowerCase()) ||
  u.email.toLowerCase().includes(search.toLowerCase())
);
```

---

## File 4: `src/pages/admin/LoanApprovals.jsx`

### UI Design:
- Show only PENDING loans
- Each loan in a card showing:
  - User name
  - Loan amount
  - Purpose
  - Duration
  - Has collateral: Yes/No
  - ML Score (probability)
  - Applied date
- Two buttons: "Approve" (green) | "Reject" (red)

### Logic:
1. Fetch all loans from `getAllLoans()`
2. Filter where `status === 'pending'`
3. When Approve clicked → call `approveLoan(loanId, 'approved')`
4. When Reject clicked → call `approveLoan(loanId, 'rejected')`
5. On success → remove that loan from the list (update state)

```jsx
const handleAction = async (loanId, action) => {
  try {
    await approveLoan(loanId, action);
    setLoans(loans.filter(l => l.loan_id !== loanId));
    alert(`Loan ${action} successfully`);
  } catch {
    alert('Failed to update loan status');
  }
};
```

---

## File 5: `src/pages/admin/FraudAlerts.jsx`

### UI Design:
- Red-themed page header "⚠️ Fraud Alerts"
- Table or card list of flagged transactions
- Columns: Flag ID | User | Transaction ID | Reason | Time | Severity | Status
- Severity badge: high = red, medium = yellow, low = gray
- "Mark Resolved" button for each flag

### Data from `getFraudAlerts()`:
```json
[
  {
    "flag_id": 1,
    "user_name": "Ali Hassan",
    "transaction_id": "TXN099",
    "reason": "Large unusual transfer",
    "flagged_at": "2025-03-01 02:15:00",
    "resolved": false,
    "severity": "high"
  }
]
```

---

## File 6: `src/pages/admin/AllTransactions.jsx`

### UI Design:
- Full transaction history across all users
- Table: Date | User | Description | Amount | Type | Account
- Filter by: All / Credit / Debit / Today

### Data:
Fetch from `getAllTransactions()` — returns combined array from all user statements.

---

## Shared Admin Layout (use in every admin page)

```jsx
import Navbar from '../../components/Navbar';

const AdminLayout = ({ children }) => (
  <div className="min-h-screen bg-gray-100">
    <Navbar />
    <div className="flex">
      {/* Admin Sidebar */}
      <aside className="w-64 bg-gray-900 text-white min-h-screen p-4">
        <nav className="space-y-2 mt-4">
          {[
            { label: 'Dashboard', path: '/admin' },
            { label: 'Users', path: '/admin/users' },
            { label: 'Loans', path: '/admin/loans' },
            { label: 'Fraud Alerts', path: '/admin/fraud' },
            { label: 'Transactions', path: '/admin/transactions' },
          ].map(item => (
            <Link key={item.path} to={item.path}
              className="block px-4 py-2 rounded hover:bg-gray-700">
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="flex-1 p-6">{children}</main>
    </div>
  </div>
);
```