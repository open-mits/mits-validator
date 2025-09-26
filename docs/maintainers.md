# Maintainers Guide

This guide provides information for project maintainers on release management, repository settings, and maintenance procedures.

## Release Management

### Versioning Strategy

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes to API or behavior
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Process

1. **Prepare Release**:
   ```bash
   # Update version in pyproject.toml
   # Update CHANGELOG.md
   # Update documentation
   ```

2. **Create Release**:
   ```bash
   # Create release branch
   git checkout -b release/v0.1.0
   
   # Update version
   # Commit changes
   git commit -m "chore: prepare v0.1.0 release"
   
   # Create tag
   git tag -a v0.1.0 -m "Release v0.1.0"
   
   # Push tag
   git push origin v0.1.0
   ```

3. **Publish Release**:
   ```bash
   # Build package
   uv build
   
   # Publish to PyPI
   uv publish
   ```

### Pre-release Process

1. **Create Pre-release**:
   ```bash
   # Create pre-release tag
   git tag -a v0.1.0-alpha.1 -m "Pre-release v0.1.0-alpha.1"
   git push origin v0.1.0-alpha.1
   ```

2. **Test Pre-release**:
   ```bash
   # Install pre-release
   pip install mits-validator==0.1.0a1
   
   # Test functionality
   mits-validate version
   ```

### Release Drafter Configuration

