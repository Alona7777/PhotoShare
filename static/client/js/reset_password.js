document.getElementById("resetPasswordBtn").addEventListener("click", sendResetPasswordRequest);

function sendResetPasswordRequest(event) {
    event.preventDefault();
    let emailInput = document.getElementById("resetPasswordForm").elements["email"];
    let emailValue = emailInput.value;
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/auth/reset-password", true);
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                setTimeout(function () {
                    emailInput.value = "";
                    window.location.href = "/api/auth/reset-password/done_request";
                }, 100);
            } else {
                handleErrorResponse(xhr);
            }
        }
    };

    let data = JSON.stringify({ "email": emailValue });
    xhr.send(data);
}

function handleErrorResponse(xhr) {
    console.error("Request failed with status:", xhr.status);
    switch (xhr.status) {
        case 401:
            alert("Check your email for confirmation");
            break;
        case 404:
            alert("Unknown email");
            break;
        default:
            alert("An unexpected error occurred. Please try again later");
            break;
    }

}