let currentStep = 1;

document.getElementById("nextStep").addEventListener("click", () => {
  if (currentStep === 1) {
    // Move to journey confirmation
    document.querySelector(".payment-container").innerHTML = `
      <h2>Confirm Journey Details</h2>
      <p>Train: Rajdhani Express</p>
      <p>Date: 2024-12-25</p>
      <p>Seat: S2-15</p>
      <button id="nextStep">Proceed to Payment</button>
    `;
    currentStep++;
  } else if (currentStep === 2) {
    // Move to payment form
    document.querySelector(".payment-container").innerHTML = `
      <h2>Payment</h2>
      <label for="cardNumber">Card Number:</label>
      <input type="text" id="cardNumber" required>
      <button id="payNow">Pay Now</button>
    `;
  }
});
