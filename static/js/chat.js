document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('#message-form');
    const messageInput = document.querySelector('#id_message');
    const chatBox = document.querySelector('#chat-box');
    const conversationId = JSON.parse(document.getElementById('conversationId').textContent);
    let lastTimestamp = 0;

    // Renderiza los mensajes enviados
    function renderMessage(msg) {
        const wrapper = document.createElement('div');
        wrapper.className = `flex ${msg.is_user ? 'justify-end' : 'justify-start'}`;
        wrapper.innerHTML = `
            <div class="flex items-end gap-2 max-w-[70%]">
                ${!msg.is_user ? `<img src="${msg.icon}" class="w-8 h-8 rounded-full object-cover">` : ''}
                <div class="${msg.is_user ? '[background-color:#FFBC0E] text-black' : 'bg-gray-800 text-white'} p-3 rounded-lg ${msg.is_user ? 'rounded-br-none' : 'rounded-bl-none'}">
                    ${!msg.is_user ? `<strong>${msg.sender}</strong>:` : ''} ${msg.message}
                    <br><small class="text-xs">${msg.created_at}</small>
                </div>
                ${msg.is_user ? `<img src="${msg.icon}" class="w-8 h-8 rounded-full object-cover">` : ''}
            </div>
        `;
        chatBox.appendChild(wrapper);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Chat asíncrono 
    let pollingTimeout = null;
    async function chatAsync() {
        try {
            const response = await fetch(`${window.location.pathname}?message=1&after=${lastTimestamp}`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            if (response.status === 403 || response.status === 404) {
                console.warn('Conversación no encontrada o acceso denegado.');
                return;
            }

            const data = await response.json();
            if (data.length > 0) {
                data.forEach(msg => {
                     if (msg.timestamp > lastTimestamp) {
                        lastTimestamp = msg.timestamp;
                        renderMessage(msg);
                    }
                });
            }
        } catch (err) {
            console.error('Error:', err);
            await new Promise(resolve => setTimeout(resolve, 2000));
        } finally {
            pollingTimeout = setTimeout(chatAsync, 500); 
        }
    }

    chatAsync();

    // Limpieza automática si el usuario sale
    window.addEventListener('beforeunload', () => {
        clearTimeout(pollingTimeout);
    });

    // Envia el formulario de forma asíncrona
    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        const formData = new FormData(form);
        await fetch(window.location.href, {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            body: formData,
        });
        form.reset();
        await chatAsync();
    });

    // Envia el mensaje solo presionando enter
    messageInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            form.requestSubmit();
        }
    });
});