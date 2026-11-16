# User accounts

`CustomUser` stores account credentials and all public profile fields. The
`users` app uses a two-step signup:

1. Register with a phone number and a 4-digit PIN.
2. Complete the public profile. `OnboardingMiddleware` redirects authenticated
   users who have not finished this step.

The PIN is stored using Django's password hashers; it is never stored in
plaintext. After changing `AUTH_USER_MODEL` in an existing deployment, back up
the database and run `python manage.py migrate`. The migration copies profile
data onto each user, then removes the separate profile table. Existing accounts
can sign in once with their old credential and must choose a PIN during
onboarding.

For the Render superuser command, configure `RENDER_ADMIN_PHONE` and
`RENDER_ADMIN_PIN` as environment variables. The PIN must be exactly four
digits. Because a 4-digit PIN has a small search space, production deployments
should also enforce login throttling using a shared cache or authentication
rate-limiting service.
