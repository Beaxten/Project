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
