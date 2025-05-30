document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');
    const emailInput = document.getElementById('email');
    const emailError = document.getElementById('email-error');
    const passwordError = document.getElementById('password-error');

    // Toggle password visibility
    togglePassword.addEventListener('click', function () {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        this.textContent = type === 'password' ? '👁️' : '👁️‍🗨️';
    });

    // Form validation
    loginForm.addEventListener('submit', function (e) {
        e.preventDefault();
        let isValid = true;

        // // Email validation
        // if (!emailInput.value || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value)) {
        //     emailError.style.display = 'block';
        //     emailInput.style.borderColor = '#e74c3c';
        //     isValid = false;
        // } else {
        //     emailError.style.display = 'none';
        //     emailInput.style.borderColor = '';
        // }

        // Password validation
        // if (!passwordInput.value || passwordInput.value.length < 8) {
        //     passwordError.style.display = 'block';
        //     passwordInput.style.borderColor = '#e74c3c';
        //     isValid = false;
        // } else {
        //     passwordError.style.display = 'none';
        //     passwordInput.style.borderColor = '';
        // }

        // If form is valid, simulate successful login
        if (isValid) {
            // Show loading state
            const submitBtn = loginForm.querySelector('button[type="submit"]');
            submitBtn.textContent = 'Signing in...';
            submitBtn.disabled = true;

            // Simulate API call
            setTimeout(() => {
                // For demo purposes, just show an alert
                alert('Login successful! Redirecting to dashboard...');

                // In a real app, you would redirect to the dashboard:
                // window.location.href = './landing-sample2.html';

                // Reset form
                submitBtn.textContent = 'Sign In';
                submitBtn.disabled = false;
            }, 1500);
        }
    });

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