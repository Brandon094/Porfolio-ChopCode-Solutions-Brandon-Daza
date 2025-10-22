// carrusel.js - Funcionalidad para los carruseles de proyectos
document.addEventListener('DOMContentLoaded', function () {
    // Inicializar todos los carruseles
    const carruseles = document.querySelectorAll('.carrusel');

    carruseles.forEach((carrusel, carruselIndex) => {
        const imagenes = carrusel.querySelector('.carrusel-imagenes');
        const puntos = carrusel.querySelectorAll('.punto');
        const btnPrev = carrusel.querySelector('.prev');
        const btnNext = carrusel.querySelector('.next');

        let indiceActual = 0;
        const totalImagenes = puntos.length;

        // Función para actualizar el carrusel
        function actualizarCarrusel() {
            // CORRECCIÓN: Cambiar 1000 por 100
            const desplazamiento = -indiceActual * 100;
            imagenes.style.transform = `translateX(${desplazamiento}%)`;

            // Actualizar puntos
            puntos.forEach((punto, index) => {
                punto.classList.toggle('activo', index === indiceActual);
            });
            
            console.log(`Imagen ${indiceActual + 1}, Desplazamiento: ${desplazamiento}%`);
        }

        // Event listeners para los puntos
        puntos.forEach((punto, index) => {
            punto.addEventListener('click', () => {
                indiceActual = index;
                actualizarCarrusel();
            });
        });

        // Event listeners para los botones
        btnPrev.addEventListener('click', () => {
            indiceActual = (indiceActual - 1 + totalImagenes) % totalImagenes;
            actualizarCarrusel();
        });

        btnNext.addEventListener('click', () => {
            indiceActual = (indiceActual + 1) % totalImagenes;
            actualizarCarrusel();
        });

        // Auto-avance opcional (descomenta si lo quieres)
        setInterval(() => {
            indiceActual = (indiceActual + 1) % totalImagenes;
            actualizarCarrusel();
        }, 8000);
        
        // Inicializar el carrusel en la primera imagen
        actualizarCarrusel();
    });

    console.log('Carruseles inicializados correctamente');
});