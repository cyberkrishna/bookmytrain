// Toggle forms
document.getElementById("toggleToSignup").addEventListener("click", (e) => {
  e.preventDefault();
  document.getElementById("loginForm").style.display = "none";
  document.getElementById("signupForm").style.display = "block";
  document.getElementById("formTitle").textContent = "Sign Up";
});

document.getElementById("toggleToLogin").addEventListener("click", (e) => {
  e.preventDefault();
  document.getElementById("signupForm").style.display = "none";
  document.getElementById("loginForm").style.display = "block";
  document.getElementById("formTitle").textContent = "Login";
});

// Validation rules
function validateUsername(username) {
  return /^[a-zA-Z0-9]{4,}$/.test(username); // Alphanumeric, at least 4 characters
}

function validatePassword(password) {
  return password.length >= 6; // At least 6 characters
}

function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email); // Basic email format
}

// Handle login form submission
document.getElementById("loginForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const username = document.getElementById("loginUsername").value;
  const password = document.getElementById("loginPassword").value;
  let valid = true;

  // Username validation
  if (!validateUsername(username)) {
    document.getElementById("loginUsernameError").textContent = "Username must be alphanumeric and at least 4 characters.";
    valid = false;
  } else {
    document.getElementById("loginUsernameError").textContent = "";
  }

  // Password validation
  if (!validatePassword(password)) {
    document.getElementById("loginPasswordError").textContent = "Password must be at least 6 characters.";
    valid = false;
  } else {
    document.getElementById("loginPasswordError").textContent = "";
  }

  if (valid) {
    alert("Login successful!"); // Placeholder for actual login process
  }
});

// Handle signup form submission
document.getElementById("signupForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const username = document.getElementById("signupUsername").value;
  const password = document.getElementById("signupPassword").value;
  const email = document.getElementById("signupEmail").value;
  let valid = true;

  // Username validation
  if (!validateUsername(username)) {
    document.getElementById("signupUsernameError").textContent = "Username must be alphanumeric and at least 4 characters.";
    valid = false;
  } else {
    document.getElementById("signupUsernameError").textContent = "";
  }

  // Password validation
  if (!validatePassword(password)) {
    document.getElementById("signupPasswordError").textContent = "Password must be at least 6 characters.";
    valid = false;
  } else {
    document.getElementById("signupPasswordError").textContent = "";
  }

  // Email validation
  if (!validateEmail(email)) {
    document.getElementById("signupEmailError").textContent = "Please enter a valid email.";
    valid = false;
  } else {
    document.getElementById("signupEmailError").textContent = "";
  }

  if (valid) {
    alert("Signup successful!"); // Placeholder for actual signup process
  }
});
