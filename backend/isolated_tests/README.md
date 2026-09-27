# Isolated checkout tests

Run from `backend`:

```powershell
python -m pytest isolated_tests --confcutdir=isolated_tests -q
```

This suite overrides `DATABASE_URL` and `TEST_DATABASE_URL` before importing the
application, uses a temporary SQLite file per test, and exercises the real cart,
payment and receipt routes with signed authentication tokens. It creates only
test fixtures, without importing `scripts.seed`, running migrations, or loading
`tests/conftest.py` (which otherwise uses the configured PostgreSQL database).

It covers mock purchase/confirmation, receipt issuance, sequential idempotent
retries, pending/declined/timeout states, gateway errors, ownership and staff
branch permissions. SQLite does not verify PostgreSQL row-lock concurrency.

CI runs this command automatically in its own step and Python process, separate
from the legacy PostgreSQL suite. Frontend checkout/cart regressions also run in
Chrome Headless in the frontend job.

Recovery tests cover a lost purchase response, validation before sale creation,
and a sale created before a gateway failure. New web purchases send a UUID
`checkout_token`; its URL-safe encoding identifies the sale through the existing
unique `invoice_number` (`WEB-...`, 26 characters). No schema migration is needed.
`GET /cart/purchase/{checkout_token}` retrieves only the authenticated owner's
sale. Repeating POST with that token returns the same sale, including when the
cart is already empty or payment creation has not finished. A missing payment
keeps recovery pending; it must not cause another sale. A 404 lookup only enables
retrying the same token, never assumes an in-flight request could not have run.
