<!--
File: docs/TESTING.md
Title: Testing Guide
Purpose: Explain how to write, run, and troubleshoot tests for the SEIM project.
-->

# Testing Guide

## Purpose
This guide explains how to write, run, and troubleshoot tests for the SEIM project, including test types, coverage, and best practices.

## Revision History
| Date       | Author              | Description                                 |
|------------|---------------------|---------------------------------------------|
| 2025-05-31 | Documentation Team  | Initial version, added template compliance, title, purpose, and revision history. |

## Table of Contents
- [Test Types](#test-types)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Coverage](#test-coverage)
- [Troubleshooting](#troubleshooting)

## Test Types
- **Unit Tests:** Test individual functions, models, and services.
- **Integration Tests:** Test workflows, API endpoints, and form submissions.
- **Frontend Tests:** (Planned) For JavaScript modules and UI interactions. *No frontend tests exist at this moment; this is a placeholder for future work.*

## Running Tests

### With Docker (Recommended)
```