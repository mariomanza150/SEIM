"""
Script to update static file paths after reorganization.
Updates template references to static files to use the new organized structure.
"""

import os
import re
from pathlib import Path


def update_static_paths(file_path, dry_run=True):
    """Update static file paths in a single file."""
    updates = []
    
    # Define path mappings
    path_mappings = {
        # CSS files
        r"{% static 'css/style\.css' %}": "{% static 'exchange/css/pages/style.css' %}",
        r"{% static 'css/custom-variables\.css' %}": "{% static 'exchange/css/components/custom-variables.css' %}",
        r"{% static 'css/datatables-animations\.css' %}": "{% static 'exchange/css/vendor/datatables-animations.css' %}",
        r"{% static 'css/datatables-custom\.css' %}": "{% static 'exchange/css/vendor/datatables-custom.css' %}",
        
        # JS files
        r"{% static 'js/jquery-3\.7\.1\.js' %}": "{% static 'exchange/js/vendor/jquery-3.7.1.js' %}",
        r"{% static 'js/datatables-config\.js' %}": "{% static 'exchange/js/vendor/datatables-config.js' %}",
        r"{% static 'js/exchange\.js' %}": "{% static 'exchange/js/pages/exchange.js' %}",
        r"{% static 'js/advanced-filters\.js' %}": "{% static 'exchange/js/components/advanced-filters.js' %}",
        r"{% static 'js/bulk-actions-enhanced\.js' %}": "{% static 'exchange/js/components/bulk-actions-enhanced.js' %}",
        r"{% static 'js/global-search\.js' %}": "{% static 'exchange/js/components/global-search.js' %}",
        r"{% static 'js/keyboard-navigation\.js' %}": "{% static 'exchange/js/components/keyboard-navigation.js' %}",
        r"{% static 'js/notifications\.js' %}": "{% static 'exchange/js/components/notifications.js' %}",
        r"{% static 'js/pdf_viewer\.js' %}": "{% static 'exchange/js/components/pdf_viewer.js' %}",
        r"{% static 'js/realtime-updates\.js' %}": "{% static 'exchange/js/components/realtime-updates.js' %}",
        r"{% static 'js/seim-components\.js' %}": "{% static 'exchange/js/components/seim-components.js' %}",
        r"{% static 'js/phase3-integration\.js' %}": "{% static 'exchange/js/pages/phase3-integration.js' %}",
        
        # Image files
        r"{% static 'images/favicon\.ico' %}": "{% static 'exchange/img/favicon.ico' %}",
        r"{% static 'images/favicon\.svg' %}": "{% static 'exchange/img/favicon.svg' %}",
    }
    
    # Also update template includes
    template_mappings = {
        r"{% include 'exchange/includes/": "{% include 'exchange/partials/",
        r"'exchange/exchange_form\.html'": "'exchange/forms/exchange_form.html'",
        r'"exchange/exchange_form\.html"': '"exchange/forms/exchange_form.html"',
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply static file path mappings
        for old_path, new_path in path_mappings.items():
            if re.search(old_path, content):
                content = re.sub(old_path, new_path, content)
                updates.append(f"  {old_path} -> {new_path}")
        
        # Apply template path mappings
        for old_path, new_path in template_mappings.items():
            if re.search(old_path, content):
                content = re.sub(old_path, new_path, content)
                updates.append(f"  {old_path} -> {new_path}")
        
        if content != original_content:
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            return updates
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    
    return []


def find_template_files(root_dir):
    """Find all HTML template files."""
    template_files = []
    for root, dirs, files in os.walk(root_dir):
        # Skip migrations and __pycache__
        if 'migrations' in root or '__pycache__' in root:
            continue
        
        for file in files:
            if file.endswith('.html'):
                template_files.append(os.path.join(root, file))
    
    return template_files


def main():
    """Main function to update all template files."""
    project_root = Path(__file__).parent.parent
    templates_dir = project_root / 'SEIM' / 'exchange' / 'templates'
    
    print("Finding template files...")
    template_files = find_template_files(templates_dir)
    
    print(f"Found {len(template_files)} template files")
    
    # First, do a dry run to show what will be changed
    print("\nDry run - showing what will be changed:")
    total_updates = 0
    files_to_update = []
    
    for template_file in template_files:
        updates = update_static_paths(template_file, dry_run=True)
        if updates:
            print(f"\n{template_file}:")
            for update in updates:
                print(update)
            files_to_update.append(template_file)
            total_updates += len(updates)
    
    if total_updates > 0:
        print(f"\nTotal updates to be made: {total_updates} in {len(files_to_update)} files")
        
        # Automatically apply changes
        print("\nApplying changes...")
        for template_file in files_to_update:
            update_static_paths(template_file, dry_run=False)
        print("Done! All template files have been updated.")
    else:
        print("\nNo updates needed - all paths are already correct!")


if __name__ == "__main__":
    main()
