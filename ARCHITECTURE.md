# Technical Design and Architecture

## Data flow
```text
Synthetic ID + PIN -> Flask authentication -> voters table (eligibility/has_voted)
                                      |
                                      v
                              one-time demo token
                                      |
                                      v
                               candidate selection
                                      |
                                      v
                     ballots table (choice + hash-chain fields)
                                      |
                                      v
                    dashboard (aggregate counts + chain check)
```

## Components
- Browser UI: login, candidate selection, confirmation, dashboard.
- Flask: validates demo credentials, marks the synthetic account as having voted, accepts one-time demo token, records ballot and events.
- SQLite: `voters`, `ballots`, `events`, and `sessions` tables.
- SHA-256 hash chain: each ballot record links to the previous record hash.

## Privacy and security notes
Voter ID is not included in ballot rows, but this simple prototype is not a formally anonymous voting system. Database access, timing, logs or software flaws may allow correlation. Demo PINs are intentionally simple. The hash chain is not tamper-proof if an attacker can rewrite the database and recompute hashes.

## Not implemented
Real biometric sensors, face recognition, liveness detection, production authentication/session security, cryptographic election protocols, audit controls, independent review or certification.
