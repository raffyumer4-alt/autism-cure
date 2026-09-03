AUTISM CURE — FINAL BUILD
========================

RUN LOCALLY
-----------
1. Python 3.11+
2. pip install -r requirements.txt
3. Set ADMIN_USERNAME, ADMIN_PASSWORD and SECRET_KEY.
4. python app.py
5. Open http://127.0.0.1:5000

RENDER
------
Build command:
  pip install -r requirements.txt

Start command:
  gunicorn app:app

Required environment variables:
  SECRET_KEY = a long random secret
  ADMIN_USERNAME = your admin username
  ADMIN_PASSWORD = a strong admin password
  DATABASE_PATH = persistent database path / PostgreSQL connection as implemented

IMPORTANT PRODUCTION NOTES
--------------------------
- Do NOT leave ADMIN_PASSWORD blank in production.
- Use PostgreSQL (or another persistent managed database) rather than Render's ephemeral filesystem for real patient data.
- Enable HTTPS.
- Add proper privacy policy, terms, consent, data retention/deletion, export and access controls before collecting real health information.
- Have all patient-facing therapeutic content reviewed by qualified autism/developmental professionals before clinical deployment.
- The app is a support/learning tool, not a diagnostic service, medical prescriber, or guaranteed cure.

PRODUCT PRINCIPLES
------------------
- Short sessions and visible progress.
- Patient/caregiver choice rather than forced long tasks.
- Age/ability and support-needs personalization.
- Practice data is retained across subscription renewal.
- Medication questions are redirected to qualified clinicians.
- Weekly reports describe app practice/observations, not a medical diagnosis.
