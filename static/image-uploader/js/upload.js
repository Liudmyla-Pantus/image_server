document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file');
    const uploadBtn = document.getElementById('uploadBtn');
    const copyBtn = document.getElementById('copyBtn');
    const currentUpload = document.getElementById('currentUpload');
    const message = document.getElementById('message');
    const preview = document.getElementById('preview');

    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];

        if (!file) {
            preview.innerHTML = '';
            return;
        }

        const reader = new FileReader();
        reader.onload = function (e) {
            preview.innerHTML = `<img src="${e.target.result}" alt="preview" style="max-width: 250px; max-height: 250px;">`;
        };
        reader.readAsDataURL(file);
    });

    uploadBtn.addEventListener('click', async () => {
        const file = fileInput.files[0];

        if (!file) {
            message.textContent = 'Оберіть файл';
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
                currentUpload.value = fullUrl;
                message.textContent = 'Успішно завантажено';
            } else {
                message.textContent = data.error || 'Помилка завантаження';
            }
        } catch (error) {
            message.textContent = 'Помилка сервера';
        }
    });

    copyBtn.addEventListener('click', async () => {
        if (!currentUpload.value) {
            message.textContent = 'Немає посилання для копіювання';
            return;
        }

        try {
            await navigator.clipboard.writeText(currentUpload.value);
            message.textContent = 'Посилання скопійовано';
        } catch (error) {
            message.textContent = 'Не вдалося скопіювати';
        }
    });
});