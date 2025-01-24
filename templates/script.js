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

    // Password strength regex pattern: At least 8 characters, one uppercase letter, one number, one special character
    var passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

    // Check if passwords match
    if (password !== confirmPassword) {
        alert("Passwords do not match.");
        return false;
    }

    // Check if password meets strength requirements
    if (!passwordPattern.test(password)) {
        alert("Password must be at least 8 characters long and contain at least one uppercase letter, one number, and one special character.");
        return false;
    }

    // Add your additional validation logic here for other fields

    if (!agreeTerms) {
        alert("Please agree to Terms and Conditions.");
        return false;
    }

    // If all validations pass, show success message and prevent form submission temporarily
    showSuccessMessage();

    // Prevent form submission temporarily
    return false;
}

// Function to show the success message
function showSuccessMessage() {
    var successMessage = document.getElementById("successMessage");
    successMessage.classList.remove("hidden");
    setTimeout(function(){
        successMessage.classList.add("hidden");
        // Allow form submission after the success message disappears
        document.getElementById("registrationForm").submit();
    }, 5000); // 5000 milliseconds = 5 seconds
}

function validateLoginForm() {
    var usernameOrEmail = document.getElementById("usernameOrEmail").value;
    var loginPassword = document.getElementById("loginPassword").value;

    // Regular expressions for email format and password strength
    var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    var passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

    // Validate email/username format
    if (!emailPattern.test(usernameOrEmail)) {
        alert("Invalid email or username format.");
        return false;
    }

    // Validate password format
    if (!passwordPattern.test(loginPassword)) {
        alert("Invalid password format. Password must be at least 8 characters long and contain at least one uppercase letter, one number, and one special character.");
        return false;
    }

    // If both email/username and password are in correct format, allow form submission
    return true;
}

// Function to handle form submission
document.getElementById("loginForm").onsubmit = function() {
    // Retrieve username from input field
    var username = document.getElementById("usernameOrEmail").value;

    // Store the username in session storage
    sessionStorage.setItem("username", username);
};

