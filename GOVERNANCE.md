# Project Governance

## Overview

MITS Validator is an open-source project under the Apache 2.0 license. This document outlines how the project is governed and how decisions are made.

## Project Structure

### Maintainers

The project is maintained by the **open-mits** organization with the following roles:

- **Project Lead**: Overall project direction and major decisions
- **Core Maintainers**: Code review, releases, and technical decisions
- **Community Maintainers**: Documentation, community support, and outreach

### Decision Making

#### Technical Decisions
- **Code changes**: Require approval from at least 2 core maintainers
- **Architecture changes**: Require consensus among core maintainers
- **Breaking changes**: Require discussion and approval from project lead

#### Community Decisions
- **Governance changes**: Require community input and maintainer consensus
- **New maintainers**: Nominated by existing maintainers, community input welcome
- **Project direction**: Open discussion with community input

## MITS Specification Changes

### Rule Changes
When modifying validation rules or adding new checks:

1. **Reference official sources**: Link to official MITS documentation
2. **Community discussion**: Open issue for discussion
3. **Impact assessment**: Document breaking changes and migration path
4. **Testing**: Comprehensive test coverage for new rules
5. **Documentation**: Update all relevant documentation

### Advisory Group
We plan to establish an advisory group including:
- MITS specification experts
- Industry representatives
- Property technology professionals
- Open source community members

## Release Management

### Versioning
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Process
1. **Development**: Features developed in feature branches
2. **Testing**: Comprehensive testing including integration tests
3. **Review**: Code review by maintainers
4. **Release**: Tagged releases with release notes
5. **Documentation**: Updated documentation and changelog

### Release Schedule
- **Patch releases**: As needed for critical fixes
- **Minor releases**: Monthly or as features are ready
- **Major releases**: Planned with community input

## Community Guidelines

### Contributing
- Follow the [Contributing Guidelines](CONTRIBUTING.md)
- Respect the [Code of Conduct](CODE_OF_CONDUCT.md)
- Use conventional commits for clear history
- Provide tests for new features

### Communication
- **Issues**: Bug reports and feature requests
- **Discussions**: General questions and community chat
- **Security**: Private reporting via security@example.org
- **Maintainers**: Direct contact for urgent matters

## Conflict Resolution

### Disagreements
1. **Discussion**: Open, respectful discussion in issues/discussions
2. **Mediation**: Maintainers can mediate disputes
3. **Escalation**: Project lead can make final decisions
4. **Appeals**: Community can appeal through governance process

### Code of Conduct Violations
- Report to maintainers privately
- Investigation by maintainer team
- Appropriate action taken
- Appeals process available

## Project Roadmap

### Phase 1: Foundation (Current)
- ✅ Repository setup and CI/CD
- ✅ Basic FastAPI service
- ✅ CLI interface
- ✅ Testing framework

### Phase 2: Core Validation
- XSD conformance validation
- Basic XML structure validation
- Error reporting and documentation

### Phase 3: Business Rules
- Schematron rule implementation
- MITS-specific business logic
- Comprehensive test suite

### Phase 4: Advanced Features
- Semantic consistency checks
- Performance optimization
- Advanced reporting
- Integration tools

## Getting Involved

### Ways to Contribute
- **Code**: Bug fixes, features, improvements
- **Documentation**: Guides, examples, API docs
- **Testing**: Test cases, bug reports
- **Community**: Help others, answer questions
- **Governance**: Participate in discussions

### Becoming a Maintainer
- Consistent contributions over time
- Understanding of project goals
- Community respect and trust
- Nomination by existing maintainers
- Community input and approval

## Contact

- **General**: GitHub discussions
- **Security**: security@example.org
- **Maintainers**: opensource@example.org
- **Project Lead**: Available through GitHub

---

This governance document is living and will evolve with the project. Community input is welcome and encouraged.
