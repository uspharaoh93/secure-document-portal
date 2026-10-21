# Implementation plan

Goal: produce a runnable, testable security portfolio project with synthetic data.
Architecture: Django views enforce assignment checks; SQLite holds documents and minimal audit records. Native session authentication and CSRF middleware handle browser state.
Spec: [Design](design.md).

1. Write request-level tests for login, list filtering, detail/download authorization and audit isolation. Run them against placeholder routes to establish failures, then implement models, policy and views.
2. Add setup, deterministic fixture descriptions and generated credentials. Test repeat setup, permission revocation, audit failure and backup restore without modifying the original database.
3. Add browser verification, linting, static analysis and dependency auditing. Pin dependencies and workflow actions. Run the entire suite.
4. Write the security study and operating guide. Review the publication file list, scan the complete fresh history, publish and verify GitHub Actions.

Review focus: direct record access, revoked access, authentication state, request data entering logs, and backup files escaping the private local directory.
