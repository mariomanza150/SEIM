# SEIM Internationalization (i18n)

This directory contains translation files for the SEIM application.

## Supported Languages

- **English (en)** - Default language
- **Spanish (es)** - Español
- **French (fr)** - Français
- **German (de)** - Deutsch

## Directory Structure

```
locale/
├── README.md
├── es/
│   └── LC_MESSAGES/
│       ├── django.po      # Translation strings
│       └── django.mo      # Compiled translations
├── fr/
│   └── LC_MESSAGES/
│       ├── django.po
│       └── django.mo
└── de/
    └── LC_MESSAGES/
        ├── django.po
        └── django.mo
```

## Prerequisites

Install GNU gettext tools:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install gettext
```

**macOS:**
```bash
brew install gettext
brew link gettext --force
```

**Docker (add to Dockerfile):**
```dockerfile
RUN apt-get update && apt-get install -y gettext
```

## Generating Translation Files

### 1. Extract translatable strings

Extract all strings marked with `gettext()`, `_()`, `{% trans %}`, etc.:

```bash
# Generate .po files for all languages
python manage.py makemessages -l es -l fr -l de --ignore=venv --ignore=node_modules

# Generate JavaScript translations
python manage.py makemessages -d djangojs -l es -l fr -l de
```

### 2. Translate strings

Edit the `.po` files in each language directory:
- `locale/es/LC_MESSAGES/django.po`
- `locale/fr/LC_MESSAGES/django.po`
- `locale/de/LC_MESSAGES/django.po`

**Example .po entry:**
```po
#: exchange/models.py:42
msgid "Application submitted successfully"
msgstr "Solicitud enviada exitosamente"  # Spanish translation
```

### 3. Compile translations

Compile `.po` files to binary `.mo` files:

```bash
python manage.py compilemessages
```

## Marking Strings for Translation

### Python Code

```python
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

# In views/forms
message = _("Welcome to SEIM")

# In model fields (use lazy)
verbose_name = gettext_lazy("Application")
```

### Templates

```django
{% load i18n %}

{# Simple translation #}
<h1>{% trans "Welcome" %}</h1>

{# Translation with context #}
{% blocktrans %}
  Hello {{ user }}, you have {{ count }} applications.
{% endblocktrans %}
```

### JavaScript

```javascript
// Use Django's JavaScript catalog
const translatedText = gettext("Submit Application");
```

## Language Detection

The application automatically detects the user's language from:
1. URL prefix (e.g., `/es/programs/`)
2. Session variable
3. Cookie (`django_language`)
4. Browser's Accept-Language header

## Switching Languages

Users can switch languages via:
1. Language selector in navigation
2. URL with language prefix
3. API endpoint: `POST /api/set-language/`

## Translation Workflow

### For Developers

1. Mark new strings with translation functions
2. Run `makemessages` to update `.po` files
3. Commit `.po` files to version control
4. Let translators update translations

### For Translators

1. Edit `.po` files with a PO editor (e.g., Poedit, Lokalize)
2. Save and test translations
3. Submit updated `.po` files

### For Deployment

1. Run `compilemessages` before deployment
2. `.mo` files are automatically loaded by Django
3. Restart application to load new translations

## Testing Translations

### Via URL

```
http://localhost:8000/es/  # Spanish
http://localhost:8000/fr/  # French
http://localhost:8000/de/  # German
```

### Via Language Switcher

```html
<form action="{% url 'set_language' %}" method="post">
  {% csrf_token %}
  <select name="language">
    <option value="en">English</option>
    <option value="es">Español</option>
    <option value="fr">Français</option>
    <option value="de">Deutsch</option>
  </select>
  <button type="submit">Switch</button>
</form>
```

### In Tests

```python
from django.utils import translation

def test_spanish_translation():
    with translation.override('es'):
        text = _("Welcome")
        assert text == "Bienvenido"
```

## Best Practices

### DO

✅ Use `gettext_lazy()` for model fields and class-level strings
✅ Keep translations in `.po` files, never hardcode
✅ Test all languages before deployment
✅ Use context when translating ambiguous terms
✅ Provide translator comments for complex strings

### DON'T

❌ Don't concatenate translatable strings
❌ Don't translate URLs or technical terms
❌ Don't forget to compile messages before deployment
❌ Don't commit `.mo` files (they're generated)
❌ Don't use translation functions in migrations

## Common Translation Contexts

### Application States
- draft, submitted, approved, rejected, withdrawn

### User Roles
- student, coordinator, administrator, reviewer

### Document Types
- transcript, passport, visa, recommendation_letter

### Grade Scales
- US GPA, ECTS, German Scale

### Notifications
- Application status changes
- Document verification
- Deadline reminders

## Troubleshooting

### Translations Not Showing

1. Check `USE_I18N = True` in settings
2. Verify `LocaleMiddleware` is in `MIDDLEWARE`
3. Run `compilemessages`
4. Restart Django server
5. Clear browser cache

### Missing Translations

1. Run `makemessages` to update `.po` files
2. Check for syntax errors in `.po` files
3. Verify `fuzzy` flag is removed from translations
4. Recompile messages

### gettext Not Found

1. Install gettext tools (see Prerequisites)
2. Add gettext to PATH
3. Verify with `which gettext` (Unix) or `where gettext` (Windows)

## Resources

- [Django Internationalization Documentation](https://docs.djangoproject.com/en/5.2/topics/i18n/)
- [GNU gettext Manual](https://www.gnu.org/software/gettext/manual/)
- [Poedit - PO File Editor](https://poedit.net/)
- [Transifex - Translation Platform](https://www.transifex.com/)

## Maintenance

- Update translations when adding new features
- Review translations quarterly for accuracy
- Use native speakers for final review
- Keep `.po` files in sync across languages

