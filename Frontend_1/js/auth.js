// Function to check authentication Status
function checkAuth() {
    const token = localStorage.getItem("token");
    const userStr = localStorage.getItem("user");

    // Pages that don't require token
    const publicPages = ["login.html", "register.html"];
    const currentPage = window.location.pathname.split("/").pop() || "login.html";

    // Skip auth check if we are just exploring at root folder without a specific html file (for local dev)
    if (!currentPage.endsWith(".html") && !currentPage.endsWith("/")) {
        return userStr ? JSON.parse(userStr) : null;
    }

    if (!token && !publicPages.includes(currentPage)) {
        // Redirect to login if user is NOT logged in and trying to access protected page
        const prefix = window.location.pathname.includes("/admin/") ? "../" : "";
        window.location.href = prefix + "login.html";
        return null;
    }

    if (token && publicPages.includes(currentPage)) {
        // Redirect to dashboard if logged in and trying to access login/register
        try {
            const user = JSON.parse(userStr);
            if (user && user.role === "admin") {
                window.location.href = "admin/admin-dashboard.html";
            } else {
                window.location.href = "Dashboard.html";
            }
        } catch (e) {
            window.location.href = "Dashboard.html";
        }
    }

    // Restrict access to admin pages if user is not admin
    if (token && window.location.pathname.includes("/admin/")) {
        try {
            const user = JSON.parse(userStr);
            if (user && user.role !== "admin") {
                window.location.href = "../Dashboard.html";
            }
        } catch (e) {
            window.location.href = "../Dashboard.html";
        }
    }

    return userStr ? JSON.parse(userStr) : null;
}

function handleLogout() {
    apiLogout().catch(console.error).finally(() => {
        localStorage.removeItem("token");
        localStorage.removeItem("user");

        const prefix = window.location.pathname.includes("/admin/") ? "../" : "";
        window.location.href = prefix + "login.html";
    });
}

async function apiLogout() {
    const API_BASE = 'http://127.0.0.1:8000';
    const token = localStorage.getItem('token');
    if (!token) return;
    try {
        await fetch(`${API_BASE}/api/auth/logout/`, {
            method: 'POST',
            headers: {
                'Authorization': `Token ${token}`
            }
        });
    } catch (e) {
        console.error("Logout failed at server", e);
    }
}

// Call checkAuth immediately on script load to redirect fast
const currentUser = checkAuth();

// Attach logout logic to all elements with class 'logout-btn' when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const logoutBtns = document.querySelectorAll('.logout-btn');
    logoutBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            handleLogout();
        });
    });

    // If there are navbar user elements, update them dynamically
    const nameDisplays = document.querySelectorAll('.display-user-name');
    if (nameDisplays.length > 0 && currentUser) {
        nameDisplays.forEach(el => el.textContent = currentUser.name);
    }
});
