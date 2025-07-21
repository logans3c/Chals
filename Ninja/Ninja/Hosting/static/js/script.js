document.addEventListener('DOMContentLoaded', function() {
    // Automatically hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    if (flashMessages) {
        setTimeout(() => {
            flashMessages.forEach(message => {
                message.style.display = 'none';
            });
        }, 5000);
    }

    // Password confirmation validation
    const registerForm = document.querySelector('form[action*="register"]');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirm_password');
            
            if (password.value !== confirmPassword.value) {
                e.preventDefault();
                alert('Passwords do not match!');
                
                // Add error styling
                password.classList.add('error');
                confirmPassword.classList.add('error');
                
                // Add error styling
                password.style.borderColor = 'red';
                confirmPassword.style.borderColor = 'red';
            }
        });
        
        // Remove error styling when user starts typing again
        const passwordInputs = [
            document.getElementById('password'),
            document.getElementById('confirm_password')
        ];
        
        passwordInputs.forEach(input => {
            if (input) {
                input.addEventListener('input', function() {
                    passwordInputs.forEach(field => {
                        field.classList.remove('error');
                        field.style.borderColor = '';
                    });
                });
            }
        });
    }
    
    // Animate navigation links
    const navLinks = document.querySelectorAll('nav ul li a');
    navLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Add event listeners to any activity selection buttons
    const activityButtons = document.querySelectorAll('.activity-select-btn');
    activityButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const activity = this.getAttribute('data-activity');
            const username = this.getAttribute('data-username') || '';
            goToActivity(activity, username);
        });
    });
});

// Function to navigate to an activity page
function goToActivity(activity, username) {
    if (!username && document.getElementById('activity-username')) {
        username = document.getElementById('activity-username').value;
    }
    
    if (!username) {
        username = prompt("Please enter a username to check activities for:");
        if (!username) return; // User cancelled the prompt
    }
    
    window.location.href = `/activity?action=${activity}.html&username=${username}`;
}
