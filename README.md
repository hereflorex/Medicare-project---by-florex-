# MediCare -FLOREX 🪄

A rebuilt Flask + SQLAlchemy hospital management project with a modern responsive UI.

## Included

- Patient and Doctor registration/login
- Password hashing and server-side sessions
- User-specific dashboard and profile
- Doctor search and availability
- Appointment booking, rescheduling, cancellation and doctor completion
- Digital prescriptions
- Appointment-linked billing
- Responsive mobile layout
- System/dark/light theme cycle
- Toast notifications, loaders, modals and micro animations
- PostgreSQL on Railway or SQLite fallback for local testing

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Open `http://localhost:5000`.

If `DATABASE_URL` is not set, the app uses a local SQLite file named `medicare.db`. For Railway/PostgreSQL, set `DATABASE_URL` and a strong `SECRET_KEY`.

## Important

This is a college/demo hospital-management project. The payment endpoint marks an invoice as paid for demo workflow; it is **not** a real payment gateway. Do not use this demo as a production medical system without proper security, privacy, audit, backups and compliance work.
