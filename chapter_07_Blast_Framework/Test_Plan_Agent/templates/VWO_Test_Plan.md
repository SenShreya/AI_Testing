# VWO Login Dashboard — Industry-Level Test Plan & Test Cases

| Field | Value |
|---|---|
| Document ID | VWO-LP-TP-001 |
| Version | 1.0 |
| Author | Senior QA Automation Tester (15 years) |
| Application Under Test | VWO Login Dashboard — https://app.vwo.com/#/login |
| Framework | RICEPOT |
| Date | 30 August 2026 |
| Status | Draft — pending review |

**Source inputs:** Product Requirements Document (PRD) embedded in `RICE_POT_Promt.md`; verification rules per `AntiHallucinationRule.md` (chapter_01_LLM_Basics). All content in this document is traceable to the PRD or explicitly labeled as inference.

---

## 1. Anti-Hallucination Compliance Block (per AntiHallucinationRule.md)

**Verified Facts (extracted from PRD input only):**
- Primary authentication is email and password with secure validation.
- Login page contains: email input, password input, "Remember Me" checkbox, account registration link, product announcement banner with Light/Dark mode options.
- Session management with configurable timeout periods; optional 2FA; enterprise SSO for organizational accounts.
- Real-time field validation on blur; email format verification; password strength indicators; clear error messages for failed authentication.
- Forgot-password flow with secure token generation; email-based reset; enforced password complexity.
- Auto-focus on first input field; clickable labels; loading states during authentication.
- ARIA labels, keyboard navigation, high-contrast mode; WCAG 2.1 AA target.
- HTTPS enforcement; encrypted transmission; encrypted password storage with industry-standard hashing; secure session tokens.
- GDPR and CCPA compliance; OWASP authentication guideline alignment; rate limiting against brute force.
- Login page load target ≤ 2 seconds on standard connections; 99.9% uptime; thousands of concurrent users.
- Seamless transition to the VWO dashboard post-login; analytics tracking of login success/failure; support-system integration.
- SSO (SAML, OAuth) and social login (Google, Microsoft) stated as optional integrations.
- KPI targets: 95%+ login success rate, sub-2-second page load, 90%+ user satisfaction, zero successful brute-force/unauthorized access, 20% reduction in login-related support tickets.

**Missing / Unknown Information (not specified in PRD):**
- Exact error-message strings shown for failed authentication (recorded as "<to be confirmed from actual build>").
- Session timeout duration value.
- Rate-limit threshold (attempts per time window).
- Password complexity rule specifics (minimum length, character classes).
- Credential details / test accounts for the QA environment.
- Reset-token validity window.
- Whether 2FA and SSO are enabled in the QA environment.
- The official acronym expansion of "RICEPOT" (repo template is empty). Interpretation per user decision: RICEPOT = the prompt's own section structure (Role, Instructions, Context, Expected, Parameters, Output, Tone).

**Self-Validation Check:**
- Every assertion above maps to a PRD statement. No feature, API, error code, or UI element has been invented. Where a value is not specified by the PRD, the test case states the observable behavior to verify and marks the specific value as "<to be confirmed from actual build>" or "Inference (low confidence)". Any inference is labeled explicitly.

---

## 2. Answers to the 10 Success-Criteria Questions (EXPECTED)

**Q1. What exactly are we testing?**
The VWO login dashboard at https://app.vwo.com/#/login: email/password authentication, input validation and error handling, forgot-password/recovery flow, Remember Me and session behavior, security controls (HTTPS, hashing, rate limiting verification), responsive/accessibility surface, Light/Dark theme, dashboard transition, and login page load performance — mapped to the PRD requirements.

**Q2. What are we NOT testing?**
Out of scope: live 2FA/SSO/SAML handshakes against real enterprise IdPs, social-login end-to-end flows, account registration and onboarding, VWO dashboard feature functionality, billing, destructive load testing, and penetration testing beyond the OWASP-verification cases listed in this plan. Rationale: PRD lists these as optional/enterprise capabilities; QA environment does not guarantee real IdP availability (Inference (low confidence) — to be confirmed with the project team).

**Q3. What can cause the biggest business impact?**
1) Total login unavailability (blocks all 4,000+ brands; breaks 99.9% uptime commitment). 2) Account takeover via brute force or session hijacking (zero-incident security KPI breached, GDPR/CCPA exposure). 3) Remember Me leaking a persistent session. 4) Login friction driving users to abandon (retention/conversion KPIs).

