const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

function loadJson(selector) {
  return JSON.parse(document.querySelector(selector).getAttribute('data-json'));
}

var jsonData = loadJson('#jsonData');
var STRIPE_PUBLISHABLE_KEY = jsonData.STRIPE_PUBLISHABLE_KEY;
var order_id = jsonData.order_id;
console.log(STRIPE_PUBLISHABLE_KEY)
console.log(order_id)
// Создайте экземпляр объекта Stripe с вашим доступным для публикации ключом API.
var stripe = Stripe(STRIPE_PUBLISHABLE_KEY);
var checkoutButton = document.getElementById("checkout-button");
checkoutButton.addEventListener("click", function () {
  fetch('/pay/create_session/' + order_id, {
    method: "GET",
    headers: {
        'X-CSRFToken': csrftoken
    }
  })
    .then(function (response) {
      return response.json();
    })
    .then(function (session) {
      return stripe.redirectToCheckout({ sessionId: session.id });
    })
    .then(function (result) {
      if (result.error) {
        alert(result.error.message);
      }
    })
    .catch(function (error) {
      console.error("Error:", error);
    });
});