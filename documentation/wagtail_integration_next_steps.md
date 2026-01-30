# Wagtail CMS Integration - Next Steps

## Overview

The Wagtail CMS has been successfully integrated into SEIM. This document outlines the remaining steps to complete the migration and go live with the new CMS.

## Completed

✅ Wagtail installed and configured
✅ CMS app created with all page models
✅ StreamField blocks implemented
✅ Templates created for all page types
✅ Admin interfaces configured
✅ URL routing integrated
✅ Docker configuration updated
✅ Migration commands created
✅ Documentation written

## ✅ UPDATED: Simplified Setup (November 2025)

### **NEW: One-Command Setup** ⭐

```bash
# Start Docker containers
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Restore CMS (one command does it all!)
docker-compose exec web python manage.py restore_cms

# Create superuser if needed
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

**That's it!** The CMS is now fully set up with:
- ✅ Wagtail site structure
- ✅ HomePage, Blog, Programs, FAQs pages
- ✅ UAdeC-branded content
- ✅ Rich content blocks on homepage

**📖 See [docs/CMS_RESTORE_GUIDE.md](../docs/CMS_RESTORE_GUIDE.md) for complete documentation**

### Export/Import Workflow

**Save your CMS state:**
```bash
docker-compose exec web python manage.py export_cms
```

**Restore it later:**
```bash
docker-compose exec web python manage.py import_cms --clear
```

### Legacy: Manual Setup (No Longer Needed)

<details>
<summary>Old multi-step process (click to expand)</summary>

**These steps are now automated by `restore_cms`:**

```bash
# Step 1: Setup site structure
docker-compose exec web python manage.py setup_wagtail_site

# Step 2: Populate content
docker-compose exec web python manage.py populate_uadec_content

# Step 3: Enhance homepage
docker-compose exec web python manage.py enhance_homepage
```

</details>

### Migrate Existing Forms (Optional)

If you have existing forms in `application_forms.FormType`:

```bash
# Dry run first to see what will happen
docker-compose exec web python manage.py migrate_forms_to_wagtail --dry-run

# Run the actual migration
docker-compose exec web python manage.py migrate_forms_to_wagtail
```

### Content Already Set Up ✅

The `restore_cms` command automatically creates:

**✅ Homepage** - Full UAdeC-branded landing page with:
- Hero section
- Feature cards
- Testimonials
- FAQ section
- Call-to-action blocks

**✅ Blog Posts** - 3 sample posts:
- Student testimonial from Salamanca
- Spring 2026 application announcement
- 10 tips for preparing for exchange

**✅ Exchange Programs** - 3 programs:
- Universidad de Salamanca (Spain)
- Texas A&M University (USA)
- Università di Bologna (Italy)

**✅ FAQ Pages** - 5 common questions answered

**✅ Standard Pages** - About, Contact, etc.

### Customization

To customize content:

1. Access Wagtail admin: `http://localhost:8000/cms/`
2. Navigate to Pages
3. Click "Edit" on any page
4. Modify content using drag-and-drop StreamFields
5. Click "Publish" to make changes live

**💡 After customizing, export your CMS:**
```bash
docker-compose exec web python manage.py export_cms --output cms/fixtures/production_cms.json
```

Then commit the fixture to Git so your team can restore the same content!

### 7. Test Everything

**CMS Features:**
- [ ] Create and edit pages in Wagtail admin
- [ ] Add images and documents
- [ ] Create blog posts with categories/tags
- [ ] Create forms and test submissions
- [ ] Test publishing workflow (draft → publish)
- [ ] Verify SEO metadata is rendering correctly
- [ ] Test responsive design on mobile devices

**Integration:**
- [ ] Verify Wagtail pages are accessible at correct URLs
- [ ] Test navigation between Django and Wagtail content
- [ ] Ensure authenticated pages still work (dashboard, applications, etc.)
- [ ] Test that API endpoints are not affected
- [ ] Verify media uploads work correctly

