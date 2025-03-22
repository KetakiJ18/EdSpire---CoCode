document.addEventListener('DOMContentLoaded', function() {
    // Add hover effect to course buttons
    const courseButtons = document.querySelectorAll('.course-button');
    
    courseButtons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});