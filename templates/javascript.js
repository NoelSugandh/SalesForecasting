// Existing JavaScript code

function validateForm() {
    // Validation logic for registration form
    var fullName = document.getElementById("fullName").value;
    var username = document.getElementById("username").value;
    var email = document.getElementById("email").value;
    var password = document.getElementById("password").value;
    var confirmPassword = document.getElementById("confirmPassword").value;
    var phoneNumber = document.getElementById("phoneNumber").value;
    var dob = document.getElementById("dob").value;
    var gender = document.getElementById("gender").value;
    var agreeTerms = document.getElementById("agreeTerms").checked;

    // Add validation logic here

    if (!agreeTerms) {
        alert("Please agree to Terms and Conditions.");
        return false;
    }

    // If all validations pass, show success message
    showSuccessMessage();
    return true;
}

function showSuccessMessage() {
    var successMessage = document.getElementById("successMessage");
    successMessage.classList.remove("hidden");
}

function validateLoginForm() {
    // Validation logic for login form
    var usernameOrEmail = document.getElementById("usernameOrEmail").value;
    var loginPassword = document.getElementById("loginPassword").value;

    if (usernameOrEmail === "example@example.com" && loginPassword === "password") {
        showWelcomeMessage();
        return true; // Allow form submission
    } else {
        // Display error message for invalid credentials
        alert("Invalid username/email or password.");
        return false; // Prevent form submission
    }
}

function showWelcomeMessage() {
    var welcomeMessage = document.getElementById("welcomeMessage");
    welcomeMessage.classList.remove("hidden");
}
