# Verification record

Publication review: October 21, 2026. Evidence applies to the revision tested, not to later changes or production use.

## Local execution

- Django request and recovery suite: **31 tests passed**.
- Django system and migration checks: passed.
- Ruff application/repository checks: passed.
- Bandit scan of `portal/` and `config/`: no findings reported.
- pip-audit of the runtime and development lockfiles: no known vulnerabilities reported at execution time.
- Chromium: login, assigned list, document view/download, denied cross-account download, reviewer isolation, audit display, logout and mobile-width layout passed.
- SQLite backup and restore comparison: passed.
- Clean-copy installation using hash-checked dependencies: all application, browser and restore checks passed.
- Separate AI-assisted code review: no critical or important findings within the local demonstration scope; audit wording clarified and narrow reviewer layouts checked. This was not an independent security audit.
- Screenshots: captured from the fictional application and visually inspected.

The initial request suite failed against unimplemented routes. After implementation, browser testing exposed a CSRF/referrer-policy interaction; the policy was corrected and the complete browser flow rerun successfully. These are actual development observations, not findings in the private application.

## Hosted checks

The [initial published revision passed all three hosted jobs](https://github.com/uspharaoh93/secure-document-portal/actions/runs/39678819868): **Verify portal**, **Secret scan**, and **Verified source artifact**. The Linux runner installed hash-locked dependencies, ran the application and browser checks, verified a restored copy, scanned the full fresh Git history and produced the tracked-source archive with its checksum.

The `main` branch requires **Verify portal** and **Secret scan**, an up-to-date branch, a pull request and resolved review conversations. These rules apply to administrators. Force pushes and branch deletion are disabled. The required approving-review count is zero for this solo project; the pull-request requirement does not imply independent human approval. Workflow tokens default to read-only, and private vulnerability reporting is enabled.

The linked run applies to its own commit. The [Actions page](https://github.com/uspharaoh93/secure-document-portal/actions) and README badge show later run results. This evidence update is submitted through the protected-branch workflow.

## Limits

No production deployment, independent penetration test, external integration test or certification was performed. Browser checks assume a fresh six-document demo seed. Automated checks cannot prove the absence of all vulnerabilities or confidential information.