**Q4. What are the critical end-to-end journeys?**
- J1: Valid user login → dashboard transition.
- J2: Forgot password → email reset → set new password → login.
- J3: Failed login → error message → recovery options.
- J4: Remember Me → session persistence → logout/expiry → re-login.
- J5: New user discovery → registration path (navigation only).

**Q5. What systems/interfaces are dependent on this change?**
VWO core platform (dashboard hand-off), analytics integration (login success/failure tracking), support systems, enterprise identity providers (SSO — out of QA scope), social login providers (out of QA scope), CDN and infrastructure for page delivery, certificate authority (TLS).

**Q6. What data do we need to prove the functionality?**
Valid active account; invalid credentials; unregistered email; boundary-length emails/passwords (per build limits); uppercase email variant; locked account fixture; disposable test inbox for reset tokens; expired/intercepted reset-token fixtures; mobile viewport profiles; throttling test harness (if available).

**Q7. What could go wrong beyond the happy path?**
Network failure / timeout mid-request; server 5xx; session expiry during reset; token reuse after password change; malformed email (SQLi/XSS probes); clipboard paste of credentials; double-submit of login button; browser back/forward after login; disabled cookies; certificate errors; throttling lockout of a valid user.

**Q8. What must be true before testing can start?**
Entry criteria: QA environment stable and mirrors production configuration; test build deployed; test accounts and data provisioned; TLS certificates valid; upstream/external interfaces available; requirements signed off; automation harness (Selenium WebDriver) smoke-checked.

**Q9. What evidence do we need before recommending release?**
Exit criteria evidence: 100% planned cases executed; no open Sev-1/Sev-2 defects; pass rate ≥ 95%; requirement coverage ≥ 95%; zero security-critical findings; regression delta zero; metrics report (section 10) attached; release recommendation signed.

**Q10. What risks remain even after testing is complete?**
2FA/SSO/social login not verifiable in QA env (needs production-staged validation); production CDN/caching performance variance not fully reproducible; rate-limit thresholds environment-specific; credential-stuffing behavior at production scale; residual risk register maintained in section 14.

---

## 3. Scope

**In scope:**
- Login form: email + password fields, Remember Me, registration link, announcement banner.
- Authentication: successful login, failed login, error handling, loading states.
- Validation: email format, field-level on-blur validation, password strength indicators.
- Password management: forgot-password flow, token-based reset, complexity enforcement.
- Session: timeout behavior, Remember Me persistence, secure logout.
- UX: auto-focus, clickable labels, responsive design, keyboard navigation, ARIA, high contrast.
- Branding: Light/Dark mode, brand consistency.
- Security verification (defensive): HTTPS, input sanitization (XSS/SQLi probes), brute-force throttling verification, session token handling.
- Performance: login page load ≤ 2 seconds baseline (QA environment measurement).
- Integration: dashboard transition, analytics event firing (observable via network logs where available).

**Out of scope:**
- Registration, onboarding, and trial signup end-to-end.
- VWO dashboard feature functionality.
- Real 2FA/SSO/SAML and social-login provider handshakes.
- Billing and account administration.
- Destructive/chaos load testing and full penetration testing.
- Mobile native applications.

---

## 4. Test Strategy

- **Approach:** Risk-based testing. Functional core (authentication, validation, recovery) receives the deepest coverage; security and performance are verification-level per PRD claims.
- **Scenario types:** every test case is tagged — P (positive), N (negative), B (boundary), E (exception).
- **Execution:** Selenium WebDriver automates the regression pack (S10) and high-runner functional cases; manual execution for accessibility, visual/theme, and exploratory security probes.
- **Test data strategy:** dedicated QA accounts; disposable inbox for reset flows; no production credentials used.
- **Defect handling:** defects logged with severity (Sev-1..Sev-4), linked to Requirement ID and failing test case ID; retest after fix with evidence.

---

## 5. Dependencies

