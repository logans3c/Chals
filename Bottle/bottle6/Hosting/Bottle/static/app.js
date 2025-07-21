document.addEventListener('DOMContentLoaded', function() {
    // Highlight all buttons on hover
    document.querySelectorAll('button').forEach(function(btn) {
        btn.addEventListener('mouseenter', function() {
            btn.style.backgroundColor = '#45a049';
        });
        btn.addEventListener('mouseleave', function() {
            btn.style.backgroundColor = '';
        });
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function(link) {
        link.addEventListener('click', function(e) {
            var target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Show/hide password toggle for all password fields
    document.querySelectorAll('input[type="password"]').forEach(function(pwd) {
        var toggle = document.createElement('span');
        toggle.textContent = '👁️';
        toggle.style.cursor = 'pointer';
        toggle.style.marginLeft = '8px';
        toggle.title = 'Show/Hide Password';
        toggle.addEventListener('click', function() {
            pwd.type = pwd.type === 'password' ? 'text' : 'password';
        });
        pwd.parentNode.insertBefore(toggle, pwd.nextSibling);
    });

    // Highlight notes on hover
    document.querySelectorAll('li, .note').forEach(function(note) {
        note.addEventListener('mouseenter', function() {
            note.style.backgroundColor = '#e8f5e9';
        });
        note.addEventListener('mouseleave', function() {
            note.style.backgroundColor = '';
        });
    });

    // Example: Alert on form submit (for demonstration, remove in production)
    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            // Uncomment the next line to see alerts on submit
            // alert('Form submitted!');
        });
    });
});
