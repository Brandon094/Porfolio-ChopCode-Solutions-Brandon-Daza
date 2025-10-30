document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const menuToggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('nav');
    const navLinks = document.querySelectorAll('nav a');

    // Función para alternar el menú
    function toggleMenu() {
        menuToggle.classList.toggle('active');
        nav.classList.toggle('active');
    }

    // Event Listeners
    menuToggle.addEventListener('click', toggleMenu);

    // Cerrar menú al hacer clic en un enlace
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            menuToggle.classList.remove('active');
            nav.classList.remove('active');
        });
    });

    // Cerrar menú al hacer clic fuera
    document.addEventListener('click', (e) => {
        if (!nav.contains(e.target) && !menuToggle.contains(e.target) && nav.classList.contains('active')) {
            toggleMenu();
        }
    });

    // Cerrar menú al redimensionar la ventana
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768 && nav.classList.contains('active')) {
            toggleMenu();
        }
    });
});