| # | Dependency | Requirement | Status | Owner |
|---|---|---|---|---|
| 1 | External system availability | VWO app, identity/auth backend reachable from QA network | Required before execution | Platform/DevOps |
| 2 | Test environment | QA environment mirrors production configuration; stable | Required | DevOps |
| 3 | Test data | Valid/invalid test accounts, disposable inbox, token fixtures provisioned | Required | QA |
| 4 | Third-party API | Analytics endpoint, support integration endpoints available (observable) | Required for INT suite | Dev/QA |
| 5 | Development deployment | Latest build deployed and versioned | Required | Dev |
| 6 | Infrastructure | CDN, DNS, hosting reachable; 99.9% uptime posture | Required | DevOps |
| 7 | Certificates | Valid TLS certificates on QA environment (no browser warnings) | Required | DevOps |
| 8 | Business availability | Authorized access to test app; no change freeze conflicts; stakeholder sign-off | Required | QA lead/Product |

---

## 6. Assumptions

1. Requirements (PRD) are stable and signed off — no mid-cycle changes.
2. Test environment mirrors production configuration (auth settings, session policy, rate limiting).
3. Upstream system (identity/authentication backend) provides expected data.
4. External interfaces (analytics, support, CDN) are available during testing.
5. QA test accounts can be provisioned on demand (Inference (low confidence) — depends on environment).
6. 2FA/SSO/social login are NOT enabled for QA accounts unless explicitly stated (Inference (low confidence)).
7. RICEPOT refers to the prompt structure (Role, Instructions, Context, Expected, Parameters, Output, Tone) — per user decision; the repo does not define an official expansion.

---

## 7. Entry & Exit Criteria

**Entry criteria (all must be met):**
- QA environment stable and configured like production; build deployed with version noted.
- Test accounts and test data seeded; disposable inbox ready.
- TLS certificates valid; no browser security warnings.
- External dependencies (section 5) confirmed available.
- Requirements signed off; this test plan reviewed and approved.

**Exit criteria (all must be met for release recommendation):**
- 100% of planned test cases executed.
- No open Sev-1 / Sev-2 defects; Sev-3/Sev-4 backlog triaged with agreed workaround.
- Pass rate ≥ 95%; requirement coverage ≥ 95%.
- Zero security-critical findings (no unauthorized access, no injection, no session issues).
- Regression results show zero new regressions.
- Metrics report (section 8) delivered; release recommendation documented and signed.

---

## 8. What We Report — Metrics (Dedicated Section)

| Metric | Definition | Target | Report Cadence |
|---|---|---|---|
| Planned vs executed test cases | Executed count / planned count | 100% executed | Daily |
| Pass/fail percentage | Passed / executed × 100 | ≥ 95% pass | Daily |
| Requirement coverage | Requirements tested / total in-scope requirements | ≥ 95% | Weekly |
| Defect count | Total defects logged (all severities) | Reported per severity | Daily |
| Defect severity distribution | Sev-1..Sev-4 count and % of total | Sev-1 = 0 at exit | Weekly |
| Defect leakage | Defects found in production / total defects | < 5% | Per release |
| Defect aging | Average & max days defects open | Sev-1 < 24 h; Sev-2 < 72 h | Weekly |
| Retest success rate | Defects verified fixed on first retest / retested defects | ≥ 90% | Weekly |
| Regression results | New regressions found during regression cycle | 0 new regressions | Per cycle |
| Automation coverage | Automated cases / total regression-suite cases | ≥ 70% | Per release |

---

## 9. Test Case Suites

**ID scheme:** `VWO-<AREA>-<NNN>_<T>` where AREA ∈ {LOG, VAL, PWD, MEM, SEC, UXA, BRD, INT, PER, REG}, NNN = sequence, T = scenario type (P positive, N negative, B boundary, E exception).

**Requirement ID reference:** FR-AUTH (authentication), FR-VAL (validation), FR-PWD (password), FR-UX (interface UX), FR-ACC (accessibility), FR-BRAND (branding), TR-SEC (data protection), TR-COMP (compliance/rate limit), TR-PERF (performance), TR-SCAL (scalability), TR-INT (integrations), TR-TPS (third-party services), JM (journeys), KPI (success metrics).

**Convention:** "Actual Result" is intentionally blank — filled at execution time with observed behavior and evidence.

### S1 — Functional: Login (16 cases)

