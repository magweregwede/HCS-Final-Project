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
        { text: 'New Trips', url: '/new-trips/' },
        { text: 'Ongoing Trips', url: '/ongoing-trips/' },
        { text: 'Review Trips', url: '/review-trips/' }
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
                        <h3>Total Miles</h3>
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
                <div class="page-header">
                    <h1>Product Management</h1>
                    <button class="btn btn-primary">Add New Product</button>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2>Product Inventory</h2>
                        <div class="search-bar">
                            <input type="text" placeholder="Search products..." class="search-input">
                            <button class="btn btn-secondary">Search</button>
                        </div>
                    </div>
                    
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Product Name</th>
                                <th>Category</th>
                                <th>Quantity</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>PRD-1001</td>
                                <td>Electronics Package</td>
                                <td>Fragile</td>
                                <td>15</td>
                                <td><span class="status active">Active</span></td>
                                <td>
                                    <button class="btn btn-secondary">Edit</button>
                                    <button class="btn btn-danger">Delete</button>
                                </td>
                            </tr>
                            <tr>
                                <td>PRD-1002</td>
                                <td>Furniture Set</td>
                                <td>Bulky</td>
                                <td>8</td>
                                <td><span class="status active">Active</span></td>
                                <td>
                                    <button class="btn btn-secondary">Edit</button>
                                    <button class="btn btn-danger">Delete</button>
                                </td>
                            </tr>
                            <tr>
                                <td>PRD-1003</td>
                                <td>Clothing Bundle</td>
                                <td>Standard</td>
                                <td>32</td>
                                <td><span class="status inactive">Inactive</span></td>
                                <td>
                                    <button class="btn btn-secondary">Edit</button>
                                    <button class="btn btn-danger">Delete</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                    
                    <div class="pagination">
                        <button class="btn btn-secondary">Previous</button>
                        <span>Page 1 of 3</span>
                        <button class="btn btn-secondary">Next</button>
                    </div>
                </div>
            `;
            break;

        case 'routes':
            contentArea.innerHTML = `
                <div class="page-header">
                    <h1>Route Management</h1>
                    <button class="btn btn-primary">Add New Route</button>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2>Available Routes</h2>
                        <div class="filter-options">
                            <select class="form-control">
                                <option>All Regions</option>
                                <option>North</option>
                                <option>South</option>
                                <option>East</option>
                                <option>West</option>
                            </select>
                            <button class="btn btn-secondary">Apply Filters</button>
                        </div>
                    </div>
                    
                    <div class="map-container">
                        <div class="map-placeholder">
                            <p>Map visualization would appear here</p>
                        </div>
                    </div>
                    
                    <div class="route-list">
                        <div class="route-card">
                            <h3>RT-101: New York to Boston</h3>
                            <div class="route-details">
                                <p><strong>Distance:</strong> 215 miles</p>
                                <p><strong>Duration:</strong> 4 hours 30 minutes</p>
                                <p><strong>Stops:</strong> 3</p>
                                <p><strong>Status:</strong> <span class="status active">Active</span></p>
                            </div>
                            <div class="route-actions">
                                <button class="btn btn-primary">View Details</button>
                                <button class="btn btn-secondary">Edit</button>
                            </div>
                        </div>
                        
                        <div class="route-card">
                            <h3>RT-102: Chicago to Detroit</h3>
                            <div class="route-details">
                                <p><strong>Distance:</strong> 282 miles</p>
                                <p><strong>Duration:</strong> 5 hours 15 minutes</p>
                                <p><strong>Stops:</strong> 2</p>
                                <p><strong>Status:</strong> <span class="status active">Active</span></p>
                            </div>
                            <div class="route-actions">
                                <button class="btn btn-primary">View Details</button>
                                <button class="btn btn-secondary">Edit</button>
                            </div>
                        </div>
                    </div>
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
        darkModeToggle.innerHTML = '<i class="icon-sun"></i><span>Light Mode</span>';
        localStorage.setItem('darkMode', 'enabled');
    } else {
        darkModeToggle.innerHTML = '<i class="icon-moon"></i><span>Dark Mode</span>';
        localStorage.setItem('darkMode', 'disabled');
    }
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Check for saved dark mode preference
    if (localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark-mode');
        document.getElementById('darkModeToggle').innerHTML = '<i class="icon-sun"></i><span>Light Mode</span>';
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
    loadContent('dashboard');
});