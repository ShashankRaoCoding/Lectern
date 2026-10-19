# Lectern

Small Django app: log in, create textbooks, upload a `.pptx` to have an AI write a biology-textbook-style explainer (with Mermaid diagrams), and read it back.

## Run locally

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser      # this is your login (there is no sign-up page)
python manage.py runserver
```

Log in at http://127.0.0.1:8000/, open **Preferences**, paste your AI API key, then create a textbook and use **Add content**.

## Deploy on PythonAnywhere

1. Open a Bash console: `git clone` / upload this folder to `~/Lectern`.
2. `mkvirtualenv Lectern --python=python3.12 && pip install -r ~/Lectern/requirements.txt`
3. `cd ~/Lectern && python manage.py migrate && python manage.py createsuperuser && python manage.py collectstatic --noinput`
4. **Web** tab → *Add a new web app* → Manual configuration → same Python version.
   - Source code / working directory: `/home/<you>/Lectern`
   - Virtualenv: `/home/<you>/.virtualenvs/Lectern`
   - Static files: URL `/static/` → `/home/<you>/Lectern/staticfiles`
5. Edit the WSGI file:

```python
import os, sys
sys.path.insert(0, "/home/<you>/Lectern")
os.environ["DJANGO_SECRET_KEY"] = "<long random string>"
os.environ["DJANGO_DEBUG"] = "0"
os.environ["DJANGO_ALLOWED_HOSTS"] = "<you>.pythonanywhere.com"
os.environ["DJANGO_CSRF_ORIGINS"] = "https://<you>.pythonanywhere.com"
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

6. Reload the web app.

### Notes

- **Don't change `DJANGO_SECRET_KEY` later**: saved API keys are encrypted with a key derived from it.
- **Free accounts** can only reach allowlisted sites from server code; check that the AI provider's API host is on PythonAnywhere's allowlist, otherwise you'll see a connection error on upload.
- Generation runs inside the web request, in chunks of about 5 slides. Very large decks may hit the request timeout; split them into several uploads.
- Default provider is **Mistral** (`mistral-small-latest`, a cheap model that's fine for testing). Use a key from console.mistral.ai.
- Env vars: `Lectern_AI_PROVIDER` (`mistral` or `anthropic`) and `Lectern_AI_MODEL` (e.g. `mistral-medium-latest`, `mistral-large-latest`). Prompt and token limits are in `config/settings.py`.
- Provider code is in `textbooks/ai.py` (`PROVIDERS`); adding another is one small function.
