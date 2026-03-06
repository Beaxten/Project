# Ehtasham — Frontend Member Context
## Assigned: Authentication Pages (Login & Register) + Profile Page

Read `front_Architecture.md` and `front_rule.md` first before building anything.


---

## Your Responsibility

You own these files:
- `src/pages/auth/Login.jsx`
- `src/pages/auth/Register.jsx`
- `src/context/AuthContext.jsx`
- `src/api/auth.js`
- `src/components/ProtectedRoute.jsx`
- `src/pages/user/Profile.jsx` 

---

## File 1: `src/api/auth.js`

This file contains all API calls for authentication. Build this first.

```js
import API from './axiosConfig';

// Login — sends email + password, gets back token + role
export const loginUser = (credentials) => API.post('/auth/login/', credentials);

// Register — sends name, email, password, CNIC
export const registerUser = (userData) => API.post('/auth/register/', userData);

// Logout — invalidates token on server
export const logoutUser = () => API.post('/auth/logout/');
```

---

## File 2: `src/context/AuthContext.jsx`

This is the GLOBAL auth state. Every page in the app uses this. Build carefully.

**What it must do:**
- Store `user` object: `{ id, name, email, role }` 
- Store `token` string
- Provide `login(token, user)` function that saves to localStorage
- Provide `logout()` function that clears localStorage and redirects to `/`
- On app load, read token from localStorage and restore session

```jsx
import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token') || null);

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) setUser(JSON.parse(savedUser));
  }, []);

  const login = (tokenValue, userData) => {
    localStorage.setItem('token', tokenValue);
    localStorage.setItem('user', JSON.stringify(userData));
    setToken(tokenValue);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
```

---

## File 3: `src/components/ProtectedRoute.jsx`

Blocks pages from unauthenticated users OR wrong role.

```jsx
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// Usage: <ProtectedRoute role="user"> OR <ProtectedRoute role="admin">
const ProtectedRoute = ({ children, role }) => {
  const { user, token } = useAuth();

  if (!token || !user) return <Navigate to="/" replace />;
  if (role && user.role !== role) return <Navigate to="/" replace />;
  return children;
};

export default ProtectedRoute;
```

---

## File 4: `src/pages/auth/Login.jsx`

### UI Design:
- Centered card on a blue/white gradient background
- Bank logo/name "SmartBank" at top
- Email input field
- Password input field  
- "Login" button (blue, full width)
- Link: "Don't have an account? Register"
- Show error message if login fails

### Logic:
1. User types email + password
2. On submit → call `loginUser({ email, password })`
3. Backend responds with `{ token, user: { id, name, email, role } }`
4. Call `login(token, user)` from AuthContext
5. If `user.role === 'admin'` → navigate to `/admin`
6. If `user.role === 'user'` → navigate to `/dashboard`
7. On error → show "Invalid email or password"

```jsx
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { loginUser } from '../../api/auth';
import { useAuth } from '../../context/AuthContext';

const Login = () => {
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await loginUser(form);
      login(res.data.token, res.data.user);
      navigate(res.data.user.role === 'admin' ? '/admin' : '/dashboard');
    } catch {
      setError('Invalid email or password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-900 flex items-center justify-center">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
        <h1 className="text-3xl font-bold text-blue-700 text-center mb-2">SmartBank</h1>
        <p className="text-gray-500 text-center mb-6">Welcome back! Please login.</p>
        {error && <div className="bg-red-100 text-red-600 p-3 rounded mb-4">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email" name="email" placeholder="Email"
            value={form.email} onChange={handleChange}
            className="border border-gray-300 rounded-lg px-4 py-3 w-full focus:outline-none focus:border-blue-500"
            required
          />
          <input
            type="password" name="password" placeholder="Password"
            value={form.password} onChange={handleChange}
            className="border border-gray-300 rounded-lg px-4 py-3 w-full focus:outline-none focus:border-blue-500"
            required
          />
          <button type="submit" disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50">
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        <p className="text-center mt-4 text-gray-600">
          No account? <Link to="/register" className="text-blue-600 font-semibold">Register</Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
```

---

## File 5: `src/pages/auth/Register.jsx`

