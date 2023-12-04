document.addEventListener("DOMContentLoaded", function () {
    const darkModeButton = document.getElementById("toggle-mode");
    const body = document.body;
    const loading = document.getElementById("loading");
    const message = document.getElementById("message");

    darkModeButton.addEventListener("click", function () {
        body.classList.toggle("dark-mode");
    });

    const signupButton = document.getElementById("signup-button");
    signupButton.addEventListener("click", function () {
        // Disable the signup button during loading
        signupButton.disabled = true;
        
        // Simulate a loading state with a delay
        loading.style.display = "block";
        message.style.display = "none";
        setTimeout(function () {
            loading.style.display = "none";
            message.style.display = "block";
            message.textContent = "Successfully created account!";
            
            // Enable the signup button after the message
            signupButton.disabled = false;
        }, 5000); // 5 seconds
    });
});
