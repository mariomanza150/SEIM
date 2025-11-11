#!/usr/bin/env python3
"""
Script to update Django templates with the correct webpack bundle hashes.
This script finds the latest webpack bundle files and updates the template references.
"""

import re
from pathlib import Path


def find_latest_bundle(bundle_name):
    """Find the latest webpack bundle file for a given name."""
    static_dist = Path("static/dist")
    if not static_dist.exists():
        return None

    # Find all files matching the bundle name pattern
    pattern = f"{bundle_name}.*.js"
    files = list(static_dist.glob(pattern))

    if not files:
        return None

    # Return the most recently modified file
    latest_file = max(files, key=lambda f: f.stat().st_mtime)
    return latest_file.name


def update_template_references():
    """Update template files with the latest webpack bundle hashes."""
    template_file = Path("templates/base.html")

    if not template_file.exists():
        print(f"Template file {template_file} not found!")
        return False

    # Read the template file
    with open(template_file, encoding="utf-8") as f:
        content = f.read()

    # Find the latest auth_entry bundle
    auth_bundle = find_latest_bundle("auth_entry")
    if not auth_bundle:
        print("No auth_entry bundle found in static/dist/")
        return False

    print(f"Found auth bundle: {auth_bundle}")

    # Update the template content
    # Replace the hardcoded auth_entry references
    old_pattern = r"auth_entry\.[a-f0-9]{20}\.js"
    new_content = re.sub(old_pattern, auth_bundle, content)

    # If no replacement was made, try a more specific pattern
    if new_content == content:
        # Look for the specific lines and replace them
        lines = content.split("\n")
        updated_lines = []

        for line in lines:
            if "auth_entry." in line and ".js" in line:
                # Replace the entire line with the new bundle name
                line = re.sub(r"auth_entry\.[a-f0-9]{20}\.js", auth_bundle, line)
            updated_lines.append(line)

        new_content = "\n".join(updated_lines)

    # Write the updated content back
    if new_content != content:
        with open(template_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {template_file} with {auth_bundle}")
        return True
    else:
        print("No changes needed in template")
        return False


if __name__ == "__main__":
    print("Updating template references with latest webpack bundles...")
    success = update_template_references()
    if success:
        print("Template updated successfully!")
    else:
        print("No updates were made.")
