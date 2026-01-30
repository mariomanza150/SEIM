# CMS Documentation Index

## 📚 Quick Navigation

### **Start Here**

- **[CMS_RESTORE_GUIDE.md](CMS_RESTORE_GUIDE.md)** ⭐  
  **NEW simplified workflow with one-command restore and export/import**
  - Single command to restore entire CMS
  - Export/import for backups and team synchronization
  - Troubleshooting guide

- **[CMS_QUICK_START.md](CMS_QUICK_START.md)**  
  Quick reference for day-to-day CMS usage
  - Accessing CMS admin
  - Editing content
  - Management commands
  - Common tasks

### **Overview & Status**

- **[CMS_STATUS_SUMMARY.md](CMS_STATUS_SUMMARY.md)**  
  Current state of the CMS, what's working, and content statistics

- **[CMS_LANDING_PAGE_OVERVIEW.md](CMS_LANDING_PAGE_OVERVIEW.md)**  
  Detailed overview of the UAdeC landing page structure and features

- **[CMS_HOMEPAGE_CONTENT_MAP.md](CMS_HOMEPAGE_CONTENT_MAP.md)**  
  Visual map of homepage content blocks and structure

### **Technical Documentation**

- **[CMS_FIX_REPORT.md](CMS_FIX_REPORT.md)**  
  Technical details of fixes applied to the CMS

- **[CMS_ASSESSMENT_SUMMARY.md](CMS_ASSESSMENT_SUMMARY.md)**  
  Initial CMS assessment and implementation plan

- **[CMS_CONTENT_ASSESSMENT.md](CMS_CONTENT_ASSESSMENT.md)**  
  Content strategy and assessment

- **[CMS_COLOR_SCHEME_UPDATE.md](CMS_COLOR_SCHEME_UPDATE.md)**  
  UAdeC branding and color scheme implementation

---

## 🚀 Common Use Cases

### I just reset my database
→ **[CMS_RESTORE_GUIDE.md](CMS_RESTORE_GUIDE.md)** - Run `restore_cms` command

### I want to edit content
→ **[CMS_QUICK_START.md](CMS_QUICK_START.md)** - Section on editing content

### I need to understand the page structure
→ **[CMS_LANDING_PAGE_OVERVIEW.md](CMS_LANDING_PAGE_OVERVIEW.md)** - Complete structure

### I want to backup my CMS
→ **[CMS_RESTORE_GUIDE.md](CMS_RESTORE_GUIDE.md)** - Export/import section

### I need to see what's currently published
→ **[CMS_STATUS_SUMMARY.md](CMS_STATUS_SUMMARY.md)** - Current content stats

---

## 🎯 Key Commands

```bash
# Restore entire CMS (one command does it all!)
docker-compose exec web python manage.py restore_cms

# Export CMS content for backup
docker-compose exec web python manage.py export_cms

# Import CMS content from backup
docker-compose exec web python manage.py import_cms --clear

# View current CMS content
docker-compose exec web python manage.py show_cms_content
```

---

## 📖 Documentation Structure

```
docs/
├── CMS_RESTORE_GUIDE.md          ⭐ Primary workflow guide (START HERE)
├── CMS_QUICK_START.md            📘 Daily usage reference
├── CMS_STATUS_SUMMARY.md         📊 Current status & content
├── CMS_LANDING_PAGE_OVERVIEW.md  🏠 Page structure details
├── CMS_HOMEPAGE_CONTENT_MAP.md   🗺️  Content block map
├── CMS_FIX_REPORT.md             🔧 Technical fixes
├── CMS_ASSESSMENT_SUMMARY.md     📋 Implementation plan
├── CMS_CONTENT_ASSESSMENT.md     ✍️  Content strategy
└── CMS_COLOR_SCHEME_UPDATE.md    🎨 Branding guide
```

---

## 🆕 What's New (November 25, 2025)

### Simplified CMS Workflow

**Before:**
```bash
docker-compose exec web python manage.py setup_wagtail_site
docker-compose exec web python manage.py populate_uadec_content
docker-compose exec web python manage.py enhance_homepage
```

**Now:**
```bash
docker-compose exec web python manage.py restore_cms
```

### New Commands

- ✅ `restore_cms` - All-in-one restore command
- ✅ `export_cms` - Export CMS to fixture file
- ✅ `import_cms` - Import CMS from fixture file

### Benefits

- ⚡ **Faster setup** - One command instead of three
- 💾 **Easy backups** - Export/import your exact CMS state
- 🤝 **Team sync** - Share CMS content via Git fixtures
- 🔄 **Quick restore** - Instant recovery after database reset

---

## 🌐 URLs

- **Public Landing Page**: http://localhost:8000/
- **CMS Admin**: http://localhost:8000/cms/
- **Django Admin**: http://localhost:8000/seim/admin/

---

**Last Updated:** November 25, 2025  
**Status:** ✅ All documentation current and verified

