document.getElementById('contactForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const formData = {
        name: document.getElementById('name').value.trim(),
        email: document.getElementById('email').value.trim(),
        message: document.getElementById('message').value.trim()
    };

    const submitButton = document.querySelector('.send-button');
    const messageDiv = document.getElementById('formMessage');

    // Limpiar mensaje anterior
    messageDiv.textContent = '';
    messageDiv.className = '';

    try {
        submitButton.disabled = true;
        submitButton.textContent = '🔄 Enviando...';

        // URL de tu backend en Render/Vercel
        const backendUrl = 'https://porfolio-chop-code-solutions-brando.vercel.app/api/main'; // Cambia por tu URL

        const response = await fetch(backendUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (response.ok) {
            messageDiv.style.color = '#00ff00';
            messageDiv.className = 'success-message';
            messageDiv.innerHTML = '✅ ' + result.message;
            document.getElementById('contactForm').reset();
        } else {
            messageDiv.style.color = '#ff4444';
            messageDiv.className = 'error-message';
            messageDiv.innerHTML = '❌ ' + (result.detail || 'Error al enviar el mensaje');
        }
    } catch (error) {
        messageDiv.style.color = '#ff4444';
        messageDiv.className = 'error-message';
        messageDiv.innerHTML = '❌ Error de conexión. Intenta nuevamente.';
        console.error('Error:', error);
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = 'Ejecutar Envío (Enviar)';
    }
});