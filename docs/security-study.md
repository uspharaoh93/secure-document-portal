# Two security risks and their remediation

## Scope and method

The subject is a small document portal with two employees and one audit reviewer. It stores only fictional text records. The review is limited to local application behavior and the public repository's build process.

The two weaknesses below are **hypothetical teaching scenarios**, not findings from a private application. The shipped routes implement the remediations. There is no internet-facing vulnerable mode.

1. Identify assets: document contents, assignments, passwords, sessions and audit records.
2. Identify entry points: login, document list, document view, download and audit view.
3. Write the expected permissions before implementing the routes.
4. Exercise requests with an assigned user, an unassigned user, a reviewer and no session.
5. Attempt the same access through direct URLs; hiding a link is not an access control.
6. Inspect stored audit fields for synthetic secret markers and document contents.
7. Retain automated regression tests and verify the same user journey in a browser.
8. Test recovery into a separate database and scan the publication history for secrets.

## Risk 1: broken object-level authorization

**Hypothetical weakness.** A detail or download handler retrieves a document by its identifier without checking whether the current user is assigned to it. A filtered document list would not fix that handler.

**How it could be exploited.** In the local learning scenario, employee Alex opens an assigned record, changes the numeric identifier in the URL to a record assigned to Jordan, and requests the detail or download route. An unrestricted lookup would return another employee's document. Knowing or guessing an identifier is not permission to use it.

**Impact on the CIA triad.** The read and download routes would breach confidentiality. If the same mistake existed in an edit or delete route, it could also affect integrity or availability; this application has neither of those routes, so those effects are hypothetical extensions, not tested findings.

**Remediation implemented.** Both retrieval routes call `assigned_document()` in `portal/views.py`. The database query includes the current user assignment. The list uses the same assignment relation. Missing and unauthorized records return the same unavailable response. Audit permission and even a superuser flag do not bypass document assignments.

**Recovery steps for a real incident.** Restrict the affected routes, preserve relevant evidence, correct the server-side policy, and review exposed records and affected accounts. Investigate the actual scope before making notification decisions. Re-run direct-view, direct-download and revocation tests before restoring service. A code patch prevents future unauthorized reads; it cannot recover copies already disclosed.

**Tests.** `test_direct_id_access_is_denied`, `test_missing_and_unassigned_responses_match`, `test_revocation_applies_to_active_session`, `test_reviewer_has_no_implicit_document_access` and `test_superuser_has_no_implicit_document_access` cover the main boundaries. Browser checks also attempt a direct cross-account download.

This control follows the principles of denying access by default and validating authorization on every request in the [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html).

## Risk 2: sensitive data exposure through logging

**Hypothetical weakness.** A diagnostic statement records the complete request or document response. A log may then contain passwords, session cookies, authorization headers or confidential text. If employees can read the log, the logging path becomes a second route to restricted information.

**How it could be exploited.** A person with access to an overly broad log viewer or exported debug file could read copied document text. If a usable session token were also present, it could permit session impersonation until expiration or revocation. This is a scenario analysis; no real token or confidential record is used here.

**Impact on the CIA triad.** Copied document text affects confidentiality. Stolen sessions could permit integrity or availability attacks if the impersonated user has write or delete permissions elsewhere. This read-only portal does not demonstrate those additional actions.

**Remediation implemented.** `portal/audit.py` accepts numeric identifiers and a fixed set of action/outcome codes. It does not accept a request object, free-form message or document body. The audit route requires a separate permission. Ordinary employees receive 403. A failed audit write blocks document delivery with 503. Logout still ends a session if audit storage fails. Local request/error loggers are suppressed to avoid a second unstructured payload channel; the trade-off is less diagnostic detail.

**Recovery steps for a real incident.** Stop sensitive payload logging, restrict affected log stores and exports, preserve an access-controlled incident record, and determine who could read the affected material. Revoke exposed sessions and rotate affected credentials. Handle log retention or disposal under the organization's incident and retention procedures. Re-run marker-based log tests and reviewer-access tests before restoring normal operation.

**Tests.** `test_audit_excludes_sensitive_request_and_document_data` sends fictional markers in headers, a cookie and query text, then verifies that none enter the audit table. Other tests verify successful and failed access events, denied log access, failed-login identity minimization and fail-closed document delivery.

The design applies the advice on excluding sensitive values and restricting log access in the [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html).

## Residual risk

SQLite operators can read or modify the database and audit table. Numeric actor IDs remain linkable to local accounts. Audit storage has no rotation, retention service, external monitoring or cryptographic integrity protection. A full disk can stop document delivery. Password login has no rate limiter or MFA. These limits make this a local teaching application, not a deployable confidential-document service.

## Additional references

- [Django security documentation](https://docs.djangoproject.com/en/5.2/topics/security/): framework protections and their configuration boundaries.
- [NIST SP 800-218, SSDF 1.1](https://csrc.nist.gov/pubs/sp/800/218/final): a public reference for integrating security activities into development. This project does not claim certification.
