document.addEventListener('DOMContentLoaded', () => {
    const themeToggleBtn = document.getElementById('theme-toggle');
    
    // 1. Check if the user previously saved a theme preference
    const currentTheme = localStorage.getItem('theme');
    if (currentTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    }

    // 2. Listen for clicks on the toggle button
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            // Check what the current theme is
            let theme = document.documentElement.getAttribute('data-theme');
            
            if (theme === 'dark') {
                // Switch to Light
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem('theme', 'light');
            } else {
                // Switch to Dark
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
            }
        });
    }
});
