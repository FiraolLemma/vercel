# Deploying to Vercel

Vercel runs this Django project as an ASGI function. The project is in the
`project/` directory, so set Vercel's **Root Directory** to `project` when
importing the repository. No custom build or start command is needed; Vercel
detects `manage.py` and collects static files during the build.

## Required environment variables

Set these for every Vercel environment you deploy (Production, Preview, and
Development):

| Variable | Value |
| --- | --- |
| `SECRET_KEY` | A new, long, random Django secret. |
| `DEBUG` | `false` |
| `DATABASE_URL` | A persistent PostgreSQL connection URL. SQLite is only used locally; Vercel's filesystem is not persistent. |
| `REDIS_URL` | A Redis connection URL for Django Channels (use `rediss://` when required by your provider). |
| `CLOUDINARY_CLOUD_NAME` | Your Cloudinary cloud name. |
| `CLOUDINARY_API_KEY` | Your Cloudinary API key. |
| `CLOUDINARY_API_SECRET` | Your Cloudinary API secret. |

`VERCEL_URL` is supplied by Vercel and is added to Django's allowed hosts and
CSRF trusted origins automatically. If you use a custom domain, add it to
`ALLOWED_HOSTS` (hostname only) and `CSRF_TRUSTED_ORIGINS` (full `https://`
origin), separated by commas.

The Cloudinary variables enable durable media uploads. Without them, uploads
would be lost when a serverless function instance is recycled. Redis backs
Channels; configure a managed Redis service to keep chat and other channel
features working across function instances.

## Database setup

Create the PostgreSQL database before deploying and set `DATABASE_URL` in
Vercel. Apply migrations against that database before serving traffic. For
example, pull the environment variables locally with the Vercel CLI, then run:

```shell
python manage.py migrate
```

Keep the pulled environment file local; never commit secrets.

## Local development

The local SQLite fallback is unchanged. For Vercel CLI development, pull
environment variables into `.env.local` and run:

```shell
vercel dev
```

The `worker` process in `Procfile` is not started by Vercel. If you rely on
background workers, run them as a separate persistent service.
