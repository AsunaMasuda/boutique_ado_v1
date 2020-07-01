/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment
    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

// get public and client key
var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);
// we need to do to set up stripe is create a variable using our stripe public key.
var stripe = Stripe(stripePublicKey);
// create an instance of stripe elements
var elements = stripe.elements();
/*  get some basic styles from the stripe js Docs. 
    but match base color(#000) and invalid color(#dc3545) to match the bootstrap*/
var style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};
// create a card element
var card = elements.create('card', {style: style});
// mount
card.mount('#card-element');

// Handle realtime validation errors on the card element
// every time it changes we'll check to see if there are any errors.
card.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card-errors');
    // If so we'll display them in the card errors div we created near the card element on the checkout page.
    if (event.error) {
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
    } else {
        errorDiv.textContent = '';
    }
});

// Handle form submit
var form = document.getElementById('payment-form');

form.addEventListener('submit', function(ev) {
    // Prevent default action which in our case is to post
    ev.preventDefault();
    // disable both the card element and the submit button to prevent multiple submissions.
    card.update({ 'disabled': true});
    $('#submit-button').attr('disabled', true);
    stripe.confirmCardPayment(clientSecret, {
        payment_method: {
            card: card,
        }
    }).then(function(result) { //then execute this function on the result.
        if (result.error) { // we'll display them in the card errors div
            var errorDiv = document.getElementById('card-errors');
            var html = `
                <span class="icon" role="alert">
                <i class="fas fa-times"></i>
                </span>
                <span>${result.error.message}</span>`;
            $(errorDiv).html(html);
            card.update({ 'disabled': false}); //if there is an error, We'll also want to re-enable the card element
            $('#submit-button').attr('disabled', false); // and the submit button to allow the user to fix it.
        } else {
            if (result.paymentIntent.status === 'succeeded') {
                form.submit(); // If the status of the payment intent comes back is succeeded we'll submit the form.
            }
        }
    });
});