# Contributing to SEIM

Thank you for your interest in contributing to the Student Exchange Information Manager (SEIM) project! This document explains how to contribute to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How Can I Contribute?](#how-can-i-contribute)
3. [Getting Started](#getting-started)
4. [Development Process](#development-process)
5. [Style Guidelines](#style-guidelines)
6. [Commit Messages](#commit-messages)
7. [Testing](#testing)
8. [Documentation](#documentation)
9. [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

- Use the issue tracker to report bugs
- Describe the bug and include specific details to help us reproduce it
- Include the version of SEIM you're using
- Include screenshots if applicable

### Suggesting Enhancements

- Use the issue tracker to suggest enhancements
- Provide a clear and detailed explanation of the feature
- Explain why this enhancement would be useful

### Pull Requests

- Fill in the required template
- Do not include issue numbers in the PR title
- Follow the style guidelines
- Include tests for new features
- Update documentation as needed

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/seim.git
   cd seim
   ```
3. Set up your development environment:
   ```bash
   docker-compose up --build
   ```
4. Create a branch for your feature:
   ```bash
   git checkout -b feature/amazing-feature
   ```

## Development Process

1. Make your changes in your feature branch
2. Add or update tests as necessary
3. Ensure all tests pass
4. Update documentation if needed
5. Commit your changes
6. Push to your fork
7. Submit a pull request

## Style Guidelines

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use 4 spaces for indentation
- Maximum line length is 79 characters
- Use descriptive variable names
- Add docstrings to all functions and classes

### JavaScript Style Guide

- Use 2 spaces for indentation
- Use semicolons
- Use `const` and `let`, avoid `var`
- Use arrow functions where appropriate
- Add JSDoc comments for functions

### Django Specific

- Follow Django's coding style
- Use Django's built-in features when possible
- Keep views thin, move business logic to services
- Use Django's ORM efficiently

## Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests when applicable

Example:
```
Add dynamic form field validation

- Implement client-side validation for form fields
- Add server-side validation in FormHandler service
- Update tests to cover validation scenarios

Fixes #123
```

## Testing

- Write tests for all new features
- Update existing tests when modifying features
- Ensure all tests pass before submitting PR
- Aim for high test coverage (>80%)

Run tests:
```bash
docker-compose run web pytest
```

Check coverage:
```bash
docker-compose run web pytest --cov=exchange
```

## Documentation

- Update README.md if needed
- Update API documentation for new endpoints
- Add docstrings to all new functions and classes
- Update user documentation for new features
- Include examples where helpful

## Pull Request Process

1. Ensure all tests pass and coverage is maintained
2. Update documentation as necessary
3. Add a description of your changes to CHANGELOG.md
4. Request review from maintainers
5. Address feedback and make requested changes
6. Once approved, a maintainer will merge your PR

### PR Checklist

- [ ] Tests pass
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] PR description explains the changes
- [ ] No merge conflicts

## Questions?

Feel free to ask questions in issues or discussions. We're here to help!

Thank you for contributing to SEIM!