The repository uses [Release Drafter](https://github.com/release-drafter/release-drafter) to automatically generate release notes.

**Configuration** (`.github/release-drafter.yml`):
```yaml
name-template: 'v$RESOLVED_VERSION 🌟'
tag-template: 'v$RESOLVED_VERSION'
categories:
  - title: '🚀 Features'
    labels:
      - 'feature'
      - 'enhancement'
  - title: '🐛 Bug Fixes'
    labels:
      - 'fix'
      - 'bugfix'
      - 'bug'
  - title: '🧰 Maintenance'
    labels:
      - 'chore'
      - 'dependencies'
      - 'maintenance'
  - title: '📚 Documentation'
    labels:
      - 'documentation'
      - 'docs'
  - title: '🔒 Security'
    labels:
      - 'security'
```

## Repository Settings

### Branch Protection Rules

**Main Branch Protection**:
- Require pull request reviews (2 reviewers)
- Require status checks to pass
- Require branches to be up to date
- Require linear history
- Restrict pushes to main branch
- Allow force pushes: No
- Allow deletions: No

**Status Checks**:
- CI (lint, type, test, coverage)
- Contract tests
- Catalog validation
- Security scan

### Code Owners

**CODEOWNERS** file:
```
# Global owners
* @open-mits/maintainers

# Core validation
src/mits_validator/validation.py @open-mits/core
src/mits_validator/levels/ @open-mits/core

# API and CLI
src/mits_validator/api.py @open-mits/api
src/mits_validator/cli.py @open-mits/api

# Documentation
docs/ @open-mits/docs
README.md @open-mits/docs

# CI/CD
.github/ @open-mits/devops
pyproject.toml @open-mits/devops
```

### Dependabot Configuration

**`.github/dependabot.yml`**:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 10
    reviewers:
      - "open-mits/maintainers"
    labels:
      - "dependencies"
      - "automated"
  
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 5
    reviewers:
      - "open-mits/maintainers"
    labels:
      - "dependencies"
      - "automated"
      - "github-actions"
```

## Maintenance Procedures

### Regular Maintenance

**Weekly**:
- Review and merge Dependabot PRs
- Check for security updates
- Review open issues and PRs
- Monitor CI/CD pipeline health

**Monthly**:
- Update dependencies
- Review and update documentation
- Check for performance regressions
- Review community feedback

**Quarterly**:
- Security audit
- Performance review
- Architecture review
- Roadmap update

### Dependency Updates

1. **Review Dependabot PRs**:
   ```bash
   # Check PR details
   # Review changelog
   # Test locally
   # Merge if safe
   ```

2. **Manual Updates**:
   ```bash
   # Update pyproject.toml
   # Run tests
   # Update lock file
   uv lock --upgrade
   ```

3. **Security Updates**:
   ```bash
   # Check for vulnerabilities
   uv audit
   
   # Update vulnerable dependencies
   # Test thoroughly
   # Deploy immediately
   ```

### Performance Monitoring

**Key Metrics**:
- Response time (p50, p95, p99)
- Throughput (requests/second)
- Error rate
- Memory usage
- CPU usage

**Monitoring Tools**:
- GitHub Actions metrics
- Codecov coverage reports
- Security scan results
- Performance benchmarks

### Security Maintenance

**Regular Security Tasks**:
- Review security scan results
- Update security dependencies
- Monitor for vulnerabilities
- Review access permissions

**Security Incident Response**:
1. **Assess**: Determine severity and impact
2. **Contain**: Prevent further damage
3. **Eradicate**: Remove threat
4. **Recover**: Restore normal operations
5. **Learn**: Improve security posture

## Community Management

### Issue Management

**Issue Triage**:
- Label issues appropriately
- Assign to maintainers
- Set priority levels
- Track progress

**Issue Labels**:
- `bug`: Something isn't working
- `feature`: New feature or request
- `enhancement`: Improvement to existing feature
- `documentation`: Documentation improvements
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed
- `priority: high`: High priority
- `priority: medium`: Medium priority
- `priority: low`: Low priority

### Pull Request Management

**PR Review Process**:
1. **Automated Checks**: CI/CD pipeline
2. **Code Review**: At least 2 reviewers
3. **Testing**: Comprehensive testing
4. **Documentation**: Update docs if needed
5. **Approval**: Maintainer approval required

**PR Labels**:
- `breaking-change`: Breaking change
- `feature`: New feature
- `bugfix`: Bug fix
- `documentation`: Documentation update
- `dependencies`: Dependency update
- `security`: Security-related change

### Community Guidelines

**Code of Conduct**:
- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow project guidelines

**Contributing Guidelines**:
- Fork and branch workflow
- Clear commit messages
- Comprehensive testing
- Documentation updates

## Release Notes

### Changelog Format

```markdown
## [1.0.0] - 2024-01-15

### Added
- New validation level for semantic checks
- Enhanced error reporting with location information
- Performance improvements for large files

### Changed
- Updated API response format
- Improved error messages
- Enhanced documentation

### Fixed
- Fixed memory leak in URL validation
- Resolved timeout issues with large files
- Corrected error code mapping

### Security
- Updated dependencies to address vulnerabilities
- Enhanced input validation
- Improved error handling
```

### Release Announcements

**Template**:
```markdown
# 🎉 MITS Validator v1.0.0 Released!

We're excited to announce the release of MITS Validator v1.0.0! This release includes:

## ✨ New Features
- [Feature 1]
- [Feature 2]

## 🐛 Bug Fixes
- [Fix 1]
- [Fix 2]

## 📚 Documentation
- [Doc update 1]
- [Doc update 2]

## 🔗 Links
- [Release Notes](https://github.com/open-mits/mits-validator/releases/tag/v1.0.0)
- [Documentation](https://open-mits.github.io/mits-validator/)
- [Installation Guide](https://open-mits.github.io/mits-validator/getting-started/installation/)

Thank you to all contributors! 🙏
```

## Emergency Procedures

### Security Incidents

1. **Immediate Response**:
   - Assess severity
   - Notify security team
   - Implement temporary fixes
   - Communicate with users

2. **Investigation**:
   - Root cause analysis
   - Impact assessment
   - Timeline reconstruction
   - Evidence collection

3. **Resolution**:
   - Implement permanent fix
   - Test thoroughly
   - Deploy update
   - Monitor for issues

4. **Post-Incident**:
   - Document lessons learned
   - Update procedures
   - Improve security
   - Communicate findings

### Critical Bugs

1. **Assessment**:
   - Determine impact
   - Identify affected users
   - Assess workarounds
   - Plan fix timeline

2. **Response**:
   - Implement hotfix
   - Test thoroughly
   - Deploy quickly
   - Communicate update

3. **Follow-up**:
   - Monitor for issues
   - Gather feedback
   - Document resolution
   - Prevent recurrence

## Contact Information

**Maintainers**:
- **Core Team**: core@open-mits.org
- **Security**: security@open-mits.org
- **Community**: community@open-mits.org

**Emergency Contacts**:
- **Security Issues**: security@open-mits.org
- **Critical Bugs**: maintainers@open-mits.org
- **General Questions**: community@open-mits.org

This guide ensures consistent and professional maintenance of the MITS Validator project.