**Admin Interfaces:**
- [ ] Log into Wagtail admin (/cms/)
- [ ] Log into Django admin (/admin/)
- [ ] Verify navigation links between admins work
- [ ] Test permissions for different user roles

### 8. Remove Old Form System (After Testing)

**IMPORTANT:** Only do this after thoroughly testing the new Wagtail forms!

```bash
# This will guide you through manual removal steps
docker-compose exec web python manage.py remove_old_form_system --confirm
```

Manual steps (as output by the command):
1. Remove `application_forms` from `INSTALLED_APPS`
2. Remove django-dynforms URLs from `seim/urls.py`
3. Remove packages from `requirements.txt`:
   - `django-dynforms`
   - `crispy-bootstrap5`
   - `django-crisp-modals`
   - `django-itemlist`
4. Update `exchange.models.Program.application_form` to reference `cms.FormPage`
5. Run migrations
6. Delete `application_forms/` directory

### 9. Update README and Documentation

Update main README.md to mention Wagtail CMS:
- Add Wagtail to technology stack
- Update features list
- Add link to CMS guide
- Update architecture diagram

### 10. Performance Optimization

After going live:
- Enable Wagtail cache (if not already enabled)
- Configure image renditions for common sizes
- Set up CDN for media files (production)
- Monitor page load times
- Optimize database queries

## Troubleshooting

### Can't Access Wagtail Admin

**Problem:** 403 Forbidden or redirect loop
**Solution:**
- Ensure user has `is_staff=True`
- Or user has 'coordinator' or 'admin' role
- Check `cms/wagtail_hooks.py` for userbar restrictions

### Pages Not Showing on Site

**Problem:** 404 errors for Wagtail pages
**Solution:**
- Ensure pages are published (not draft)
- Check that Site is configured correctly (Settings → Sites)
- Verify URL routing in `seim/urls.py` has Wagtail catch-all at the end

### Media Files Not Loading

**Problem:** Images/documents return 404
**Solution:**
- Check `MEDIA_URL` and `MEDIA_ROOT` in settings
- Ensure media volume is mounted in docker-compose.yml
- Verify file permissions in Docker container

### Forms Not Receiving Submissions

**Problem:** Form submissions disappear or don't send emails
**Solution:**
- Check email configuration in settings
- Verify Celery is running for async emails
- Check FormPage email settings (to_address, from_address)
- Look for errors in application logs

## Rollback Plan

If you need to rollback the Wagtail integration:

1. Comment out `cms` from `INSTALLED_APPS`
2. Comment out Wagtail middleware
3. Remove Wagtail URL patterns from `seim/urls.py`
4. Restore old homepage template routing
5. Restart Docker containers

The database migrations can be reversed if needed:
```bash
docker-compose exec web python manage.py migrate cms zero
```

## Support

- **CMS Guide**: [documentation/cms_guide.md](cms_guide.md)
- **Architecture**: [documentation/architecture.md](architecture.md)
- **Developer Guide**: [documentation/developer_guide.md](developer_guide.md)
- **Wagtail Docs**: https://docs.wagtail.org/

## Success Criteria

The Wagtail integration is considered complete when:

- [ ] All page types can be created and edited in Wagtail admin
- [ ] Blog posts can be published with categories and tags
- [ ] Forms can be created and submissions received
- [ ] SEO metadata is working correctly
- [ ] Both admin interfaces are accessible and functional
- [ ] All existing Django app functionality is preserved
- [ ] Documentation is updated
- [ ] Team is trained on CMS usage
- [ ] Old form system is removed (after verification)

## Timeline

Recommended timeline for completion:

1. **Week 1**: Initialize Wagtail, create initial pages, test CMS features
2. **Week 2**: Migrate forms, create content, integrate with programs
3. **Week 3**: Comprehensive testing, bug fixes, documentation
4. **Week 4**: Training, go-live preparation
5. **Week 5**: Remove old form system, final optimization

## Conclusion

The Wagtail CMS integration provides SEIM with a powerful, flexible content management system. Follow these next steps carefully to ensure a smooth transition.

For questions or issues, refer to the documentation or contact the development team.

