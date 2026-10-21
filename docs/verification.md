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

The workflow is included. Hosted run status and repository merge protection will be verified after publication; until then, they are not claimed as passing or enforced. The [Actions page](https://github.com/uspharaoh93/secure-document-portal/actions) is the live record.

## Limits

No production deployment, independent penetration test, external integration test or certification was performed. Browser checks assume a fresh six-document demo seed. Automated checks cannot prove the absence of all vulnerabilities or confidential information.
