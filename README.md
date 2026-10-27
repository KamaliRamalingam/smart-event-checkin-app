# Smart Event Check-in App

A Flask web app for event check-in with QR codes, built with a full **GitLab DevSecOps pipeline**: linting, tests, security scanning and automated deployment checks.

**GitLab DevSecOps Flow Hackathon · March 2026 · Team of three**

Built by a team of Data Analyst students without a formal development background, exploring backend, frontend and deployment end to end.

## What the app does

- **Login** with session-based authentication
- **Events and attendees** served through a REST API
- **Check in** attendees with one click
- **QR codes** generated for each attendee

| Endpoint | Purpose |
|---|---|
| `GET /api/events` | List events |
| `GET /api/attendees` | List attendees |
| `POST /api/checkin/<id>` | Check in an attendee |
| `GET /api/qrcode/<id>` | Generate an attendee's QR code |

## The DevSecOps pipeline

The project was built around GitLab CI/CD ([`.gitlab-ci.yml`](.gitlab-ci.yml)). Every push runs:

| Stage | What it checks |
|---|---|
| **Build** | Installs dependencies |
| **Lint** | Code style with flake8 |
| **Test** | pytest suite ([`test_app.py`](test_app.py)) |
| **Security** | Bandit, GitLab SAST and secret detection (including a scan of the full history) |
| **DAST** | Dynamic security scan of the deployed app |
| **Deploy** | Verifies the deployed app on Render responds correctly |

The pipeline runs on GitLab. On GitHub the file is included for reference.

## Run it locally

```bash
pip install -r requirements.txt
python app.py
```

Demo logins (`admin`, `user`, `demo`) use default passwords for local testing only. Set `SECRET_KEY` and the `*_PASSWORD` environment variables for any real deployment.

Run the tests with `pytest`. The test suite also covers features planned in [`FEATURES.md`](FEATURES.md), such as CSV export and event creation, which this version of the app doesn't include yet.

## Built with

Python · Flask · qrcode · pytest · flake8 · Bandit · GitLab CI/CD · SAST · DAST · Render
