# Frontend Rules — SmartBank System

## Golden Rules (Follow Always)

1. **One page = one file** — Each member owns their assigned pages only
2. **No direct fetch()** — Always use files from `/src/api/` folder
3. **No inline CSS** — Use only Tailwind CSS classes
4. **Always handle loading and error states** in every page
5. **Never store passwords or sensitive data in state** — only token and role
6. **Use `React Router <Link>`** for navigation — never `window.location`
7. **Name components in PascalCase** — `UserDashboard.jsx` not `userDashboard.jsx`
8. **Name files exactly as defined** in your context file — spelling matters

---

## Folder Rules

```
✅ Your pages go in: src/pages/user/ OR src/pages/admin/
✅ Shared components go in: src/components/
✅ API calls go in: src/api/
❌ Never create new folders without team agreement
❌ Never edit another member's files
```

---

## API Call Pattern (Copy This Every Time)

```jsx
import { useState, useEffect } from 'react';
import { getBalance } from '../../api/accounts';

const MyPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await getBalance();
        setData(res.data);
      } catch (err) {
        setError('Failed to load data. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className="text-center p-8">Loading...</div>;
  if (error) return <div className="text-red-500 p-4">{error}</div>;

  return <div>{/* your UI */}</div>;
};

export default MyPage;
```

---

## Form Handling Pattern

```jsx
const [form, setForm] = useState({ amount: '', recipient: '' });

const handleChange = (e) => {
  setForm({ ...form, [e.target.name]: e.target.value });
};

const handleSubmit = async (e) => {
  e.preventDefault();
  try {
    await transferMoney(form);
    alert('Success!');
  } catch (err) {
    setError(err.response?.data?.message || 'Error occurred');
  }
};
```

---

## Tailwind Quick Reference

```
Layout:    flex, grid, items-center, justify-between, gap-4
Spacing:   p-4, px-6, py-2, m-4, mt-2, mb-6
Text:      text-xl, font-bold, text-gray-600, text-blue-500
Colors:    bg-white, bg-blue-600, bg-gray-100, border-gray-300
Cards:     bg-white rounded-lg shadow p-6
Buttons:   px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700
Inputs:    border rounded px-3 py-2 w-full focus:outline-none
```

---

## Protected Route Usage

```jsx
// In App.jsx - already set up, just use it
<Route path="/dashboard" element={
  <ProtectedRoute role="user">
    <Dashboard />
  </ProtectedRoute>
} />
```

---

## Common Mistakes to Avoid

| ❌ Wrong | ✅ Right |
|---------|---------|
| `fetch('/api/balance')` | `import { getBalance } from '../../api/accounts'` |
| `<a href="/dashboard">` | `<Link to="/dashboard">` |
| `style={{ color: 'red' }}` | `className="text-red-500"` |
| Hardcoding user ID | `useAuth().user.id` |
| No loading state | Always add `loading` state |

---

## How to Run Locally

```bash
cd frontend
npm install
npm run dev
```

Vite runs at `http://localhost:5173`

---

## Git Rules

- Pull before you start working
- Commit only your own files
- Commit message format: `feat: add loan application page`
- Push to your own branch, not main