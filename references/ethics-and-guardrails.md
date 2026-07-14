# Ethics and guardrails

## Purpose of this skill

Teach coding agents to build **installable HTTP client packages** that wrap
web-app private endpoints—the architecture used by educational/community projects
like Claude-API.

It is **not** a guide for attacking systems, stealing accounts, or commercial
fraud.

## Allowed

- Learning reverse-engineering and packaging patterns
- Automating **services the user owns** or has explicit permission to automate
- Personal tooling where the vendor has no API and ToS allows reasonable automation
- Scaffolding **demo/mock** clients for teaching
- Migrating users **toward official APIs** when available

## Disallowed / refuse

- Credential stuffing, phishing helpers, session theft tools
- Bypassing CAPTCHA, MFA, or paywalls for unauthorized access
- Malware, exploit PoCs against third-party systems
- Instructions whose sole purpose is ToS-violating bulk abuse of a commercial AI

If the user request is clearly malicious, refuse briefly. If ambiguous, prefer
official APIs + demo scaffolding and explain risks.

## Always document

1. Unofficial status and lack of affiliation
2. Fragility (endpoints change without notice)
3. Account/ban risk when using cookie automation against consumer sites
4. Official alternative when it exists

## Secrets handling

- Never commit cookies, HAR files with cookies, or `.env`
- Prefer `SERVICE_COOKIE` / `API_TOKEN` env vars
- Redact secrets in logs and README screenshots
- Rotate cookies if they were pasted into chat logs

## Production recommendation

| Use case | Recommendation |
|----------|----------------|
| SaaS product, paid users | Official API only |
| Learning packaging | Demo Client scaffold |
| Personal one-off script | Unofficial OK with eyes open |
| High volume automation | Official API + rate limits |

## Legal note (non-lawyer)

Terms of service, CFAA-like laws, and local computer-misuse statutes vary.
Agents should not claim “it's free so it's legal.” Prefer user-owned systems and
documented APIs.