| Test case id | Description | Actual Result | Expected result | Requirement ID | Dependencies |
|---|---|---|---|---|---|
| VWO-LOG-001_P | Valid registered email and correct password; click Login | | Login succeeds; user lands on VWO dashboard; no error shown; loading state clears | FR-AUTH, JM | Test account active; auth backend up |
| VWO-LOG-002_P | Login with email containing uppercase characters (e.g., User@Example.com) | | Login succeeds; email treated case-insensitively for the local part handling per backend rules | FR-AUTH, FR-VAL | Valid account |
| VWO-LOG-003_P | Login with leading/trailing whitespace trimmed on email field | | Whitespace trimmed; login succeeds if core email is valid | FR-AUTH, FR-VAL | Valid account |
| VWO-LOG-004_P | Valid credentials with Remember Me unchecked; close browser; reopen | | Session does not persist after browser close; user must re-login | FR-AUTH, FR-UX | Valid account |
| VWO-LOG-005_N | Valid email with incorrect password | | Login fails; clear, actionable error message shown; user remains on login page; no crash | FR-AUTH, FR-VAL | Valid email, wrong password |
| VWO-LOG-006_N | Unregistered email with any password | | Login fails with error; no account enumeration detail in message (verify message wording against build) | FR-AUTH, TR-COMP | Auth backend |
| VWO-LOG-007_N | Blank email field; valid password; click Login | | Field-level validation error on email; login blocked | FR-VAL | Form validation enabled |
| VWO-LOG-008_N | Blank password field; valid email; click Login | | Field-level validation error on password; login blocked | FR-VAL | Form validation enabled |
| VWO-LOG-009_N | Both fields blank; click Login | | Validation errors on both fields; no request submitted | FR-VAL | Form validation enabled |
| VWO-LOG-010_N | Email field contains spaces only | | Validation error; login blocked | FR-VAL | Form validation enabled |
| VWO-LOG-011_B | Email at maximum permitted length (per build — <to be confirmed from actual build>) with valid password | | Login succeeds; no truncation issues | FR-VAL | Boundary spec from build |
| VWO-LOG-012_B | Password at maximum permitted length (per build) | | Login succeeds; field accepts full input | FR-VAL | Boundary spec from build |
| VWO-LOG-013_E | Network timeout during login submission (kill network mid-request) | | Graceful error/retry state shown; no hang, no partial session, no data loss | FR-AUTH, FR-UX | Network control in QA env |
| VWO-LOG-014_E | Server returns 5xx during authentication | | User-facing error message; login not completed; no stack trace exposed | FR-AUTH, TR-SEC | Fault injection available |
| VWO-LOG-015_E | Double-click Login button rapidly | | Single authentication request; no duplicate session or error | FR-AUTH, FR-UX | Button disabled during submit (verify) |
| VWO-LOG-016_E | Browser Back/Forward navigation after successful login | | Cannot return to a functional login form that re-submits; session remains consistent; no logout | FR-AUTH, JM | Browser session |

### S2 — Input Validation (8 cases)

| Test case id | Description | Actual Result | Expected result | Requirement ID | Dependencies |
|---|---|---|---|---|---|
| VWO-VAL-001_P | Type valid email; tab/blur out of field | | Real-time validation passes with no error | FR-VAL | Form validation enabled |
| VWO-VAL-002_N | Enter invalid email format (e.g., "user@" or "user@.com") and blur | | Immediate field-level error on blur; login blocked | FR-VAL | Form validation enabled |
| VWO-VAL-003_N | Enter email without domain extension; blur | | Validation error shown | FR-VAL | Form validation enabled |
| VWO-VAL-004_B | Enter email of exactly minimum length (per build); blur | | Accepted or rejected consistently with documented rule | FR-VAL | Boundary spec from build |
| VWO-VAL-005_B | Enter email just over maximum length; blur | | Rejected with clear length error | FR-VAL | Boundary spec from build |
| VWO-VAL-006_N | Password field with only lowercase characters (strength indicator) | | Weak-strength indicator shown; login still permitted if complexity rule is display-only (verify against build) | FR-VAL, FR-PWD | Password strength UI present |
| VWO-VAL-007_E | Paste credentials via clipboard instead of typing | | Paste works; validation and login behave as typed input | FR-UX | Browser paste allowed |
| VWO-VAL-008_E | Special characters in email local part (e.g., quotes, plus signs) | | Processed per RFC/backend rules without error or injection | FR-VAL, TR-SEC | Backend email parser |

### S3 — Forgot Password / Recovery (10 cases)