### UI Design:
- Same card design as Login
- Fields: Full Name, Email, Password, Confirm Password, CNIC (13 digits)
- "Register" button
- Link back to Login

### Logic:
1. Validate: password === confirmPassword, CNIC is 13 digits
2. Call `registerUser({ name, email, password, cnic })`
3. On success → navigate to `/` (login page) with success message
4. On error → show server error message

### Validation Rules:
- Password minimum 6 characters
- CNIC: exactly 13 numeric characters
- All fields required

---

## How to Connect to App.jsx

Tell Tamjeed (who sets up App.jsx routing) that your routes are:
- `/` → Login page (public)
- `/register` → Register page (public)

And wrap the whole app in `<AuthProvider>` in `main.jsx`:

```jsx
// main.jsx
import { AuthProvider } from './context/AuthContext';
ReactDOM.createRoot(document.getElementById('root')).render(
  <AuthProvider>
    <App />
  </AuthProvider>
);
```

---

---

## File 6 (NEW): `src/pages/user/Profile.jsx`

### What This Page Does:
Shows the logged-in user's profile information. Read-only — no editing needed.

### Layout:
```jsx
import Navbar from '../../components/Navbar';
import Sidebar from '../../components/Sidebar';
// wrap your content inside Navbar + Sidebar layout (same as Dashboard)
```

### Data to Fetch:
Call `getUserProfile()` from `../../api/accounts` — already created by Tamjeed.

Returns:
```json
{
  "name": "Ali Hassan",
  "email": "ali@gmail.com",
  "cnic": "3520212345678",
  "account_number": "12345678901",
  "account_type": "savings",
  "created_at": "2024-01-15",
  "balance": 150000
}
```

### Avatar with initials:
```jsx
const initials = profileData?.name?.split(' ').map(n => n[0]).join('').toUpperCase();
// "Ali Hassan" → "AH"
```

### Full Component:
```jsx
import { useState, useEffect } from 'react';
import { getUserProfile } from '../../api/accounts';
import Navbar from '../../components/Navbar';
import Sidebar from '../../components/Sidebar';

const Profile = () => {
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getUserProfile()
      .then(res => setProfileData(res.data))
      .catch(() => setError('Failed to load profile.'))
      .finally(() => setLoading(false));
  }, []);

  const initials = profileData?.name?.split(' ').map(n => n[0]).join('').toUpperCase();

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          <h1 className="text-2xl font-bold text-gray-800 mb-6">My Profile</h1>
          {loading && <p className="text-center text-gray-500">Loading...</p>}
          {error && <p className="text-red-500">{error}</p>}
          {profileData && (
            <div className="max-w-lg mx-auto bg-white rounded-2xl shadow p-8">
              <div className="text-center mb-6">
                <div className="w-20 h-20 bg-blue-600 rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-3">
                  {initials}
                </div>
                <p className="text-xl font-bold text-gray-800">{profileData.name}</p>
                <span className="bg-blue-100 text-blue-700 text-sm px-3 py-1 rounded-full capitalize">
                  {profileData.account_type} Account
                </span>
              </div>
              <div>
                {[
                  { label: 'Email', value: profileData.email },
                  { label: 'CNIC', value: profileData.cnic },
                  { label: 'Account Number', value: profileData.account_number },
                  { label: 'Account Type', value: profileData.account_type },
                  { label: 'Member Since', value: profileData.created_at },
                  { label: 'Balance', value: `PKR ${Number(profileData.balance).toLocaleString()}` },
                ].map(item => (
                  <div key={item.label} className="flex justify-between py-3 border-b border-gray-100">
                    <span className="text-gray-500">{item.label}</span>
                    <span className="text-gray-800 font-semibold">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default Profile;
```

---

## Test Checklist Before Submitting

- [ ] Login with correct credentials → goes to dashboard
- [ ] Login with wrong credentials → shows error
- [ ] Admin login → goes to /admin
- [ ] Register with mismatched passwords → shows validation error
- [ ] After login, refresh page → still logged in (token in localStorage)
- [ ] Logout (from any page) → redirected to /
- [ ] Profile page loads and shows correct user info
- [ ] Avatar initials are correct (e.g. "AH" for Ali Hassan)
- [ ] Balance formatted correctly as PKR 1,50,000