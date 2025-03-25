// Toggle between light and dark mode
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
  }
  
  // Show and hide dropdown menu
  function toggleDropdown() {
    document.getElementById('dropdown-menu').classList.toggle('hidden');
  }
  
  // Hide all pages and show only the selected one
  function showPage(pageId) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.classList.add('hidden'));
    
    document.getElementById(pageId).classList.remove('hidden');
  }