| Test case id | Description | Actual Result | Expected result | Requirement ID | Dependencies |
|---|---|---|---|---|---|
| VWO-PWD-001_P | Click "Forgot Password" with registered email | | Password reset email with secure token sent to registered address | FR-PWD | Mail service; disposable inbox |
| VWO-PWD-002_P | Open reset link from email; set new valid password | | New password accepted; confirmation shown | FR-PWD | Valid token |
| VWO-PWD-003_P | After password reset, login with new password | | Login succeeds | FR-PWD, FR-AUTH | Reset completed |
| VWO-PWD-004_P | Password reset success message with clear next-step guidance | | Success confirmation and guidance displayed | FR-PWD, JM | Reset flow |
| VWO-PWD-005_N | Submit forgot-password for unregistered email | | No account-confirmation detail leaked; user informed reset link sent if not found (message wording — <to be confirmed from actual build>) | FR-PWD, TR-COMP | Auth backend |
| VWO-PWD-006_N | Open reset link with expired token | | Clear expiry error; option to request a new link | FR-PWD, TR-SEC | Token expiry fixture |
| VWO-PWD-007_N | Open reset link with already-used/invalid token | | Invalid-token error; no password change allowed | FR-PWD, TR-SEC | Used-token fixture |
| VWO-PWD-008_N | Set new password below minimum complexity (per build rules) | | Rejected with actionable complexity message | FR-PWD, FR-VAL | Complexity rule from build |
| VWO-PWD-009_B | Reset token at boundary of validity window (just before expiry) | | Succeeds if within window; else clear expiry message (verify timestamp behavior) | FR-PWD | Token fixtures |
| VWO-PWD-010_E | Old password reused after reset; attempt login with old password | | Old password no longer works; new password required | FR-PWD, TR-SEC | Reset completed |

### S4 — Remember Me / Session (8 cases)

| Test case id | Description | Actual Result | Expected result | Requirement ID | Dependencies |
|---|---|---|---|---|---|
| VWO-MEM-001_P | Check Remember Me; login; close browser; reopen | | Session persists; user remains logged in | FR-AUTH, FR-UX | Cookie/token persistence |
| VWO-MEM-002_P | Login without Remember Me; close browser; reopen | | User is logged out; must re-login | FR-AUTH, FR-UX | Default session behavior |
| VWO-MEM-003_P | Explicit logout; check session cleared | | Logout terminates session; credentials not auto-replayed; login page shown | FR-AUTH, TR-SEC | Logout control present |
| VWO-MEM-004_E | Session times out during active use (per configured timeout — value <to be confirmed from actual build>) | | User redirected to login; no data loss; clear session-expiry message | FR-AUTH, JM | Session policy |
| VWO-MEM-005_N | Login on device A, then attempt same-session reuse from device B (token replay) | | Replayed/stolen token rejected; no unauthorized session | TR-SEC | Security fixtures |
| VWO-MEM-006_E | Cookies disabled in browser; attempt login | | Clear messaging or functional degradation documented; no silent breakage | FR-UX, TR-SEC | Browser config |
| VWO-MEM-007_N | Check Remember Me; log out; close browser; reopen | | Logout overrides Remember Me; login page shown | FR-AUTH, TR-SEC | — |
| VWO-MEM-008_E | Session expiry while on dashboard; click a dashboard action | | Redirected to login with session-expired notice; action not executed twice | FR-AUTH, JM | Session policy |

### S5 — Security (12 cases) — defensive verification per PRD claims

| Test case id | Description | Actual Result | Expected result | Requirement ID | Dependencies |
|---|---|---|---|---|---|
| VWO-SEC-001_N | Repeated failed login attempts beyond rate limit (threshold <to be confirmed from actual build>) | | Requests throttled; account locked/blocked per policy; no brute force succeeds | TR-COMP | Rate-limit config |
| VWO-SEC-002_N | SQL injection probe in email field (e.g., `' OR '1'='1`) | | Input treated as data; login fails; no SQL error exposed | TR-SEC, TR-COMP | WAF/backend |
| VWO-SEC-003_N | XSS probe in email/password fields (e.g., `<script>alert(1)</script>`) | | Input escaped; no script execution; no stored XSS | TR-SEC | Input sanitization |
| VWO-SEC-004_N | Verify login page loads only over HTTPS (attempt HTTP) | | HTTP redirects to HTTPS or is refused; no plaintext form | TR-SEC | TLS config |
| VWO-SEC-005_N | Inspect password field — confirm not transmitted/stored in plaintext (network logs, storage) | | Password masked in UI; request body encrypted (HTTPS); no plaintext in logs | TR-SEC | Network inspection |
| VWO-SEC-006_N | Inspect session token/cookie attributes | | HttpOnly, Secure flags set (verify); token not exposed in JS | TR-SEC | Auth backend |
| VWO-SEC-007_N | Login as user A, then tamper session cookie to impersonate user B | | Tampered token rejected; no privilege escalation | TR-SEC | Auth backend |
| VWO-SEC-008_E | Certificate invalid/expired on QA env | | Browser blocks with warning; login not possible over invalid cert | TR-SEC, TR-COMP | Env cert state |
| VWO-SEC-009_N | Verify password storage claim: reset password and confirm no mechanism returns original password | | Original password unrecoverable; only reset flow exists | TR-SEC | Auth backend |
| VWO-SEC-010_N | Verify rate limiting persists across restart/browser change (throttle state server-side) | | Throttle not bypassed by clearing cookies | TR-COMP | Rate-limit config |
| VWO-SEC-011_N | Verify no sensitive data in URL/query string during login or reset | | Credentials/tokens not in URL; all in body/headers | TR-SEC | Auth backend |
| VWO-SEC-012_E | Concurrent login from multiple locations with same account | | Behavior defined by policy (e.g., both allowed, or session invalidation) — verify and document | FR-AUTH, TR-SEC | Session policy |

