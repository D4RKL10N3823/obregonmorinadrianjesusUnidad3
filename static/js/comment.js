document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('#comment-form');
    const commentInput = document.querySelector('#comment-input');
    const commentsContainer = document.querySelector('#comment-container');
    let lastTimestamp = window.initialTimestamp || 0;

    // Comentarios de forma asíncrona
    async function commentAsync() {
        try {
            // Realiza una petición GET al servidor solicitando comentarios nuevos desde el último timestamp
            const response = await fetch(`${window.location.pathname}?comment=1&after=${lastTimestamp}`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            const data = await response.json();
            // Si hay comentarios nuevos mostrarlos
            if (data.length > 0) {
                data.forEach(comment => {
                    if (comment.timestamp > lastTimestamp) {
                        lastTimestamp = comment.timestamp;

                        const commentDiv = document.createElement('div');
                        commentDiv.className = 'bg-[#11111F] p-4 rounded shadow-sm';

                        const header = document.createElement('div');
                        header.className = 'flex items-center mb-2';

                        const username = document.createElement('span');
                        username.className = 'text-[#FFBC0E] font-bold mr-2';
                        username.textContent = comment.user;

                        const date = document.createElement('span');
                        date.className = 'text-gray-400 text-sm';
                        date.textContent = comment.created_at;

                        const content = document.createElement('p');
                        content.className = 'text-white';
                        content.textContent = comment.comment;

                        header.appendChild(username);
                        header.appendChild(date);
                        commentDiv.appendChild(header);
                        commentDiv.appendChild(content);

                        commentsContainer.appendChild(commentDiv);
                        commentsContainer.scrollTop = commentsContainer.scrollHeight;
                    }
                });
            }
        } catch (err) {
            console.error('Error:', err);
            await new Promise(resolve => setTimeout(resolve, 2000));
        } finally {
            commentAsync();
        }
    }

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
    });

    // Envia el comentario solo presionando enter
    commentInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            form.requestSubmit();
        }
    });

    commentAsync();
});