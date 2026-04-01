async function loadImages() {
    try {
        const response = await fetch('/api/images');
        const images = await response.json();

        const container = document.getElementById('images-container');
        container.innerHTML = '';

        images.forEach(img => {
            const wrapper = document.createElement('div');
            wrapper.style.display = 'inline-block';
            wrapper.style.margin = '10px';
            wrapper.style.textAlign = 'center';

            const imageElement = document.createElement('img');
            imageElement.src = img.url;
            imageElement.style.width = '200px';
            imageElement.style.display = 'block';
            imageElement.style.marginBottom = '10px';

            const deleteButton = document.createElement('button');
            deleteButton.textContent = 'Delete';

            deleteButton.addEventListener('click', async () => {
                try {
                    const response = await fetch(`/delete?name=${encodeURIComponent(img.filename)}`, {
                        method: 'DELETE'
                    });

                    const result = await response.json();

                    if (result.success) {
                        loadImages();
                    } else {
                        alert(result.error || 'Delete error');
                    }
                } catch (error) {
                    alert('Network error while deleting');
                }
            });

            wrapper.appendChild(imageElement);
            wrapper.appendChild(deleteButton);
            container.appendChild(wrapper);
        });

    } catch (error) {
        console.error('Error loading images:', error);
    }
}

window.onload = loadImages;