# Test plan: AUTH-77 - Lock account after repeated failed logins

6 scenarios covering 3 acceptance criteria (offline heuristic mode).

**Coverage:** accessibility: 1, edge: 1, positive: 3, security: 1

## Risks
- Generated without an LLM: review wording and add domain-specific cases.

## Scenarios

| ID | Title | Type | Priority | Level | Automate |
|---|---|---|---|---|---|
| TC-01 | Verify: After 5 failed login attempts within 15 minutes the account is locked. | positive | P0 | api | yes |
| TC-02 | Boundary values for: After 5 failed login attempts within 15 minutes the account is locked. | edge | P2 | api | yes |
| TC-03 | Verify: A locked user sees the message "Account locked" on the login page. | positive | P1 | ui | yes |
| TC-04 | Verify: A successful login resets the failed attempt counter. | positive | P1 | api | yes |
| TC-05 | Unauthenticated access is blocked | security | P1 | api | yes |
| TC-06 | Keyboard and screen-reader access for new UI | accessibility | P2 | manual | no |

### TC-01: Verify: After 5 failed login attempts within 15 minutes the account is locked.
_Covers: After 5 failed login attempts within 15 minutes the account is locked._

**Preconditions**
- User is logged in

**Steps**
1. Perform the action described: After 5 failed login attempts within 15 minutes the account is locked.

**Expected**
- After 5 failed login attempts within 15 minutes the account is locked.

### TC-02: Boundary values for: After 5 failed login attempts within 15 minutes the account is locked.
_Covers: After 5 failed login attempts within 15 minutes the account is locked._

**Steps**
1. Test the value just below, at, and just above each limit in the criterion

**Expected**
- Behaviour switches exactly at the stated limit

### TC-03: Verify: A locked user sees the message "Account locked" on the login page.
_Covers: A locked user sees the message "Account locked" on the login page._

**Preconditions**
- User is logged in

**Steps**
1. Perform the action described: A locked user sees the message "Account locked" on the login page.

**Expected**
- A locked user sees the message "Account locked" on the login page.

### TC-04: Verify: A successful login resets the failed attempt counter.
_Covers: A successful login resets the failed attempt counter._

**Preconditions**
- User is logged in

**Steps**
1. Perform the action described: A successful login resets the failed attempt counter.

**Expected**
- A successful login resets the failed attempt counter.

### TC-05: Unauthenticated access is blocked

**Steps**
1. Call the endpoint without a session or with an expired token

**Expected**
- 401/403 returned
- No data leaked in the response body

### TC-06: Keyboard and screen-reader access for new UI

**Steps**
1. Navigate the new elements with keyboard only
2. Inspect with a screen reader

**Expected**
- All controls reachable and labelled

## Locator contract

| Element | data-testid | Role |
|---|---|---|
| Account locked | `account-locked` | - |