### S6 — UX / Accessibility / Responsive (10 cases)

| Test case id | Description | Actual Result | Expected result | Requirement ID | Dependencies |
|---|---|---|---|---|---|
| VWO-UXA-001_P | Page loads; observe focus placement | | Auto-focus on first input field (email) | FR-UX | — |
| VWO-UXA-002_P | Click on the label of email/password fields | | Label click focuses corresponding input (clickable labels) | FR-UX, FR-ACC | — |
| VWO-UXA-003_P | Navigate entire login form using keyboard only (Tab/Enter/Esc) | | All interactive elements reachable and operable; focus order logical | FR-ACC | — |
| VWO-UXA-004_P | Run screen reader over login form (e.g., NVDA/VoiceOver) | | ARIA labels announced for all fields/errors/buttons; no unlabeled controls | FR-ACC | Screen reader tooling |
| VWO-UXA-005_P | Verify high-contrast mode rendering | | Content readable; contrast meets WCAG 2.1 AA (verify against build measurement) | FR-ACC | Contrast tooling |
| VWO-UXA-006_P | Resize to mobile viewport (e.g., 375×667); attempt login | | Responsive layout; touch-friendly controls; full login flow works | FR-UX, FR-ACC | Mobile emulation |
| VWO-UXA-007_P | Loading state during authentication | | Clear progress/loading indicator shown; no frozen UI | FR-UX | Slow-network simulation |
| VWO-UXA-008_P | Error state readability — validation errors visible and near the field | | Errors visually associated with field; readable by assistive tech | FR-UX, FR-ACC | — |
| VWO-UXA-009_E | Extreme narrow viewport / browser zoom | | Layout does not break; login remains usable or graceful scroll | FR-UX | Viewport tooling |
| VWO-UXA-010_N | Focus trap: open error and tab through — no invisible focus loss | | Focus visible at all times; no focus lost off-page | FR-ACC | — |

### S7 — Branding & Theme (4 cases)

| Test case id | Description | Actual Result | Expected result | Requirement ID | Dependencies |
|---|---|---|---|---|---|
| VWO-BRD-001_P | Toggle Dark Mode from announcement banner | | Theme switches; branding consistent; no contrast regressions | FR-BRAND, FR-UX | Theme control present |
| VWO-BRD-002_P | Toggle Light Mode | | Theme switches back; branding consistent | FR-BRAND | Theme control present |
| VWO-BRD-003_P | Theme persistence after reload / navigation | | Selected theme persists (verify persistence scope — per build) | FR-BRAND | Theme control |
| VWO-BRD-004_N | Compare rendered colors/logos against VWO design system | | No off-brand colors, broken logos, or layout distortion | FR-BRAND | Design spec reference |

### S8 — Integration & Navigation (6 cases)

