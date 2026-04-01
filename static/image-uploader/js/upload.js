const form = document.getElementById('upload-form');
const fileInput = document.getElementById('file-input');
const message = document.getElementById('message');
const uploadedUrlInput = document.getElementById('uploaded-url');
const copyBtn = document.getElementById('copy-btn');

form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const file = fileInput.files[0];

    if (!file) {
        message.textContent = 'Выберите файл';
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            const fullUrl = `${window.location.origin}${data.url}`;
            uploadedUrlInput.value = fullUrl;
            message.textContent = 'Успешно загружено';
        } else {
            message.textContent = data.error || 'Ошибка загрузки';
        }
    } catch (error) {
        message.textContent = 'Ошибка сети';
    }
});

copyBtn.addEventListener('click', async () => {
    if (!uploadedUrlInput.value) {
        message.textContent = 'Нет ссылки для копирования';
        return;
    }

    try {
        await navigator.clipboard.writeText(uploadedUrlInput.value);
        message.textContent = 'Ссылка скопирована';
    } catch (error) {
        message.textContent = 'Ошибка копирования';
    }
});