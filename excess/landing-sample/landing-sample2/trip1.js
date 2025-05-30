 // Toggle submenus
 function toggleSubmenu(menuId) {
    const submenu = document.getElementById(menuId);
    submenu.classList.toggle('show');

    // Update active menu item
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    event.currentTarget.classList.add('active');
}

// Load content dynamically
function loadContent(page) {
    const contentArea = document.getElementById('content-area');

    // Update active nav link
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.classList.remove('active');
        if (link.textContent.toLowerCase() === page.toLowerCase() ||
            (page !== 'dashboard' && link.textContent === 'Home')) {
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

    // In a real application, this would fetch content from the server
    // For this example, we'll just change the content manually

    switch (page) {
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

        case 'products':
            contentArea.innerHTML = `
                <div class="page-header">
                    <h1>Products</h1>
                    <button class="btn btn-primary">Add Product</button>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2>Product Inventory</h2>
                        <div>
                            <button class="btn btn-secondary">Export</button>
                            <button class="btn btn-primary">Filter</button>
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
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>PRD-1001</td>
                                <td>Industrial Bearings</td>
                                <td>Machinery Parts</td>
                                <td>450</td>
                                <td>In Stock</td>
                            </tr>
                            <tr>
                                <td>PRD-1002</td>
                                <td>Steel Pipes</td>
                                <td>Construction</td>
                                <td>320</td>
                                <td>In Stock</td>
                            </tr>
                            <tr>
                                <td>PRD-1003</td>
                                <td>Electrical Wires</td>
                                <td>Electrical</td>
                                <td>780</td>
                                <td>Low Stock</td>
                            </tr>
                            <tr>
                                <td>PRD-1004</td>
                                <td>Hydraulic Pumps</td>
                                <td>Machinery Parts</td>
                                <td>120</td>
                                <td>In Stock</td>
                            </tr>
                            <tr>
                                <td>PRD-1005</td>
                                <td>Aluminum Sheets</td>
                                <td>Construction</td>
                                <td>95</td>
                                <td>Out of Stock</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            `;
            break;

        case 'routes':
            contentArea.innerHTML = `
                <div class="page-header">
                    <h1>Routes</h1>
                    <button class="btn btn-primary">Create New Route</button>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2>Route Network</h2>
                        <div>
                            <button class="btn btn-secondary">Map View</button>
                            <button class="btn btn-primary">List View</button>
                        </div>
                    </div>
                    
                    <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                        <div style="flex: 1; min-width: 300px;">
                            <h3 style="margin-bottom: 15px;">Primary Routes</h3>
                            <ul style="list-style: none;">
                                <li style="padding: 10px; border-bottom: 1px solid var(--light-color);">East Coast Corridor (NYC to Miami)</li>
                                <li style="padding: 10px; border-bottom: 1px solid var(--light-color);">Midwest Express (Chicago to Denver)</li>
                                <li style="padding: 10px; border-bottom: 1px solid var(--light-color);">Southern Cross (Dallas to Atlanta)</li>
                                <li style="padding: 10px; border-bottom: 1px solid var(--light-color);">West Coast Highway (LA to Seattle)</li>
                            </ul>
                        </div>
                        
                        <div style="flex: 1; min-width: 300px;">
                            <h3 style="margin-bottom: 15px;">Secondary Routes</h3>
                            <ul style="list-style: none;">
                                <li style="padding: 10px; border-bottom: 1px solid var(--light-color);">Northeast Loop (Boston to Philadelphia)</li>
                                <li style="padding: 10px; border-bottom: 1px solid var(--light-color);">Central Plains (Kansas City to Omaha)</li>
                                <li style="padding: 10px; border-bottom: 1px solid var(--light-color);">Southwest Connection (Phoenix to El Paso)</li>
                            </ul>
                        </div>
                        
                        <div style="flex: 1; min-width: 300px;">
                            <h3 style="margin-bottom: 15px;">Route Statistics</h3>
                            <div style="background: var(--card-bg); padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                                <p>Total Routes: <strong>7</strong></p>
                                <p>Average Distance: <strong>1,245 miles</strong></p>
                                <p>Average Duration: <strong>2.5 days</strong></p>
                                <p>Most Active: <strong>East Coast Corridor</strong></p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            break;

        case 'driver-availability':
            contentArea.innerHTML = `
                <div class="page-header">
                    <h1>Driver Availability</h1>
                    <button class="btn btn-primary">Update Schedule</button>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2>Current Driver Status</h2>
                        <div>
                            <button class="btn btn-secondary">Export</button>
                            <button class="btn btn-primary">Filter</button>
                        </div>
                    </div>
                    
                    <table>
                        <thead>
                            <tr>
                                <th>Driver ID</th>
                                <th>Name</th>
                                <th>Current Location</th>
                                <th>Status</th>
                                <th>Next Available</th>
                                <th>Assigned Route</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>DRV-1001</td>
                                <td>John Smith</td>
                                <td>Chicago, IL</td>
                                <td>On Duty</td>
                                <td>Tomorrow 8AM</td>
                                <td>Midwest Express</td>
                            </tr>
                            <tr>
                                <td>DRV-1002</td>
                                <td>Maria Garcia</td>
                                <td>Atlanta, GA</td>
                                <td>Available</td>
                                <td>Immediate</td>
                                <td>None</td>
                            </tr>
                            <tr>
                                <td>DRV-1003</td>
                                <td>Robert Johnson</td>
                                <td>Denver, CO</td>
                                <td>On Break</td>
                                <td>Today 5PM</td>
                                <td>Southern Cross</td>
                            </tr>
                            <tr>
                                <td>DRV-1004</td>
                                <td>Sarah Williams</td>
                                <td>Dallas, TX</td>
                                <td>On Duty</td>
                                <td>Tomorrow 10AM</td>
                                <td>West Coast Highway</td>
                            </tr>
                            <tr>
                                <td>DRV-1005</td>
                                <td>James Brown</td>
                                <td>Miami, FL</td>
                                <td>Available</td>
                                <td>Immediate</td>
                                <td>None</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2>Availability Calendar</h2>
                    </div>
                    <p style="text-align: center; padding: 50px 0; background: var(--light-color); border-radius: 8px;">
                        Interactive calendar view would be displayed here showing driver availability over time.
                    </p>
                </div>
            `;
            break;

        case 'deliveries':
            contentArea.innerHTML = `
                <div class="page-header">
                    <h1>Deliveries</h1>
                    <div>
                        <button class="btn btn-primary" onclick="loadContent('new-trip')">New Trip Log</button>
                        <button class="btn btn-primary" onclick="loadContent('view-trips')">View Trips</button>
                        <button class="btn btn-primary" onclick="loadContent('trip-review')">Trip Review</button>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2>Delivery Management</h2>
                    </div>
                    <p>Select an option above to manage deliveries.</p>
                </div>
            `;
            break;

        case 'new-trip':
            contentArea.innerHTML = `
                <div class="page-header">
                    <h1>New Trip Log</h1>
                    <button class="btn btn-primary" onclick="loadContent('deliveries')">Back to Deliveries</button>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2>Create New Trip</h2>
                    </div>
                    <p>Form for creating a new trip log will go here...</p>
                </div>
            `;
            break;

        case 'view-trips':
            contentArea.innerHTML = `
                <div class="page-header">
                    <h1>View Trips</h1>
                    <button class="btn btn-primary" onclick="loadContent('deliveries')">Back to Deliveries</button>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2>Trip List</h2>
                    </div>
                    <p>Table showing all trips will go here...</p>
                </div>
            `;
            break;

        case 'trip-review':
            contentArea.innerHTML = `
                <div class="page-header">
                    <h1>Trip Review</h1>
                    <button class="btn btn-primary" onclick="loadContent('deliveries')">Back to Deliveries</button>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2>Trip Performance</h2>
                    </div>
                    <p>Analytics and review tools for trips will go here...</p>
                </div>
            `;
            break;

        case 'truck-companies':
            contentArea.innerHTML = `
                <div class="page-header">
                    <h1>Truck Companies</h1>
                    <button class="btn btn-primary">Add Company</button>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2>Truck Company Management</h2>
                    </div>
                    <p>Content for managing truck companies will go here...</p>
                </div>
            `;
            break;

        case 'truck-drivers':
            contentArea.innerHTML = `
                <div class="page-header">
                    <h1>Truck Drivers</h1>
                    <button class="btn btn-primary">Add Driver</button>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2>Truck Driver Management</h2>
                    </div>
                    <p>Content for managing truck drivers will go here...</p>
                </div>
            `;
            break;

        case 'reporting':
            contentArea.innerHTML = `
                <div class="page-header">
                    <h1>Reporting</h1>
                    <button class="btn btn-primary">Generate Report</button>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2>Reports Dashboard</h2>
                    </div>
                    <p>Content for reporting will go here...</p>
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
document.addEventListener('DOMContentLoaded', function () {
    // Check for saved dark mode preference
    if (localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark-mode');
        document.getElementById('darkModeToggle').innerHTML = '<i class="icon-sun"></i><span>Light Mode</span>';
    }

    // Set up dark mode toggle
    document.getElementById('darkModeToggle').addEventListener('click', toggleDarkMode);

    // Set up event listeners for nav links
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelectorAll('.nav-links a').forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Set up event listeners for sidebar menu items
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', function () {
            document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Set up event listeners for submenu items
    document.querySelectorAll('.submenu-item').forEach(item => {
        item.addEventListener('click', function () {
            document.querySelectorAll('.submenu-item').forEach(i => i.classList.remove('active'));
            this.classList.add('active');
        });
    });
});