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

        // Usar ruta relativa primaria; si falla (405 o no responde), probamos fallbacks y mostramos logs.
        // Ajusta o elimina los fallbacks si sabes la URL final en producción.
        const candidateUrls = [
            '/api/contact',       // ruta esperada
            '/api/main.py',       // ruta que Vercel a veces expone
            '/contact',           // prueba por si la petición está llegando sin /api
        ];

        let response = null;
        let lastError = null;

        for (const url of candidateUrls) {
            try {
                console.info('Intentando enviar formulario a:', url);
                response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                // Log básico
                console.info(`Respuesta recibida desde ${url}:`, response.status, response.statusText);

                // Si recibimos 405 intentamos el siguiente fallback
                if (response.status === 405) {
                    lastError = { url, status: response.status };
                    console.warn('405 recibido en', url, '- probando siguiente fallback.');
                    response = null;
                    continue; // intentar siguiente url
                }

                // Si hay respuesta (no 405), salimos del loop y la procesamos
                break;
            } catch (err) {
                lastError = { url, error: err };
                console.error('Error enviando a', url, err);
                response = null;
                // intentar siguiente url
            }
        }

        if (!response) {
            // Ningún endpoint respondió correctamente
            messageDiv.style.color = '#ff4444';
            messageDiv.className = 'error-message';
            messageDiv.innerHTML = '❌ No se pudo conectar con el servidor (probé varios endpoints). Revisa la consola para más detalles.';
            console.error('Fallaron todos los intentos. Último error/fallback:', lastError);
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