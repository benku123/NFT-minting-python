const signupContainer = document.getElementById('signup-container');

    // Add an enhanced entrance animation when the page loads
    window.addEventListener('load', () => {
        signupContainer.style.opacity = '0';
        signupContainer.style.transform = 'scale(0.8)';

        // Use setTimeout to delay the animation for better visual effect
        setTimeout(() => {
            signupContainer.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            signupContainer.style.opacity = '1';
            signupContainer.style.transform = 'scale(1)';
        }, 100);
    });
