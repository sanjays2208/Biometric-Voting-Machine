# Integrated Biometric Electronic Voting Machine (BVM) — Academic Demo

Runnable Flask + SQLite simulation for demo voter authentication, ballot recording, a separate eligibility/ballot data model, a basic hash-chain integrity check, and an aggregate dashboard.

## Important
This is an educational software simulation. It does **not** capture fingerprints or faces and is **not** suitable for real elections. It does not prove biometric accuracy, ballot anonymity, or election-grade security.

## Run
Requires Python 3.10+.
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000. Demo accounts: `DEMO001 / 1234`, `DEMO002 / 5678`. Delete `instance/bvm.sqlite3` to reset the local demo database.

## Features
- Synthetic ID/PIN authentication and one-vote-per-demo-account control
- Candidate selection, local SQLite ballot storage and confirmation page
- Eligibility/participation table separated from ballot-choice table
- Dashboard showing aggregate counts, events and basic SHA-256 hash-chain check
- Responsive HTML/CSS, sample data, architecture document and MIT license

## Files
`app.py` contains routes and database logic; `templates/` contains UI pages; `static/style.css` contains styling; `docs/ARCHITECTURE.md` explains the data flow; `sample_data/voters.csv` contains synthetic data.

## Publish to GitHub
Create an empty repository on GitHub, then run these commands from this folder:
```bash
git init
git add .
git commit -m "Initial academic BVM demo"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```
Replace the example URL with your real GitHub username and repository. Paste the real public URL in the application form after you have pushed the code.

## Limitations and future work
Real fingerprint/camera SDK integration, liveness checks, secure enrollment, authentication hardening, access controls, encryption, independent security review, accessibility validation and relevant legal/certification processes are not implemented. Hash chains can detect some changes but are not tamper-proof. Do not publish voter-linked candidate choices or connect real voter data.
