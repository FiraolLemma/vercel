# Local and Vercel deployment

## Local development

From the `project/` directory, copy the example environment file and install
the Python dependencies:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Replace the example `SECRET_KEY` before using the app beyond local development.
Local development uses SQLite and stores uploads in `media/`. Redis is only
needed for Channels features such as chat.

## Vercel deployment

Set Vercel's **Root Directory** to `project`. Vercel detects the Django
application and collects static files automatically; no custom build or start
command is needed. The ASGI function serves HTTP and Channels WebSockets.

Before deploying, add the required values under **Project Settings >
Environment Variables** in Vercel and enable them for every environment you
deploy (at least Production, and Preview if you use preview deployments).
Vercel reads Django settings during its build, so these variables must be
available to the build as well as the running function. A local `.env` file is
not uploaded as Vercel configuration.

In particular, the reported `DATABASE_URL is required on Vercel` error means
`DATABASE_URL` is missing from the selected Vercel environment. Add the
connection URL for your persistent PostgreSQL database, then redeploy. Do not
replace it with SQLite: Vercel's function filesystem is ephemeral.

Set these variables:

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | A new, long, random Django secret. |
| `DEBUG` | Set to `false` (Django also forces it off on Vercel). |
| `DATABASE_URL` | Persistent PostgreSQL connection URL. |
| `REDIS_URL` | Managed Redis URL for Django Channels (`rediss://` if required). |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name for persistent uploads. |
| `CLOUDINARY_API_KEY` | Cloudinary API key. |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret. |

Vercel supplies `VERCEL_URL`; Django adds it to allowed hosts and CSRF trusted
origins. For a custom domain, set `ALLOWED_HOSTS` to its hostname and
`CSRF_TRUSTED_ORIGINS` to its full `https://` origin. Separate multiple values
with commas.

The database, Redis, and Cloudinary credentials are required on Vercel because
its function filesystem is ephemeral. Apply database migrations before serving
traffic. For example, pull Vercel environment variables locally, then run:

```powershell
python manage.py migrate
```

Keep `.env` and `.env.local` private; neither should be committed. To run with
Vercel's local emulator, pull environment variables into `.env.local`, then
run `vercel dev`.

The `worker` process in `Procfile` is not started by Vercel. Run background
workers as a separate persistent service if your deployment needs them.
