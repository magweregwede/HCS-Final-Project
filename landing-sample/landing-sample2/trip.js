// Modified toggleSubmenu function
function toggleSubmenu(menuId) {
    const submenu = document.getElementById(menuId);
    submenu.classList.toggle('show');
    
    // Close other submenus at the same level
    const parentMenu = submenu.parentElement.closest('.submenu');
    if (parentMenu) {
        Array.from(parentMenu.children)
            .filter(item => item !== submenu.parentElement)
            .forEach(item => {
                const childSubmenus = item.querySelectorAll('.submenu');
                childSubmenus.forEach(child => child.classList.remove('show'));
            });
    }
    
    // Update active menu item
    document.querySelectorAll('.menu-item').forEach(item => {
        if (item.contains(event.currentTarget)) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}

// Add this click handler for submenu items
document.querySelectorAll('.submenu-item').forEach(item => {
    item.addEventListener('click', function(e) {
        if (this.querySelector('.submenu')) {
            e.stopPropagation();
            const submenu = this.querySelector('.submenu');
            submenu.classList.toggle('show');
        }
    });
});