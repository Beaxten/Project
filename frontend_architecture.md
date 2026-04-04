# Frontend Architecture — SmartBank System

## Tech Stack

- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **State Management**: React Context API + useState/useReducer
- **Deployment**: Vercel

---

## Project Folder Structure

```
frontend/
├── public/
├── src/
│   ├── api/               ← All Axios API calls (one file per domain)
│   │   ├── auth.js
│   │   ├── accounts.js
│   │   ├── transactions.js
│   │   ├── loans.js
│   │   └── admin.js
│   ├── components/        ← Reusable UI components
│   │   ├── Navbar.jsx
│   │   ├── Sidebar.jsx
│   │   ├── ProtectedRoute.jsx
│   │   ├── TransactionTable.jsx
│   │   ├── LoanCard.jsx
│   │   └── AlertBanner.jsx
│   ├── context/
│   │   └── AuthContext.jsx  ← Global auth state (token, user role)
│   ├── pages/
│   │   ├── auth/
│   │   │   ├── Login.jsx
│   │   │   └── Register.jsx
│   │   ├── user/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Transfer.jsx
│   │   │   ├── Statement.jsx
│   │   │   ├── LoanApply.jsx
│   │   │   └── Profile.jsx
│   │   └── admin/
│   │       ├── AdminDashboard.jsx
│   │       ├── ManageUsers.jsx
│   │       ├── LoanApprovals.jsx
│   │       ├── FraudAlerts.jsx
│   │       └── AllTransactions.jsx
│   ├── utils/
│   │   └── formatters.js   ← date, currency formatting helpers
│   ├── App.jsx
│   └── main.jsx
├── index.html
├── vite.config.js
└── tailwind.config.js
```

---

## Routing Map

| Route                 | Page             | Access     |
| --------------------- | ---------------- | ---------- |
| `/`                   | Login            | Public     |
| `/register`           | Register         | Public     |
| `/dashboard`          | User Dashboard   | User only  |
| `/transfer`           | Transfer Money   | User only  |
| `/statement`          | Bank Statement   | User only  |
| `/loan`               | Apply for Loan   | User only  |
| `/profile`            | User Profile     | User only  |
| `/admin`              | Admin Dashboard  | Admin only |
| `/admin/users`        | Manage Users     | Admin only |
| `/admin/loans`        | Loan Approvals   | Admin only |
| `/admin/fraud`        | Fraud Alerts     | Admin only |
| `/admin/transactions` | All Transactions | Admin only |

---

## Backend API Endpoints (Frontend must call these)

| Method | URL                              | Purpose              |
| ------ | -------------------------------- | -------------------- |
| POST   | `/api/auth/login/`               | Login                |
| POST   | `/api/auth/register/`            | Register             |
| GET    | `/api/account/balance/`          | Get balance          |
| POST   | `/api/transactions/transfer/`    | Transfer money       |
| GET    | `/api/transactions/history/`     | Statement            |
| POST   | `/api/loans/apply/`              | Apply for loan       |
| GET    | `/api/loans/status/`             | Loan status          |
| GET    | `/api/admin/users/`              | All users (admin)    |
| PUT    | `/api/admin/loans/{id}/approve/` | Approve loan (admin) |
| GET    | `/api/admin/fraud-alerts/`       | Fraud alerts (admin) |

---

## Component Responsibilities

### Shared Components

- `Navbar` — top navigation, shows user name + logout
- `Sidebar` — left nav links (different for user vs admin)
- `ProtectedRoute` — redirects if not authenticated or wrong role
- `TransactionTable` — reusable table to display transaction history
- `AlertBanner` — shows success/error messages

### Pages (see individual member context files for details)

---

## Environment Variables

```
VITE_API_BASE_URL=http://localhost:8000
```

In production (Vercel), set this to your Django backend URL.

---

## Notes for All Frontend Members

- **Never hardcode API URLs** — always use `VITE_API_BASE_URL`
- **All API calls go in `/src/api/` files only** — not inside components
- **Use `try/catch` for all API calls** and show error with `AlertBanner`
- **Use Tailwind for all styling** — no inline styles
- **All pages must be responsive** (mobile + desktop)
- Commit your files individually — don't touch other members' pages
