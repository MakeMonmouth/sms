// static/sms_stripe.js

console.log("Loading Stripe for SMS");

// Get Stripe publishable key
fetch("/memberships/config/")
.then((result) => { return result.json(); })
.then((data) => {
  // Initialize Stripe.js
  const stripe = Stripe(data.publicKey);

 // Event handler
  document.querySelector("button").addEventListener("click", () => {
    // Get Checkout Session ID
    fetch("/memberships/create-checkout-session/")
    .then((result) => { return result.json(); })
    .then((data) => {
      console.log(data);
      // Redirect to Stripe Checkout
      return stripe.redirectToCheckout({sessionId: data.sessionId})
    })
    .then((res) => {
      console.log(res);
    });
  });
});
