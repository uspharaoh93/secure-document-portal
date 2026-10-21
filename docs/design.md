# Design

This independent portfolio application demonstrates two controls: document-level authorization and audit logging that excludes sensitive content. It uses Python, Django and SQLite, server-rendered HTML, two employee accounts and one audit reviewer. Six synthetic text documents live in the database. A reviewer can inspect events but has no implicit document access.

Every list, detail and download request checks current assignments on the server. Unassigned and nonexistent records both return 404. A failed audit write prevents document delivery. Audit entries contain only time, numeric actor/target identifiers, an event code and an outcome. No request bodies, credentials, document titles or contents enter the application audit trail.

The demonstration runs on loopback HTTP. It has no public hosting, uploads, external integrations, self-registration, email or production deployment. SQLite and a local audit table are deliberate teaching constraints, not an enterprise architecture. Users with database or filesystem access remain trusted operators. MFA, distributed throttling, tamper-resistant log storage and production availability engineering are outside this build.

Acceptance: working login/logout, correct lists and downloads, immediate permission revocation, CSRF rejection, escaped document text, safe audit access, backup/restore verification, passing dependency/static/secret checks, real browser demonstration and passing hosted CI. Hypothetical flaws must be labeled; private code, data and architecture must not enter this repository.
