<script>
document.addEventListener('DOMContentLoaded', function() {
    fetchPhotos();

    async function fetchPhotos() {
        try {
            const response = await fetch('/photos');
            const photos = await response.json();
            const gallery = document.querySelector('.gallery');
            photos.forEach(photo => {
                const photoElement = document.createElement('div');
                photoElement.className = 'photo';
                photoElement.innerHTML = `<img src="${photo.url}" alt="${photo.description}">`;
                gallery.appendChild(photoElement);
            });
        } catch (error) {
            console.error('Error fetching photos:', error);
        }
    }
});
</script>