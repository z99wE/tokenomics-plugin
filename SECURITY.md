# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.x     | ✅ |
| < 2.0   | ❌ |

## Reporting a Vulnerability

Please **do not** open a public issue for security vulnerabilities.

Email: souvikchakraborty@souvik.local (or open a private GitHub Security Advisory).

We aim to acknowledge within 48 hours and provide a fix or mitigation within 7 days for critical issues.

## Security Practices

- Tokenomics never compresses or modifies secrets, auth tokens, crypto keys, SQL, or security-critical code.
- All processing is local; no data is sent to external servers.
- No hidden prompt injection; compression is opt-in and reversible.
- Secret scanning is recommended before commits (`npx soloknuckle check` or your own scanner).
