const API_URL = "http://127.0.0.1:8000"; // Адреса вашого бекенду

document.getElementById("upload-link").addEventListener("click", showUploadForm);
document.getElementById("view-link").addEventListener("click", fetchPhotos);
document.getElementById("auth-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch(`${API_URL}/api/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams({
                username: username,
                password: password,
            }),
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem("access_token", data.access_token);
            localStorage.setItem("token_type", data.token_type);
            displayUserInfo(username);
        } else {
            alert("Invalid username or password");
        }
    } catch (error) {
        console.error("Error during login:", error);
    }
});

function displayUserInfo(username) {
    document.getElementById("username-display").textContent = username;
    document.getElementById("login-form").style.display = "none";
    document.getElementById("user-info").style.display = "block";
}

document.getElementById("logout-button").addEventListener("click", () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("token_type");
    document.getElementById("login-form").style.display = "block";
    document.getElementById("user-info").style.display = "none";
});


function showUploadForm() {
    const content = document.getElementById("content");
    content.innerHTML = `
        <form id="upload-form">
            <label for="photo">Choose a photo:</label>
            <input type="file" id="photo" name="photo" accept="image/*">
            <button type="submit">Upload</button>
        </form>
    `;

    const form = document.getElementById("upload-form");
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const fileInput = document.getElementById("photo");
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        const response = await fetch(`${API_URL}/upload`, {
            method: "POST",
            body: formData,
        });

        if (response.ok) {
            alert("Photo uploaded successfully!");
            fetchPhotos();
        } else {
            alert("Failed to upload photo.");
        }
    });
}

async function fetchPhotos() {
    const response = await fetch(`${API_URL}/photos`);
    const photos = await response.json();
    const content = document.getElementById("content");

    content.innerHTML = photos
        .map(
            (photo) => `
            <div>
                <img src="${photo.url}" alt="${photo.description}" width="200">
                <p>${photo.description}</p>
            </div>
        `
        )
        .join("");
}
async function fetchProtectedResource() {
    const token = localStorage.getItem("access_token");
    const tokenType = localStorage.getItem("token_type");

    const response = await fetch(`${API_URL}/api/protected-resource`, {
        headers: {
            Authorization: `${tokenType} ${token}`,
        },
    });

    if (response.ok) {
        const data = await response.json();
        console.log("Protected data:", data);
    } else {
        console.error("Access denied");
    }
}

document.getElementById("show-register-form").addEventListener("click", () => {
    document.getElementById("signup-form").style.display = "block";
    document.getElementById("login-form").style.display = "none";
    document.getElementById("show-register-form").style.display = "none";
    document.getElementById("show-login-form").style.display = "block";
});

document.getElementById("show-login-form").addEventListener("click", () => {
    document.getElementById("signup-form").style.display = "none";
    document.getElementById("login-form").style.display = "block";
    document.getElementById("show-register-form").style.display = "block";
    document.getElementById("show-login-form").style.display = "none";
});


document.getElementById("register-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("register-username").value;
    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;
    const confirmPassword = document.getElementById("register-confirm-password").value;

    if (password !== confirmPassword) {
        alert("Passwords do not match!");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/auth/signup`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password,
            }),
        });

        if (response.ok) {
            alert("Registration successful! You can now log in.");
            document.getElementById("signup-form").style.display = "none";
            document.getElementById("login-form").style.display = "block";
        } else {
            const error = await response.json();
            alert(`Registration failed: ${error.detail || "Unknown error"}`);
        }
    } catch (error) {
        console.error("Error during registration:", error);
    }
});
