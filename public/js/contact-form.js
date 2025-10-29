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

        // En desarrollo usa localhost, en producción usa la URL relativa
        const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        const apiUrl = isDevelopment 
            ? 'http://localhost:8000/api/contact'
            : '/api/contact';
        
        console.info('🎯 URL del backend:', apiUrl);
        console.info('📦 Datos a enviar:', formData);

        let response = null;
        try {
            console.info('🚀 Iniciando petición POST a:', apiUrl);
            const fetchOptions = {
                method: 'POST',
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Origin': window.location.origin
                },
                body: JSON.stringify(formData)
            };
            console.info('⚙️ Opciones de fetch:', fetchOptions);
            
            response = await fetch(apiUrl, fetchOptions);
            
            console.info(`Respuesta recibida desde ${apiUrl}:`, response.status, response.statusText);
            
            // Si es un error 500, intentamos obtener más detalles
            if (response.status === 500) {
                const errorData = await response.json();
                console.error('Detalles del error del servidor:', errorData);
                messageDiv.style.color = '#ff4444';
                messageDiv.className = 'error-message';
                messageDiv.innerHTML = `❌ Error del servidor: ${errorData.detail || errorData.message || 'Error desconocido'}`;
                return;
            }
        } catch (err) {
            console.error('Error en fetch a', apiUrl, err);
            messageDiv.style.color = '#ff4444';
            messageDiv.className = 'error-message';
            messageDiv.innerHTML = '❌ No se pudo conectar con el servidor. Revisa la consola para más detalles.';
            return;
        }
        // Intentar parsear JSON solo si el servidor responde JSON; si no, usar texto plano.
        let result;
        const contentType = response.headers.get('content-type') || '';
        if (contentType.includes('application/json')) {
            try {
                result = await response.json();
            } catch (err) {
                console.error('Error parseando JSON del servidor:', err);
                result = { message: 'Respuesta no válida del servidor', detail: '' };
            }
        } else {
            // Puede ser HTML de error o texto plano
            const text = await response.text();
            result = { message: text, detail: text };
        }

        if (response.ok) {
            messageDiv.style.color = '#00ff00';
            messageDiv.className = 'success-message';
            messageDiv.innerHTML = '✅ ' + (result.message || 'Mensaje enviado correctamente');
            document.getElementById('contactForm').reset();
        } else {
            messageDiv.style.color = '#ff4444';
            messageDiv.className = 'error-message';
            // Mostrar detalle si existe, sino texto genérico con status
            messageDiv.innerHTML = '❌ ' + (result.detail || result.message || ('Error ' + response.status));
            console.warn('Respuesta de error del servidor:', response.status, result);
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