# SEIM Documentation Maintenance Guide

**Last Updated:** November 20, 2025  
**Version:** 1.0

## Overview

This guide provides comprehensive procedures for maintaining, updating, and organizing the SEIM documentation. It is intended for developers and documentation maintainers to ensure consistency, accuracy, and accessibility of project documentation.

---

## Table of Contents

- [Documentation Structure](#documentation-structure)
- [Update Procedures](#update-procedures)
- [Auto-Generated Documentation](#auto-generated-documentation)
- [Archiving Guidelines](#archiving-guidelines)
- [Link Management](#link-management)
- [Version Control](#version-control)
- [Review Schedule](#review-schedule)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Documentation Structure

### Main Documentation Directory

```
documentation/
├── README.md                           # Documentation index and overview
├── developer_guide.md                  # Development workflows and practices
├── architecture.md                     # System architecture and design
├── business_rules.md                   # Business logic and rules
├── deployment.md                       # Production deployment guide
├── api_documentation.md                # API endpoints reference
├── form_builder_guide.md               # Form Builder comprehensive guide
├── grade_translation_user_guide.md     # Grade translation system guide
├── testing.md                          # Testing strategies
├── troubleshooting.md                  # Common issues and solutions
├── changelog.md                        # Release notes
├── roadmap.md                          # Future features
├── backlog.md                          # Current tasks
├── generated/                          # Auto-generated docs
│   ├── code_documentation.md
│   └── database_schema.md
├── archive/                            # Historical documentation
│   ├── README.md
│   ├── session_2025_11/
│   ├── session_2025_10_18/
│   ├── session_2025_01/
│   ├── form_builder_development/
│   ├── phase_2_summaries/
│   └── audit_reports/
├── implementation_plans/               # Feature implementation plans
├── wireframes/                         # UI/UX wireframes
└── sphinx/                             # Sphinx HTML documentation
    ├── source/
    └── build/html/
```

### Root Documentation Files

```
/
├── README.md                           # Main project README
├── CONTRIBUTING.md                     # Contribution guidelines
├── RELEASE_NOTES.md                    # Release announcements
└── documentation-cleanup.plan.md       # Documentation plans
```

---

## Update Procedures

### When to Update Documentation

Update documentation when:

1. **New Features**: Adding or modifying features
2. **Architecture Changes**: System design updates
3. **API Changes**: New endpoints or modifications
4. **Bug Fixes**: Significant fixes that affect usage
5. **Configuration Changes**: New environment variables or settings
6. **Deployment Changes**: Updates to deployment procedures
7. **Dependencies**: Major dependency updates

### Documentation Update Checklist

When making updates:

- [ ] Update relevant markdown files
- [ ] Update version numbers and dates
- [ ] Update cross-references and links
- [ ] Regenerate auto-generated documentation
- [ ] Update changelog
- [ ] Review for consistency
- [ ] Test any code examples
- [ ] Update archive index if archiving

### Step-by-Step Update Process

#### 1. Identify Affected Documentation

```bash
# Search for references to changed component
grep -r "ComponentName" documentation/
```

#### 2. Update Core Files

- **Architecture**: Add/update component descriptions
- **Developer Guide**: Update workflows and commands
- **API Documentation**: Add/update endpoints
- **Business Rules**: Update business logic descriptions

#### 3. Update Related Files

- **README.md**: Update feature lists and links
- **Changelog**: Add entry for changes
- **Testing Guide**: Update test procedures
- **Deployment Guide**: Update if deployment affected

#### 4. Regenerate Auto-Generated Docs

```bash
# Inside Docker
make docs-all
```

#### 5. Verify Links

Check all internal links still work:

```bash
# Search for markdown links
grep -r "\[.*\](.*\.md)" documentation/
```

#### 6. Update Version and Date

Update "Last Updated" and version numbers in affected files.

---

## Auto-Generated Documentation

### Types of Auto-Generated Documentation

1. **API Documentation**: OpenAPI/Swagger schema
2. **Code Documentation**: Code structure and docstrings
3. **Database Schema**: Model definitions and relationships
4. **Sphinx HTML**: Comprehensive HTML documentation

### Generation Commands

#### Generate All Documentation

```bash
# Run inside Docker
make docs-all
```

This generates:
- Code documentation
- Database schema documentation
- Sphinx HTML documentation

#### Individual Generation

```bash
# Generate code documentation only
docker-compose exec web python manage.py generate_docs --include-code

# Generate database documentation only
docker-compose exec web python manage.py generate_docs --include-db

# Build Sphinx HTML documentation
make docs-sphinx-docker
```

### Generated File Locations

- **Code Documentation**: `documentation/generated/code_documentation.md`
- **Database Schema**: `documentation/generated/database_schema.md`
- **Sphinx HTML**: `documentation/sphinx/build/html/`
- **API Schema**: `api_schema.yaml` (root directory)

### When to Regenerate

Regenerate documentation when:

- Models are added or changed
- New apps are created
- Docstrings are updated
- API endpoints are modified
- Database schema changes

### Regeneration Schedule

- **After each feature**: Regenerate affected docs
- **Before releases**: Full regeneration
- **Monthly**: Routine full regeneration
- **After major refactors**: Full regeneration

---

## Archiving Guidelines

### What to Archive

Archive documentation that is:

- Session summaries and completion reports
- Development phase documentation
- Feature development tracking docs
- Historical analysis and proposals
- Outdated implementation plans
- Superseded guides

### What NOT to Archive

Keep in main documentation:

- Current user guides
- Active architecture documentation
- Current API reference
- Active business rules
- Deployment procedures
- Contributing guidelines

### Archive Organization

#### By Date/Session

```
archive/session_YYYY_MM_DD/
├── README.md
├── session_summary.md
├── feature_reports.md
└── completion_summaries.md
```

#### By Feature

```
archive/feature_name_development/
├── README.md
├── analysis.md
├── implementation_plan.md
├── status_tracking.md
└── completion_summary.md
```

#### By Phase

```
archive/phase_N_summaries/
├── README.md
├── phase_reports.md
└── deployment_guides.md
```

### Archiving Process

1. **Create Archive Directory**

```bash
mkdir -p documentation/archive/session_YYYY_MM_DD
```

2. **Move Files**

```bash
mv FILE.md documentation/archive/session_YYYY_MM_DD/
```

3. **Create Archive README**

Create `README.md` in archive directory documenting:
- What is archived
- Date range
- Context and purpose
- Key highlights

4. **Update Archive Index**

Update `documentation/archive/README.md` with new archive entry.

5. **Verify Main Docs**

Ensure main documentation still references current information.

---

## Link Management

### Internal Link Conventions

Use relative paths for internal links:

```markdown
<!-- Within documentation/ directory -->
[Developer Guide](developer_guide.md)

<!-- From root to documentation/ -->
[Architecture](documentation/architecture.md)

<!-- To archive -->
[Archive](archive/README.md)
```

### Link Verification

#### Manual Verification

```bash
# Find all markdown links
grep -r "\[.*\](.*\.md)" documentation/

# Check if files exist
find documentation/ -name "*.md"
```

#### Automated Verification

Use link checkers:

```bash
# Install markdown-link-check
npm install -g markdown-link-check

# Check links
markdown-link-check documentation/*.md
```

### Fixing Broken Links

When moving or renaming files:

1. **Search for references**:
   ```bash
   grep -r "old_filename.md" documentation/
   ```

2. **Update all references**

3. **Verify with grep**:
   ```bash
   grep -r "new_filename.md" documentation/
   ```

### Link Patterns to Avoid

- Absolute paths: `/home/user/project/docs/file.md`
- External links for internal docs
- Links to temporary files
- Links with spaces (use hyphens)

---

## Version Control

### Documentation Versioning

#### Version Number Format

`MAJOR.MINOR`

- **MAJOR**: Significant restructuring or major updates
- **MINOR**: Regular updates, new sections, corrections

Current Version: **2.2** (as of November 20, 2025)

#### When to Increment Version

**MAJOR (X.0)**:
- Complete documentation overhaul
- Major restructuring
- New documentation system

**MINOR (X.Y)**:
- Adding new guides
- Significant updates to existing docs
- Archive reorganization

#### Version Tracking

Update version in:
- `documentation/README.md`
- Major documentation files
- Changelog

### Git Best Practices

#### Commit Messages

```bash
# Good commit messages
docs: add Form Builder guide
docs: update architecture with grades app
docs: archive November 2025 session files
docs: regenerate API documentation

# Bad commit messages
update docs
fix
docs
```

#### Commit Frequency

- Commit documentation changes with related code changes
- Separate doc-only updates into their own commits
- Don't combine unrelated documentation updates

#### Documentation Branches

For large documentation updates:

```bash
# Create documentation branch
git checkout -b docs/major-update

# Make changes
# ...

# Commit and push
git add documentation/
git commit -m "docs: comprehensive update for v2.2"
git push origin docs/major-update

# Create pull request
```

---

## Review Schedule

### Regular Reviews

#### Weekly

- [ ] Check for outdated "Last Updated" dates
- [ ] Review new feature documentation
- [ ] Verify recent code changes have docs

#### Monthly

- [ ] Full link verification
- [ ] Regenerate all auto-generated docs
- [ ] Review and archive completed session files
- [ ] Update changelog
- [ ] Check for outdated version numbers

#### Quarterly

- [ ] Comprehensive documentation review
- [ ] Archive review and cleanup
- [ ] User guide accuracy verification
- [ ] Screenshot and diagram updates
- [ ] External link verification

#### Annually

- [ ] Major version update consideration
- [ ] Complete restructuring review
- [ ] Archive consolidation
- [ ] Documentation system evaluation

### Review Checklist

Use this checklist for periodic reviews:

#### Accuracy
- [ ] All features documented correctly
- [ ] Code examples work as shown
- [ ] Commands produce expected results
- [ ] Screenshots are current
- [ ] Version numbers are correct

#### Completeness
- [ ] All features documented
- [ ] All apps have documentation
- [ ] All APIs documented
- [ ] Deployment procedures complete
- [ ] Troubleshooting covers common issues

#### Consistency
- [ ] Formatting is consistent
- [ ] Terminology is consistent
- [ ] Link format is consistent
- [ ] Code block formatting consistent
- [ ] Header levels consistent

#### Accessibility
- [ ] Clear table of contents
- [ ] Good navigation structure
- [ ] Search-friendly headings
- [ ] Examples are clear
- [ ] Links work correctly

---

## Best Practices

### Writing Guidelines

#### Style

- **Be clear and concise**: Avoid unnecessary jargon
- **Use active voice**: "Click the button" not "The button should be clicked"
- **Be specific**: Provide exact commands and paths
- **Include examples**: Show, don't just tell
- **Use consistent terminology**: Don't alternate between "form builder" and "form creator"

#### Formatting

**Headers**:
```markdown
# Main Title (H1) - Once per document
## Section (H2) - Major sections
### Subsection (H3) - Subsections
#### Sub-subsection (H4) - Details
```

**Code Blocks**:
````markdown
```language
code here
```
````

**Lists**:
```markdown
- Unordered item
- Another item

1. Ordered item
2. Another item
```

**Tables**:
```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

#### Code Examples

- **Always test**: Verify examples work
- **Include context**: Show necessary imports/setup
- **Comment complex code**: Add inline comments
- **Show expected output**: Include results

#### Screenshots and Diagrams

- **Keep updated**: Review quarterly
- **Use descriptive names**: `form-builder-interface.png`
- **Include alt text**: For accessibility
- **Store organized**: In `documentation/images/`

### Documentation Templates

#### Feature Documentation Template

```markdown
# Feature Name

**Version**: X.Y  
**Last Updated**: YYYY-MM-DD

## Overview

Brief description of the feature.

## User Guide

How to use the feature.

## Technical Details

Implementation details.

## API Reference

Related API endpoints.

## Examples

Code examples.

## Troubleshooting

Common issues and solutions.
```

#### Archive README Template

```markdown
# Session/Feature YYYY-MM-DD

Brief description of what's archived.

## Contents

- File 1 - Description
- File 2 - Description

## Context

Background information.

## Key Highlights

- Major achievement 1
- Major achievement 2

---

**Archive Date**: YYYY-MM-DD  
**Period**: Date range
```

---

## Troubleshooting

### Common Issues

#### Sphinx Build Fails

**Issue**: Sphinx build produces errors

**Solutions**:
```bash
# Clear Sphinx build directory
rm -rf documentation/sphinx/build/

# Rebuild
make docs-sphinx-docker

# If errors persist, check for:
# - Missing docstrings
# - Syntax errors in .rst files
# - Missing referenced files
```

#### Links Not Working

**Issue**: Internal links broken

**Solutions**:
1. Verify file exists at referenced path
2. Check for typos in filename
3. Ensure relative paths are correct
4. Update links if file was moved

#### Generated Docs Empty

**Issue**: Generated documentation is empty or incomplete

**Solutions**:
```bash
# Ensure Django is running
docker-compose up -d

# Clear any caches
docker-compose exec web python manage.py clearcache

# Regenerate
make docs-all

# Check for model/app import errors
docker-compose exec web python manage.py check
```

#### Out of Sync Documentation

**Issue**: Docs don't match current codebase

**Solutions**:
1. Review recent code changes
2. Update relevant documentation
3. Regenerate auto-generated docs
4. Update version numbers and dates

### Getting Help

If you encounter documentation issues:

1. **Check this guide**: Review relevant sections
2. **Check recent changes**: `git log -- documentation/`
3. **Search archives**: Past issues may have solutions
4. **Ask team**: Reach out to documentation maintainers
5. **Create issue**: Document new issues for future reference

---

## Maintenance Tools

### Useful Commands

```bash
# Find all documentation files
find documentation/ -name "*.md"

# Count total documentation files
find documentation/ -name "*.md" | wc -l

# Find recently modified docs
find documentation/ -name "*.md" -mtime -7

# Search documentation for term
grep -r "search term" documentation/

# List documentation by size
du -sh documentation/*/ | sort -h

# Check for broken links (requires tool)
markdown-link-check documentation/**/*.md
```

### Scripts

Location: `scripts/documentation/`

- `generate_all_docs.sh` - Generate all documentation
- `check_links.sh` - Verify all internal links
- `update_dates.sh` - Update "Last Updated" dates
- `archive_session.sh` - Archive session documents

---

## Contact & Support

### Documentation Maintainers

- **Primary**: SEIM Development Team
- **Email**: dev@seim.local
- **Repository**: GitHub Issues for documentation

### Contributing to Documentation

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on contributing to project documentation.

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-20 | 1.0 | Initial documentation maintenance guide created |

---

**Maintained By**: SEIM Development Team  
**Next Review**: December 20, 2025

