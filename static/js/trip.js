// Toggle submenus
function toggleSubmenu(menuId) {
    const submenu = document.getElementById(menuId);
    submenu.classList.toggle('show');
    event.stopPropagation();
}

// Load content dynamically
function loadContent(page) {
    const contentArea = document.getElementById('content-area');

    // Update active nav link
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.classList.remove('active');
        if (link.textContent.toLowerCase() === page.toLowerCase()) {
            link.classList.add('active');
        }
    });

    // Update active menu item
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
        if (item.textContent.toLowerCase().includes(page.toLowerCase())) {
            item.classList.add('active');
        }
    });

    // Clear previous content
    contentArea.innerHTML = '';

    // Create delivery navigation (shown only for deliveries section)
    const deliveryNav = document.createElement('div');
    deliveryNav.className = 'delivery-nav';
    deliveryNav.style.display = 'none';
    
    const deliveryButtons = [
        { text: 'New Trips', url: '/app/trip/new' },
        { text: 'Ongoing Trips', url: '/app/trip/?status=ongoing' },
        { text: 'Review Trips', url: '/app/triproute' }
    ];

    deliveryButtons.forEach(btn => {
        const button = document.createElement('a');
        button.textContent = btn.text;
        button.className = 'btn btn-primary';
        button.href = btn.url;
        button.style.marginRight = '10px';
        deliveryNav.appendChild(button);
    });

    // Set content based on page
    switch (page.toLowerCase()) {
        case 'dashboard':
            contentArea.innerHTML = `
                <div class="page-header">
                    <h1>Dashboard</h1>
                    <button class="btn btn-primary">Refresh Data</button>
                </div>
                
                <div class="dashboard-grid">
                    <div class="stat-card">
                        <h3>Active Deliveries</h3>
                        <div class="value">42</div>
                        <div class="change">+5% from last week</div>
                    </div>
                    
                    <div class="stat-card">
                        <h3>Available Drivers</h3>
                        <div class="value">18</div>
                        <div class="change">-2 from yesterday</div>
                    </div>
                    
                    <div class="stat-card">
                        <h3>On-time Rate</h3>
                        <div class="value">94%</div>
                        <div class="change">+3% from last month</div>
                    </div>
                    
                    <div class="stat-card">
                        <h3>Total Kilometres</h3>
                        <div class="value">12,456</div>
                        <div class="change negative">-8% from last week</div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2>Recent Activities</h2>
                    </div>
                    <p>Content for recent activities will go here...</p>
                </div>
            `;
            break;

        case 'deliveries':
            deliveryNav.style.display = 'block';
            contentArea.innerHTML = `
                <div class="page-header">
                    <h1>Deliveries Management</h1>
                    <p>Select an action below to manage deliveries</p>
                </div>
                <div class="deliveries-content">
                    <!-- Delivery buttons will be inserted here -->
                </div>
            `;
            contentArea.querySelector('.deliveries-content').appendChild(deliveryNav);
            break;

        case 'products':
            contentArea.innerHTML = `
                
                <div class="card">
                    <div class="card-header">
                        <h2>Product Inventory</h2>
                    </div>
                    
                    <table>
                        <thead>
                            <tr>
                                <th>Product Name</th>
                                <th>Category</th>
                                <th>Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>PRD-1001</td>
                                <td>Electronics Package</td>
                                <td>Fragile</td>
                            </tr>
                            <tr>
                                <td>PRD-1002</td>
                                <td>Furniture Set</td>
                                <td>Bulky</td>
                            </tr>
                            <tr>
                                <td>PRD-1003</td>
                                <td>Clothing Bundle</td>
                                <td>Standard</td>
                            </tr>
                        </tbody>
                    </table>
                    
            `;
            break;

        case 'routes':
            contentArea.innerHTML = `
                <div class="card">
                 <table>
                        <thead>
                            <tr>
                                <th>Origin</th>
                                <th>Destination</th>
                                <th>Distance [km]</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>PRD-1001</td>
                                <td>Electronics Package</td>
                                <td>Fragile</td>
                            </tr>
                            <tr>
                                <td>PRD-1002</td>
                                <td>Furniture Set</td>
                                <td>Bulky</td>
                            </tr>
                            <tr>
                                <td>PRD-1003</td>
                                <td>Clothing Bundle</td>
                                <td>32</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            `;
            break;

        default:
            contentArea.innerHTML = `
                <div class="page-header">
                    <h1>Page Not Found</h1>
                    <button class="btn btn-primary" onclick="loadContent('dashboard')">Back to Dashboard</button>
                </div>
                <div class="card">
                    <p>The requested page could not be found.</p>
                </div>
            `;
    }
}

// Dark Mode Toggle
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const darkModeToggle = document.getElementById('darkModeToggle');
    const isDarkMode = document.body.classList.contains('dark-mode');

    if (isDarkMode) {
        darkModeToggle.innerHTML = '<i class="icon-sun"></i><span></span>';
        localStorage.setItem('darkMode', 'enabled');
    } else {
        darkModeToggle.innerHTML = '<i class="icon-moon"></i><span></span>';
        localStorage.setItem('darkMode', 'disabled');
    }
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Check for saved dark mode preference
    if (localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark-mode');
        document.getElementById('darkModeToggle').innerHTML = '<i class="icon-sun"></i><span></span>';
    }

    // Set up dark mode toggle
    document.getElementById('darkModeToggle').addEventListener('click', toggleDarkMode);

    // Close submenus when clicking outside
    document.addEventListener('click', function() {
        document.querySelectorAll('.submenu').forEach(submenu => {
            submenu.classList.remove('show');
        });
    });

    // Prevent submenu from closing when clicking inside it
    document.querySelectorAll('.submenu').forEach(submenu => {
        submenu.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    });

    // Initialize with dashboard content
    // loadContent('dashboard');
});