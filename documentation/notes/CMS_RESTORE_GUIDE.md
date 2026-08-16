# CMS Restore Guide - Simple Workflow

## 🚀 Quick Start (After Database Reset)

### Option 1: Single Command (Recommended)

**Just run this one command:**

```bash
docker-compose exec web python manage.py restore_cms
```

That's it! This command will:
1. ✅ Set up Wagtail site structure  
2. ✅ Populate UAdeC content (programs, blog posts, FAQs)
3. ✅ Enhance the homepage with rich content blocks

Then visit: **http://localhost:8000/**

---

### Option 2: Export/Import Workflow

**First time setup (export your working CMS):**

```bash
# After you have CMS set up the way you want it
docker-compose exec web python manage.py export_cms
```

This creates: `cms/fixtures/cms_content.json`

**Later restore (after database reset):**

```bash
# Run migrations first
docker-compose exec web python manage.py migrate

# Import your saved CMS content
docker-compose exec web python manage.py import_cms --clear
```

Done! Your CMS is restored exactly as it was.

---

## 📋 Command Reference

### `restore_cms` - All-in-one restore

```bash
# Full restore (recommended)
docker-compose exec web python manage.py restore_cms

# Skip specific steps if already done
docker-compose exec web python manage.py restore_cms --skip-setup
docker-compose exec web python manage.py restore_cms --skip-populate
docker-compose exec web python manage.py restore_cms --skip-enhance
```

### `export_cms` - Save your CMS content

```bash
# Export to default location
docker-compose exec web python manage.py export_cms

# Export to custom file
docker-compose exec web python manage.py export_cms --output backups/cms_backup_2025.json
```

### `import_cms` - Restore saved content

```bash
# Import from default location
docker-compose exec web python manage.py import_cms

# Clear existing pages first (recommended)
docker-compose exec web python manage.py import_cms --clear

# Import from custom file
docker-compose exec web python manage.py import_cms --input backups/cms_backup_2025.json
```

---

## 🔄 Common Scenarios

### After `docker-compose down -v` (database wiped)

```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py restore_cms
```

### After pulling new code

```bash
docker-compose down
docker-compose build
docker-compose up -d
docker-compose exec web python manage.py migrate

# If CMS is blank:
docker-compose exec web python manage.py import_cms --clear
```

### Creating a backup before changes

```bash
docker-compose exec web python manage.py export_cms --output backups/cms_before_changes.json
```

### Reverting to backup

```bash
docker-compose exec web python manage.py import_cms --input backups/cms_before_changes.json --clear
```

---

## 🎯 Workflow Comparison

| Method | First Setup | After DB Reset | Pros | Cons |
|--------|-------------|----------------|------|------|
| **restore_cms** | ✅ Fast | ✅ Fast | Simple, one command | Generates same content each time |
| **export/import** | ✅ One-time export | ⚡ Instant | Preserves exact state, custom content | Requires initial export |

---

## 💡 Best Practice Workflow

1. **Initial setup:**
   ```bash
   docker-compose exec web python manage.py restore_cms
   ```

2. **Customize your CMS** via http://localhost:8000/cms/

3. **Export your customized content:**
   ```bash
   docker-compose exec web python manage.py export_cms --output cms/fixtures/production_cms.json
   ```

4. **Commit the fixture to Git:**
   ```bash
   git add cms/fixtures/production_cms.json
   git commit -m "CMS content fixture"
   ```

5. **Anyone can now restore:**
   ```bash
   docker-compose exec web python manage.py import_cms --input cms/fixtures/production_cms.json --clear
   ```

---

## 🔍 Troubleshooting

### "HomePage not found" error

```bash
# Run the setup first
docker-compose exec web python manage.py setup_wagtail_site

# Then try restore again
docker-compose exec web python manage.py restore_cms --skip-setup
```

### Import fails with "Integrity error"

```bash
# Clear existing pages first
docker-compose exec web python manage.py import_cms --clear
```

### Want to start completely fresh

```bash
# Delete all CMS pages (keeps root)
docker-compose exec web python manage.py shell
>>> from wagtail.models import Page
>>> root = Page.objects.get(depth=1)
>>> for page in root.get_children():
...     page.delete()
>>> exit()

# Then restore
docker-compose exec web python manage.py restore_cms
```

---

## 📦 What Gets Exported/Imported

The export includes:
- ✅ All page structure (HomePage, Blog, Programs, FAQs, etc.)
- ✅ All content (text, StreamField blocks, rich text)
- ✅ Page hierarchy and relationships
- ✅ Published/draft states
- ✅ Blog categories and tags
- ✅ Site configuration

**Not included** (by default):
- ❌ Images (wagtailimages.Image) - too large for fixtures
- ❌ User accounts
- ❌ Form submissions

---

## 🎓 Summary

**After any database reset:**

```bash
docker-compose exec web python manage.py restore_cms
```

**That's the only command you need to remember!** 🎉

---

**Created:** November 25, 2025  
**Status:** ✅ Production Ready

