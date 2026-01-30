# SEIM CMS Guide

## Overview

SEIM now includes a comprehensive Content Management System (CMS) powered by Wagtail, providing powerful tools for managing website content, blog posts, program pages, and dynamic forms.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Page Types](#page-types)
3. [Content Blocks](#content-blocks)
4. [Creating Pages](#creating-pages)
5. [Managing Forms](#managing-forms)
6. [Blog Management](#blog-management)
7. [SEO & Analytics](#seo--analytics)
8. [Workflows & Publishing](#workflows--publishing)
9. [Administration](#administration)

## Getting Started

### Accessing the CMS

The Wagtail CMS admin interface is available at: `http://localhost:8000/cms/`

**Access Requirements:**
- Staff users (is_staff=True)
- Coordinators and Administrators
- Users with page editing permissions

### Admin Interfaces

SEIM now has two admin interfaces:

1. **Wagtail CMS** (`/cms/`) - For content management, pages, blog posts, and forms
2. **Django Admin** (`/admin/`) - For system configuration, user management, and exchange workflows

You can switch between them using the links in the navigation menu.

## Page Types

### HomePage

The main landing page for the site with:
- Hero section (title, subtitle, CTA button, image)
- Flexible content area using StreamField blocks
- SEO optimization

**Template:** `cms/templates/cms/home_page.html`

### StandardPage

General purpose pages for about, contact, help, etc.
- Introduction text
- Flexible content body
- Optional sidebar
- Related pages section
- Full SEO support

**Template:** `cms/templates/cms/standard_page.html`

### BlogIndexPage

Container page that lists all blog posts with:
- Category filtering
- Tag filtering
- Pagination
- Search functionality

**Template:** `cms/templates/cms/blog_index_page.html`

### BlogPostPage

Individual blog posts with:
- Author attribution
- Featured image
- Categories and tags
- Rich content body
- Related posts
- Social sharing

**Template:** `cms/templates/cms/blog_post_page.html`

### ProgramIndexPage

Lists all exchange programs with:
- Grid layout
- Pagination
- Program search and filtering

**Template:** `cms/templates/cms/program_index_page.html`

### ProgramPage

Individual program pages with:
- Program details
- Rich content
- Quick information sidebar (location, duration, language, deadline)
- Integration with exchange.Program model
- Application CTAs

**Template:** `cms/templates/cms/program_page.html`

### FormPage

Dynamic forms with:
- Drag-and-drop form builder
- Multiple field types
- Email notifications
- Submission storage
- Link to exchange programs (for application forms)

**Template:** `cms/templates/cms/form_page.html`

### FAQIndexPage & FAQPage

Frequently Asked Questions pages with:
- Category organization
- Accordion UI for Q&A
- Search functionality

**Templates:** `cms/templates/cms/faq_index_page.html`, `cms/templates/cms/faq_page.html`

## Content Blocks

Wagtail StreamFields provide flexible, structured content blocks:

### Rich Text Block
Rich text editor with formatting options (headings, bold, italic, links, lists, images).

### Image Block
Images with:
- Caption
- Attribution
- Alignment options (left, center, right, full width)

### Call to Action Block
Prominent CTAs with:
- Title and text
- Button with customizable style
- Link to page or external URL

### Card Grid Block
Feature cards in grid layout:
- Configurable columns (2, 3, or 4)
- Icon, title, text per card
- Optional links

### Testimonial Block
Quotes and testimonials with:
- Quote text
- Author name and title
- Optional author image

### FAQ Block
Accordion-style Q&A sections:
- Multiple questions/answers
- Collapsible interface
- Rich text answers

### Hero Block
Large banner sections with:
- Title and subtitle
- Background image or color
- CTA button

### Video Block
Embedded videos from YouTube, Vimeo, etc. with captions.

### Document Download Block
File downloads with:
- Title and description
- Download button

### Process Steps Block
Step-by-step processes with:
- Numbered or icon steps
- Title and description per step
- Grid layout

### Two Column Block
Side-by-side content layout with flexible blocks in each column.

### Embedded Form Block
Embed a FormPage within another page.

## Creating Pages

### Basic Page Creation

1. Navigate to Wagtail admin `/cms/`
2. Click "Pages" in the left sidebar
3. Navigate to the parent page
4. Click "Add child page"
5. Select the page type
6. Fill in the required fields
7. Add content using StreamField blocks
8. Configure SEO settings in the "Promote" tab
9. Click "Publish" or "Save draft"

### Best Practices

- **Use descriptive titles**: Clear, concise titles improve SEO and navigation
- **Write meta descriptions**: 150-160 characters for search engines
- **Optimize images**: Use appropriate sizes and alt text
- **Structure content**: Use blocks to create scannable, organized content
- **Preview before publishing**: Use the preview button to check appearance

## Managing Forms

### Creating a Form

1. Create a new FormPage under the appropriate parent
2. Add an introduction
3. Add form fields using the inline editor:
   - Single line text
   - Multi-line text
   - Email
   - Number
   - URL
   - Checkbox
   - Checkboxes (multiple)
   - Dropdown
   - Radio buttons
   - Date
   - DateTime
   - File upload
4. Mark required fields
5. Configure email notifications:
   - To address
   - From address
   - Subject line
6. Set thank you message
7. (Optional) Link to an Exchange Program for application forms

### Viewing Submissions

1. Navigate to the FormPage in the admin
2. Click the "Form submissions" tab
3. View, export, or delete submissions

### Migrating from django-dynforms

A management command is provided to migrate existing forms:

```bash
# In Docker
docker-compose exec web python manage.py migrate_forms_to_wagtail --dry-run
docker-compose exec web python manage.py migrate_forms_to_wagtail

# After verification
docker-compose exec web python manage.py remove_old_form_system --confirm
```

## Blog Management

### Creating Blog Posts

1. Create a BlogIndexPage if you don't have one
2. Under the BlogIndexPage, create BlogPostPages
3. Add:
   - Published date
   - Author
   - Featured image
   - Introduction (excerpt)
   - Body content using StreamField
   - Categories and tags
4. Configure SEO settings
5. Publish

### Managing Categories

Categories are managed as Snippets:

1. Go to "Snippets" → "Blog Categories"
2. Add/edit categories
3. Assign to blog posts

### Tags

Tags are added directly to blog posts and are automatically created.

## SEO & Analytics

### SEO Configuration

Each page includes SEO fields (via wagtail-seo):

- **SEO Title**: Custom title for search engines (override page title)
- **Meta Description**: 150-160 character summary
- **Social Sharing Image**: Image for Open Graph/Twitter Cards
- **Canonical URL**: Prevent duplicate content issues

### Best Practices

- Write unique meta descriptions for each page
- Include target keywords naturally
- Use descriptive alt text for all images
- Create meaningful URL slugs
- Use header hierarchy (H1, H2, H3)
- Optimize images for web
- Keep content fresh and updated

## Workflows & Publishing

### Draft vs Live

- **Draft**: Save work in progress, not visible to public
- **Live**: Published and visible to website visitors

### Revision History

- Every save creates a revision
- View revision history in the page editor
- Compare versions
- Revert to previous versions

### Publishing Workflows

Wagtail supports approval workflows:

1. Content editors submit pages for review
2. Moderators/Admins approve or request changes
3. Approved pages are published
4. Email notifications for workflow events

Configure workflows in Settings → Workflows.

### Scheduled Publishing

Set a "Go live date/time" to automatically publish pages in the future.

## Administration

### User Roles & Permissions

**Content Editor:**
- Create and edit pages
- Submit for moderation
- Cannot publish without approval

**Moderator:**
- All editor permissions
- Approve/reject pages
- Publish pages

**Administrator:**
- All permissions
- Manage users and permissions
- Configure workflows
- Access Django admin

### Page Permissions

Set page-level permissions:
1. Navigate to page
2. Click "More" → "Privacy"
3. Choose:
   - Public (everyone)
   - Private (login required)
   - Password protected
   - Specific groups

### Image Management

Images are stored in the Wagtail media library:

- Max size: 10MB
- Supported formats: JPEG, PNG, GIF, WEBP, SVG
- Automatic format conversion
- Multiple renditions for responsive design

### Document Management

Documents (PDF, DOCX, etc.) can be uploaded:

- Max size: 50MB
- Allowed extensions configured in settings
- Download tracking
- Organize in collections

## Tips & Tricks

### Performance

- Optimize images before upload
- Use image renditions for responsive design
- Enable caching for frequently accessed pages
- Monitor page load times

### Content Strategy

- Plan page hierarchy before building
- Use consistent naming conventions
- Maintain a content calendar for blog posts
- Review and update content regularly
- Use analytics to guide content decisions

### Troubleshooting

**Problem:** Can't access Wagtail admin
- **Solution:** Ensure user has `is_staff=True` or coordinator/admin role

**Problem:** Page not appearing on site
- **Solution:** Check that page is published (not draft) and parent pages are also published

**Problem:** Images not loading
- **Solution:** Check MEDIA_URL and MEDIA_ROOT settings, ensure media volume is mounted in Docker

**Problem:** Form submissions not received
- **Solution:** Check email settings, verify SMTP configuration, check spam folder

## Further Reading

- [Wagtail Documentation](https://docs.wagtail.org/)
- [StreamField Guide](https://docs.wagtail.org/en/stable/topics/streamfield.html)
- [SEO Best Practices](https://docs.wagtail.org/en/stable/advanced_topics/performance.html)
- [SEIM Developer Guide](developer_guide.md)
- [SEIM Architecture](architecture.md)

## Support

For technical support or questions:
- Check the [Troubleshooting Guide](troubleshooting.md)
- Review the [Developer Guide](developer_guide.md)
- Contact the development team

