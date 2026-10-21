# Continuous integration and artifact delivery

The GitHub Actions workflow runs on pushes, pull requests and manual requests. Jobs use a read-only contents token. Actions are pinned to full commit hashes and checkout does not retain credentials. No production secrets are required.

1. Install the Python dependencies from the hash-locked file.
2. Run Django configuration/migration checks and request-level tests.
3. Run Ruff, Bandit and an advisory-based dependency audit.
4. Seed a disposable fictional database and run Chromium through login, document access, a denied direct download, reviewer isolation, logout and mobile layout.
5. Verify a backup and restored copy.
6. Independently scan the complete Git history with a pinned Gitleaks release whose archive checksum is verified.
7. Only when verification and secret scanning succeed on `main`, create a source archive from tracked Git content and upload it with a checksum. Local data, credentials and virtual environments are not in that archive.

The artifact job is a limited continuous-delivery demonstration. It does not deploy a server, publish a container or approve production use. Artifact retention is seven days. The action page records run status; the workflow's presence alone does not prove a successful run.

Required branch checks are configured separately from workflow YAML. See the verification record for the repository settings actually enabled. Changes to the pipeline should receive the same review as application changes.

The choices around token permissions and immutable action references follow [GitHub's secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use).
