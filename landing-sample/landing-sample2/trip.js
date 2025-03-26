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

    // Clear previous content
    contentArea.innerHTML = '';

    // Create container for delivery buttons (will be shown only for deliveries section)
    const deliveryNav = document.createElement('div');
    deliveryNav.className = 'nav-bar';
    deliveryNav.style.display = 'none'; // Hidden by default
    deliveryNav.style.marginBottom = '20px';
    deliveryNav.style.padding = '10px';
    // deliveryNav.style.backgroundColor = '#f5f5f5';
    deliveryNav.style.borderRadius = '5px';

    // Create delivery navigation buttons
    const buttonNames = ['New Trip', 'View Trips', 'Trip Review'];
    buttonNames.forEach(btnName => {
        const button = document.createElement('button');
        button.textContent = btnName;
        button.className = 'btn btn-primary';
        button.style.marginRight = '10px';
        button.onclick = () => loadContent(btnName.toLowerCase().replace(' ', '-'));
        deliveryNav.appendChild(button);
    });

    const iframeContainer = document.createElement('div');
    iframeContainer.style.width = '100%';
    iframeContainer.style.height = '100%';
    iframeContainer.style.overflow = 'hidden';

    // Create iframe
    const iframe = document.createElement('iframe');
    iframe.id = 'content-iframe';
    iframe.style.width = '100%';
    iframe.style.height = '100px'; // Initial small height
    iframe.style.border = 'none';
    iframe.style.overflow = 'hidden';

    // Auto-resize function
    function resizeIframe() {
        try {
            const body = iframe.contentDocument.body;
            const html = iframe.contentDocument.documentElement;
            const height = Math.max(
                body.scrollHeight,
                body.offsetHeight,
                html.clientHeight,
                html.scrollHeight,
                html.offsetHeight
            );
            iframe.style.height = height + 'px';
        } catch (e) {
            console.log('Resize error:', e);
        }
    }

    // Set up iframe load event
    iframe.onload = function() {
        // Initial resize
        resizeIframe();
        
        // Periodic checks for dynamic content
        const resizeInterval = setInterval(resizeIframe, 100);
        
        // Clean up when iframe unloads
        iframe.contentWindow.addEventListener('unload', () => {
            clearInterval(resizeInterval);
        });
    };


    // Set iframe source based on page
    switch (page) {
        case 'deliveries':
            deliveryNav.style.display = 'block'; // Show delivery navigation
            // iframe.src = '#'; // Replace with your deliveries.html path
            break;
            
        case 'new-trip':
            deliveryNav.style.display = 'block'; // Show delivery navigation
            iframe.src = './login.html'; // Replace with your new-trip.html path
            break;
            
        case 'view-trips':
            deliveryNav.style.display = 'block'; // Show delivery navigation
            iframe.src = './login.html'; // Replace with your view-trips.html path
            break;
            
        case 'trip-review':
            deliveryNav.style.display = 'block'; // Show delivery navigation
            iframe.src = './login.html'; // Replace with your trip-review.html path
            break;
            
        // Other cases remain the same
        case 'dashboard':
            // iframe.src = '#'; // Replace with your dashboard.html path
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
            iframe.src = './login.html'; // Replace with your products.html path
            break;
        case 'routes':
            iframe.src = './login.html'; // Replace with your routes.html path
            break;
        case 'driver-availability':
            iframe.src = './login.html'; // Replace with your driver-availability.html path
            break;
        case 'truck-companies':
            iframe.src = './login.html'; // Replace with your truck-companies.html path
            break;
        case 'truck-drivers':
            iframe.src = './login.html'; // Replace with your truck-drivers.html path
            break;
        case 'reporting':
            iframe.src = './login.html'; // Replace with your reporting.html path
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
            return;
    }

    // Add elements to content area
    if (page === 'deliveries' || page === 'new-trip' || page === 'view-trips' || page === 'trip-review') {
        contentArea.appendChild(deliveryNav);
    }
    iframeContainer.appendChild(iframe);
    contentArea.appendChild(iframeContainer);
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