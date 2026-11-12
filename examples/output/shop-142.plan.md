# Test plan: SHOP-142 - Apply a coupon code at checkout

12 scenarios covering 5 acceptance criteria (offline heuristic mode).

**Coverage:** accessibility: 1, edge: 2, negative: 3, positive: 5, security: 1

## Risks
- Generated without an LLM: review wording and add domain-specific cases.

## Scenarios

| ID | Title | Type | Priority | Level | Automate |
|---|---|---|---|---|---|
| TC-01 | Verify: Given a logged-in user with items in the cart, when they enter a vali… | positive | P0 | ui | yes |
| TC-02 | Verify: An expired or invalid code shows the message "Coupon is not valid" an… | positive | P1 | ui | yes |
| TC-03 | Negative path for: An expired or invalid code shows the message "Coupon is not valid" an… | negative | P1 | ui | yes |
| TC-04 | Verify: A coupon only applies when the cart subtotal is at least 499. | positive | P1 | ui | yes |
| TC-05 | Boundary values for: A coupon only applies when the cart subtotal is at least 499. | edge | P2 | api | yes |
| TC-06 | Negative path for: A coupon only applies when the cart subtotal is at least 499. | negative | P1 | ui | yes |
| TC-07 | Verify: Only one coupon can be applied per order. | positive | P1 | api | yes |
| TC-08 | Negative path for: Only one coupon can be applied per order. | negative | P1 | api | yes |
| TC-09 | Verify: The applied coupon can be removed with the "Remove" link and the tota… | positive | P1 | ui | yes |
| TC-10 | Idempotency: repeat the same action twice quickly | edge | P1 | api | yes |
| TC-11 | Unauthenticated access is blocked | security | P1 | api | yes |
| TC-12 | Keyboard and screen-reader access for new UI | accessibility | P2 | manual | no |

### TC-01: Verify: Given a logged-in user with items in the cart, when they enter a vali…
_Covers: Given a logged-in user with items in the cart, when they enter a valid code and click "Apply coupon", then the order total is reduced by the coupon discount._

**Preconditions**
- a logged-in user with items in the cart

**Steps**
1. they enter a valid code and click "Apply coupon"

**Expected**
- the order total is reduced by the coupon discount

### TC-02: Verify: An expired or invalid code shows the message "Coupon is not valid" an…
_Covers: An expired or invalid code shows the message "Coupon is not valid" and the total does not change._

**Preconditions**
- User is logged in

**Steps**
1. Perform the action described: An expired or invalid code shows the message "Coupon is not valid" an…

**Expected**
- An expired or invalid code shows the message "Coupon is not valid" and the total does not change.

### TC-03: Negative path for: An expired or invalid code shows the message "Coupon is not valid" an…
_Covers: An expired or invalid code shows the message "Coupon is not valid" and the total does not change._

**Steps**
1. Provide input that violates the rule

**Expected**
- Request is rejected with a clear, user-facing error
- No partial state is saved

### TC-04: Verify: A coupon only applies when the cart subtotal is at least 499.
_Covers: A coupon only applies when the cart subtotal is at least 499._

**Preconditions**
- User is logged in

**Steps**
1. Perform the action described: A coupon only applies when the cart subtotal is at least 499.

**Expected**
- A coupon only applies when the cart subtotal is at least 499.

### TC-05: Boundary values for: A coupon only applies when the cart subtotal is at least 499.
_Covers: A coupon only applies when the cart subtotal is at least 499._

**Steps**
1. Test the value just below, at, and just above each limit in the criterion

**Expected**
- Behaviour switches exactly at the stated limit

### TC-06: Negative path for: A coupon only applies when the cart subtotal is at least 499.
_Covers: A coupon only applies when the cart subtotal is at least 499._

**Steps**
1. Provide input that violates the rule

**Expected**
- Request is rejected with a clear, user-facing error
- No partial state is saved

### TC-07: Verify: Only one coupon can be applied per order.
_Covers: Only one coupon can be applied per order._

**Preconditions**
- User is logged in

**Steps**
1. Perform the action described: Only one coupon can be applied per order.

**Expected**
- Only one coupon can be applied per order.

### TC-08: Negative path for: Only one coupon can be applied per order.
_Covers: Only one coupon can be applied per order._

**Steps**
1. Provide input that violates the rule

**Expected**
- Request is rejected with a clear, user-facing error
- No partial state is saved

### TC-09: Verify: The applied coupon can be removed with the "Remove" link and the tota…
_Covers: The applied coupon can be removed with the "Remove" link and the total is restored._

**Preconditions**
- User is logged in

**Steps**
1. Perform the action described: The applied coupon can be removed with the "Remove" link and the tota…

**Expected**
- The applied coupon can be removed with the "Remove" link and the total is restored.

### TC-10: Idempotency: repeat the same action twice quickly

**Steps**
1. Send the same request twice concurrently

**Expected**
- Only one effect is applied
- Totals stay consistent

### TC-11: Unauthenticated access is blocked

**Steps**
1. Call the endpoint without a session or with an expired token

**Expected**
- 401/403 returned
- No data leaked in the response body

### TC-12: Keyboard and screen-reader access for new UI

**Steps**
1. Navigate the new elements with keyboard only
2. Inspect with a screen reader

**Expected**
- All controls reachable and labelled

## Locator contract

| Element | data-testid | Role |
|---|---|---|
| Apply coupon | `apply-coupon` | - |
| Coupon is not valid | `coupon-is-not-valid` | - |
| Remove | `remove` | - |
