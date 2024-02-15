function toggleDarkMode() {
    const body = document.body;
    const toggleIcon = document.getElementById('toggle-icon');
    body.classList.toggle('dark-mode');
    if (body.classList.contains('dark-mode')) {
        toggleIcon.classList.remove('fa-sun');
        toggleIcon.classList.add('fa-moon');
    } else {
        toggleIcon.classList.remove('fa-moon');
        toggleIcon.classList.add('fa-sun');
    }
    localStorage.setItem('darkMode', body.classList.contains('dark-mode'));
}

window.onload = () => {
    const toggleIcon = document.getElementById('toggle-icon');
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');    
        toggleIcon.classList.remove('fa-sun');
        toggleIcon.classList.add('fa-moon');
    } else {
        toggleIcon.classList.remove('fa-moon');
        toggleIcon.classList.add('fa-sun');
    }
};