| Test case id | Description | Actual Result | Expected result | Requirement ID | Dependencies |
|---|---|---|---|---|---|
| VWO-INT-001_P | Successful login → dashboard | | Seamless transition to VWO dashboard; correct user context | TR-INT, JM | VWO core platform |
| VWO-INT-002_P | Verify login success event observed in analytics (network/log) | | Login success/failure tracking event fires with expected payload | TR-INT | Analytics endpoint |
| VWO-INT-003_P | Click registration link from login page | | Navigates to free trial signup path | TR-INT, JM | Marketing site |
| VWO-INT-004_E | VWO core platform unavailable during login | | Clear error state; no misleading success; retry guidance | TR-INT | Fault injection |
| VWO-INT-005_E | Analytics endpoint failure during login | | Login not blocked by analytics failure; degradation graceful | TR-INT | Fault injection |
| VWO-INT-006_P | SSO/social login buttons visible (if present) | | Links rendered; navigation to provider works where in scope (full handshake out of scope) | TR-TPS | Provider availability |

### S9 — Performance (4 cases)

| Test case id | Description | Actual Result | Expected result | Requirement ID | Dependencies |
|---|---|---|---|---|---|
| VWO-PER-001_B | Measure login page load time on standard connection (QA env baseline) | | ≤ 2 seconds per PRD target | TR-PERF, KPI | Load tooling |
| VWO-PER-002_B | Measure time from submit to dashboard render with valid credentials | | Within acceptable threshold (<to be confirmed from actual build>); no long stall | TR-PERF | Valid account |
| VWO-PER-003_B | Verify static assets served via CDN (headers/caching) | | CSS/JS/images cached and served from CDN; minified/compressed | TR-PERF | CDN config |
| VWO-PER-004_E | Simulate N concurrent login attempts (N <to be confirmed from actual build>) | | No outage, no degradation beyond acceptable limits; auth backend handles concurrency | TR-SCAL | Load harness |

### S10 — Regression Pack (6 cases, automation candidates)

| Test case id | Description | Actual Result | Expected result | Requirement ID | Dependencies |
|---|---|---|---|---|---|
| VWO-REG-001_P | Smoke: valid login → dashboard → logout | | Full happy path passes end-to-end | FR-AUTH, JM | Selenium harness |
| VWO-REG-002_P | Smoke: invalid password error state | | Error message shown; no crash | FR-AUTH | Selenium harness |
| VWO-REG-003_P | Smoke: blank-field validation | | Both fields validated | FR-VAL | Selenium harness |
| VWO-REG-004_P | Smoke: forgot-password request for registered email | | Reset email triggered | FR-PWD | Selenium harness |
| VWO-REG-005_P | Smoke: Remember Me persistence | | Session persists as configured | FR-AUTH | Selenium harness |
| VWO-REG-006_P | Smoke: responsive viewport login | | Login succeeds on mobile viewport | FR-UX | Selenium harness |

---

## 10. Requirement Coverage Matrix

| Requirement | Suites covering it | Status |
|---|---|---|
| FR-AUTH | S1, S4, S5, S8, S10 | Planned |
| FR-VAL | S1, S2, S3 | Planned |
| FR-PWD | S3 | Planned |
| FR-UX | S1, S4, S6, S7, S10 | Planned |
| FR-ACC | S6 | Planned |
| FR-BRAND | S7 | Planned |
| TR-SEC | S3, S4, S5 | Planned |
| TR-COMP | S1, S3, S5 | Planned |
| TR-PERF | S9 | Planned |
| TR-SCAL | S9 | Planned |
| TR-INT | S8 | Planned |
| TR-TPS | S8 | Planned |
| JM | S1, S3, S4, S8, S10 | Planned |
| KPI | S9 | Planned |

---

## 11. Risk Register (residual risks after testing)

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | 2FA/SSO/social login not verifiable in QA env | Medium | High | Production-staged verification plan; document as residual risk |
| 2 | Production CDN/caching performance differs from QA | Medium | Medium | Baseline on production-like staging; monitor post-release |
| 3 | Rate-limit thresholds environment-specific | Medium | Medium | Confirm thresholds with security team; verify logic, not absolute numbers |
| 4 | Exact error-message copy differs from PRD | Low | Low | Capture actual strings during execution; confirm with UX/Dev |
| 5 | Test data sensitivity (disposable accounts) | Low | Medium | No production data; restricted QA accounts |

---

## 12. Sign-off & Release Recommendation Gate

Release may be recommended only when all exit criteria (section 7) are met, the metrics report (section 8) is attached, residual risks (section 11) are accepted by stakeholders, and this document is signed:

| Role | Name | Signature | Date |
|---|---|---|---|
| Test Lead / Author | | | |
| Development Lead | | | |
| Product Owner | | | |
| Release Manager | | | |
