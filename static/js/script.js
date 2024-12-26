const API_BASE = 'http://127.0.0.1:8000';
let currentPage = 0;
const limit = 10;

// login
async function loginUser(event) {
    event.preventDefault();

    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    try {
        const response = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData.toString(),
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('accessToken', data.access_token);
            alert('Login successful!');
            window.location.href = '/';
        } else {
            const error = await response.json();
            alert(`Login failed: ${error.detail}`);
        }
    } catch (error) {
        console.error('Error during login:', error);
        alert('An error occurred. Please try again.');
    }
}

// registration
async function signupUser(event) {
    event.preventDefault();

    const username = document.getElementById('signup-username').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;

    try {
        const response = await fetch(`${API_BASE}/api/auth/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password,
            }),
        });

        if (response.ok) {
            alert('Signup successful! Redirecting to login page...');
            console.log('Redirecting to /auth...');
            window.location.href = '/auth';
        } else {
            const error = await response.json();
            console.error('Signup error:', error);
            alert(`Signup failed: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error during signup:', error);
        alert('An error occurred. Please try again.');
    }
}

// upload photo
async function uploadPhoto(event) {
    event.preventDefault();

    const token = localStorage.getItem('accessToken');
    if (!token) {
        alert('You must be logged in to upload photos.');
        window.location.href = '/auth';
        return;
    }

    const title = document.getElementById('photo-title').value;
    const description = document.getElementById('photo-description').value;
    const file = document.getElementById('photo-file').files[0];

    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE}/api/photos/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
            body: formData,
        });

        if (response.ok) {
            alert('Photo uploaded successfully!');
            window.location.href = '/';
        } else {
            const error = await response.json();
            alert(`Upload failed: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error uploading photo:', error);
        alert('An error occurred. Please try again.');
    }
}

// upload all photos
async function loadPhotos(skip = 0, limit = 10) {
    const gallery = document.getElementById('photo-gallery');
    gallery.innerHTML = '<p>Loading photos...</p>';

    try {
        const response = await fetch(`${API_BASE}/api/photos/all?skip=${skip}&limit=${limit}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
            },
        });

        if (response.ok) {
            const photos = await response.json();
            gallery.innerHTML = '';

            if (photos.length === 0 && skip === 0) {
                gallery.innerHTML = '<p>No photos available.</p>';
                return;
            }

            if (photos.length === 0) {
                document.getElementById('next-page').disabled = true;
                return;
            }

            photos.forEach(photo => {
                const photoCard = document.createElement('div');
                photoCard.className = 'photo-card';

                photoCard.innerHTML = `
                    <img src="${photo.file_path.startsWith('http') ? photo.file_path : `${API_BASE}${photo.file_path}`}"
                         alt="${photo.title}"
                         class="photo-img">
                    <h3>${photo.title}</h3>
                    <p>${photo.description}</p>
                `;

                gallery.appendChild(photoCard);
            });

            document.getElementById('prev-page').disabled = skip === 0;
            document.getElementById('next-page').disabled = photos.length < limit;
        } else {
            const error = await response.json();
            gallery.innerHTML = `<p>Error loading photos: ${error.detail || 'Unknown error'}</p>`;
        }
    } catch (error) {
        console.error('Error loading photos:', error);
        gallery.innerHTML = '<p>An error occurred while loading photos.</p>';
    }
}

// pagination
document.getElementById('prev-page').addEventListener('click', () => {
    if (currentPage > 0) {
        currentPage--;
        loadPhotos(currentPage * limit, limit);
    }
});

document.getElementById('next-page').addEventListener('click', () => {
    currentPage++;
    loadPhotos(currentPage * limit, limit);
});
