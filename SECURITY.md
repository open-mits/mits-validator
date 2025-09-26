# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability, please follow these steps:

### 1. **DO NOT** create a public GitHub issue

Security vulnerabilities should be reported privately to avoid potential exploitation.

### 2. Email us directly

Send an email to: **security@example.org**

Include the following information:
- Description of the vulnerability
- Steps to reproduce (if applicable)
- Potential impact
- Any suggested fixes or mitigations

### 3. Response timeline

- **Initial response**: Within 48 hours
- **Status update**: Within 7 days
- **Resolution**: As quickly as possible, typically within 30 days

### 4. What to expect

- We will acknowledge receipt of your report
- We will investigate and validate the vulnerability
- We will work on a fix and coordinate disclosure
- We will credit you in our security advisories (unless you prefer to remain anonymous)

## Security Considerations

### Data Privacy

**Important**: MITS XML feeds may contain sensitive property information. When using this validator:

- **Never upload production data** to public instances
- **Use local deployment** for sensitive feeds
- **Review data** before uploading to any service
- **Consider data retention policies** of your deployment

### Safe Usage Guidelines

1. **Local deployment recommended** for sensitive data
2. **Network security**: Use HTTPS in production
3. **File size limits**: Default 10MB limit to prevent DoS
4. **Timeout limits**: 30-second timeout for URL requests
5. **No persistent storage**: Data is not stored by default

### Security Features

- Input validation and sanitization
- File size and timeout limits
- No persistent data storage by default
- Secure HTTP client with proper timeouts
- Type-safe request/response handling

## Security Updates

Security updates will be:
- Released as patch versions (e.g., 1.0.1, 1.0.2)
- Documented in release notes
- Tagged with security labels
- Communicated through GitHub security advisories

## Responsible Disclosure

We follow responsible disclosure practices:
- Vulnerabilities are kept private until fixed
- Coordinated disclosure with security researchers
- Credit given to reporters (unless anonymous)
- Clear communication about impact and mitigation

Thank you for helping keep MITS Validator secure!
