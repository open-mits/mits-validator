# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please follow these steps:

1. **Do not** create a public GitHub issue
2. Email security@open-mits.org with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

3. We will respond within 48 hours
4. We will work with you to resolve the issue
5. We will coordinate disclosure after the fix is ready

## Security Considerations

### Data Handling

- **No Data Storage**: The validator does not store uploaded files or URLs
- **Memory Only**: All processing happens in memory
- **No Logging**: Sensitive data is not logged
- **Temporary Files**: No temporary files are created

### Input Validation

- **File Size Limits**: Enforced to prevent DoS attacks
- **Content Type Validation**: Only XML content types allowed
- **URL Validation**: Restricted to HTTP/HTTPS schemes
- **Timeout Limits**: All operations have timeouts

### Network Security

- **HTTPS Only**: All network requests use HTTPS
- **No External Dependencies**: Minimal external dependencies
- **Sandboxed Execution**: Validation runs in isolated environment

### Code Security

- **Input Sanitization**: All inputs are validated
- **Error Handling**: No sensitive information in error messages
- **Dependency Scanning**: Regular security updates
- **Code Review**: All code changes are reviewed

## Security Best Practices

### For Users

1. **Use HTTPS**: Always use HTTPS for API requests
2. **Validate Inputs**: Validate XML before sending to validator
3. **Monitor Usage**: Monitor for unusual activity
4. **Keep Updated**: Use the latest version
5. **Secure Deployment**: Deploy behind a secure proxy

### For Developers

1. **No Secrets**: Never commit secrets or credentials
2. **Input Validation**: Validate all inputs
3. **Error Handling**: Don't expose sensitive information
4. **Dependencies**: Keep dependencies updated
5. **Code Review**: Review all security-related changes

## Security Features

### Built-in Protections

- **Size Limits**: Configurable file size limits
- **Timeout Protection**: All operations have timeouts
- **Content Type Validation**: Only XML content allowed
- **Memory Limits**: Configurable memory usage limits
- **Error Isolation**: Errors don't expose system information

### Configuration

```bash
# Security-related environment variables
export MITS_MAX_FILE_SIZE=10485760  # 10MB
export MITS_TIMEOUT_SECONDS=30
export MITS_ALLOWED_CONTENT_TYPES="application/xml,text/xml"
export MITS_DISABLE_URL_VALIDATION=false
export MITS_ALLOWED_URL_SCHEMES="http,https"
```

## Vulnerability Disclosure

### Timeline

1. **Report**: Vulnerability reported to security@open-mits.org
2. **Acknowledge**: Response within 48 hours
3. **Investigate**: Investigation within 7 days
4. **Fix**: Fix developed and tested
5. **Disclose**: Coordinated disclosure after fix

### Credit

Security researchers who responsibly disclose vulnerabilities will be:
- Credited in security advisories
- Listed in CONTRIBUTORS.md
- Recognized in release notes

## Security Updates

### Regular Updates

- **Dependencies**: Monthly security updates
- **Code Review**: Continuous security review
- **Penetration Testing**: Annual security testing
- **Vulnerability Scanning**: Automated scanning

### Emergency Updates

- **Critical Vulnerabilities**: Immediate patches
- **Security Advisories**: Public notifications
- **Version Updates**: New versions as needed

## Contact

- **Security Issues**: security@open-mits.org
- **General Questions**: conduct@open-mits.org
- **Project Issues**: GitHub Issues

## Legal

This security policy is provided for informational purposes only. It does not create any legal obligations or warranties. Users are responsible for their own security practices and compliance with applicable laws and regulations.
