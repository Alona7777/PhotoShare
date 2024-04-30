# REST API Documentation for the "PhotoShare" Application

    Introduction
The "PhotoShare" application allows users to upload, view, and comment on photos. The API is developed using the
FastAPI framework, ensuring fast and efficient handling of HTTP requests.

    Authentication
Authentication in the "PhotoShare" API is managed through tokens issued following successful user login.
The process involves the following steps:

    User Registration:
POST /users/register
Fields: username, password, email
Result: Confirmation of successful registration or validation errors.
Login:
POST /users/login
Fields: username, password
Result: Authentication token, used to authorize subsequent requests.
    
    Photo Management
The application provides the ability to upload new photos, view existing ones, and delete them.
Each operation requires authentication.

Uploading a Photo:
POST /photos
The request must include multipart/form-data with the photo file.
Result: URL of the uploaded photo and information about it.
Viewing a Photo:
GET /photos/{photo_id}
Result: Details of the photo and URL for viewing.
Deleting a Photo:
DELETE /photos/{photo_id}
Result: Confirmation of successful deletion or an error if the photo is not found or the user lacks rights to it.
    
    Commenting
Commenting allows users to interact with photos through text comments.

    Adding a Comment:
POST /photos/{photo_id}/comments
Fields: text
Result: Details of the added comment.
Viewing Comments on a Photo:
GET /photos/{photo_id}/comments
Result: List of all comments on the photo.
Deleting a Comment:
DELETE /comments/{comment_id}
Result: Confirmation of successful deletion or an error if the comment is not found.
    
# Conclusion
The "PhotoShare" API uses REST standards to ensure simplicity and convenience in interactions.
With the speed and reliability of FastAPI, "PhotoShare" serves as an effective tool for photo sharing and user
communication.

# Get started

1) Clone repository:

    ```https://github.com/Alona7777/Project-TEAM_1.git```

2) Activate Poetry environment:

    ```poetry shell```

3) Install packages:

    ```poetry install```

4) Run docker compose:
    ```docker compose up -d```

5) Run migrations:
    ```alembic upgrade heads```

6) Run main.py