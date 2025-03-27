document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.querySelector('.login-form');
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('id_password');
    
    // Toggle password visibility
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function () {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.textContent = type === 'password' ? '👁️' : '👁️‍🗨️';
        });
    }

    // Input field focus effects
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', function () {
            this.style.borderColor = 'var(--primary)';
            this.style.boxShadow = '0 0 0 3px var(--primary-light)';
        });

        input.addEventListener('blur', function () {
            this.style.borderColor = '';
            this.style.boxShadow = '';
        });
    });
});