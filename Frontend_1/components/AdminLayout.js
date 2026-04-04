function buildAdminLayout(activeId) {
    const navLinks = [
        { id: "dashboard", text: "Dashboard", href: "admin-dashboard.html" },
        { id: "users", text: "Users", href: "manage-users.html" },
        { id: "loans", text: "Loans", href: "loan-approvals.html" },
        { id: "fraud", text: "Fraud", href: "fraud-alerts.html" },
        { id: "transactions", text: "Transactions", href: "all-transactions.html" }
    ];

    const linksHtml = navLinks.map(link =>
        `<a href="${link.href}" class="fake-link ${link.id === activeId ? 'active' : ''}">${link.text}</a>`
    ).join("");

    const layoutHtml = `
            <div class="fake-navbar">
                <span>SmartBank Admin</span>
                <span style="font-size:13px;">
                    <span class="display-user-name">Admin</span> &nbsp;
                    <button class="logout-btn" style="background:rgba(255,255,255,0.2);padding:5px 10px;border-radius:4px;border:none;color:white;cursor:pointer;font-weight:600;">Logout</button>
                </span>
            </div>
            <div class="layout">
                <div class="fake-sidebar">
                    ${linksHtml}
                </div>
                <div class="main-content" id="admin-container">
                    <!-- page content moves here -->
                </div>
            </div>
    `;

    document.body.insertAdjacentHTML("afterbegin", layoutHtml);

    // Move the original page body content inside #admin-container
    const container = document.getElementById("admin-container");
    const adminWrapper = document.getElementById("admin-wrapper");
    if (adminWrapper) {
        container.appendChild(adminWrapper);
        adminWrapper.style.display = "block";
    }

    // Wire up the logout button dynamically injected
    const logoutBtn = document.querySelector(".logout-btn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            if (window.handleLogout) {
                window.handleLogout();
            } else {
                localStorage.clear();
                window.location.href = "../login.html";
            }
        });
    }

    // Attempt to set display name if auth provides it
    try {
        const userStr = localStorage.getItem("user");
        if (userStr) {
            const user = JSON.parse(userStr);
            const userDisplays = document.querySelectorAll(".display-user-name");
            userDisplays.forEach(el => el.textContent = user.name);
        }
    } catch (e) { }
}
