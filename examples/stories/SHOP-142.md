# SHOP-142: Apply a coupon code at checkout

As a shopper, I want to apply a coupon code on the checkout page so that I get a discount on my order.

## Acceptance criteria
- Given a logged-in user with items in the cart, when they enter a valid code and click "Apply coupon", then the order total is reduced by the coupon discount.
- An expired or invalid code shows the message "Coupon is not valid" and the total does not change.
- A coupon only applies when the cart subtotal is at least 499.
- Only one coupon can be applied per order.
- The applied coupon can be removed with the "Remove" link and the total is restored.
