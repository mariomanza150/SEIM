#!/usr/bin/env python3
"""
SEIM CSS Optimization Script
Extracts critical CSS and optimizes CSS delivery for better performance
"""

import gzip
import hashlib
import json
import re
import sys
from pathlib import Path


class CSSOptimizer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.static_dir = self.project_root / "static"
        self.css_dir = self.static_dir / "css"
        self.templates_dir = self.project_root / "templates"
        self.output_dir = self.project_root / "staticfiles"

        # Critical CSS selectors (above-the-fold content)
        self.critical_selectors = {
            "body",
            "html",
            "head",
            "title",
            ".navbar",
            ".navbar-brand",
            ".navbar-nav",
            ".nav-link",
            ".container",
            ".row",
            ".col",
            ".btn",
            ".btn-primary",
            ".btn-secondary",
            ".form-control",
            ".form-group",
            ".form-label",
            ".alert",
            ".alert-success",
            ".alert-danger",
            ".alert-warning",
            ".spinner-border",
            ".loading",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "p",
            ".d-none",
            ".d-block",
            ".d-flex",
            ".text-center",
            ".mt-3",
            ".mb-3",
            ".p-3",
        }

        # Non-critical CSS files
        self.non_critical_files = [
            "components/cards.css",
            "components/tables.css",
            "utilities/colors.css",
            "utilities/spacing.css",
            "utilities/typography.css",
        ]

    def extract_critical_css(self) -> str:
        """Extract critical CSS from main.css"""
        main_css_path = self.css_dir / "main.css"
        if not main_css_path.exists():
            print(f"Warning: {main_css_path} not found")
            return ""

        critical_css = []
        in_critical_block = False

        with open(main_css_path, encoding="utf-8") as f:
            content = f.read()

        # Extract critical CSS from critical.css
        critical_css_path = self.css_dir / "critical.css"
        if critical_css_path.exists():
            with open(critical_css_path, encoding="utf-8") as f:
                critical_css.append(f.read())

        # Parse main.css and extract critical selectors
        lines = content.split("\n")
        for line in lines:
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith("/*") or line.startswith("//"):
                continue

            # Check if this is a selector
            if not line.startswith(" ") and not line.startswith("\t") and ":" in line:
                # Extract selector
                selector_match = re.match(r"^([^{]+)", line)
                if selector_match:
                    selector = selector_match.group(1).strip()
                    # Check if this selector is critical
                    is_critical = any(
                        crit in selector for crit in self.critical_selectors
                    )

                    if is_critical:
                        in_critical_block = True
                        critical_css.append(line)
                    else:
                        in_critical_block = False
                else:
                    if in_critical_block:
                        critical_css.append(line)
            elif in_critical_block:
                critical_css.append(line)

        return "\n".join(critical_css)

    def create_non_critical_css(self) -> str:
        """Create non-critical CSS bundle"""
        non_critical_css = []

        for css_file in self.non_critical_files:
            file_path = self.css_dir / css_file
            if file_path.exists():
                with open(file_path, encoding="utf-8") as f:
                    non_critical_css.append(f"/* {css_file} */")
                    non_critical_css.append(f.read())

        return "\n".join(non_critical_css)

    def minify_css(self, css_content: str) -> str:
        """Minify CSS content"""
        # Remove comments
        css_content = re.sub(r"/\*.*?\*/", "", css_content, flags=re.DOTALL)

        # Remove unnecessary whitespace
        css_content = re.sub(r"\s+", " ", css_content)
        css_content = re.sub(r";\s*}", "}", css_content)
        css_content = re.sub(r"{\s*", "{", css_content)
        css_content = re.sub(r"}\s*", "}", css_content)

        # Remove trailing semicolons
        css_content = re.sub(r";}", "}", css_content)

        return css_content.strip()

    def compress_css(self, css_content: str) -> bytes:
        """Compress CSS using gzip"""
        return gzip.compress(css_content.encode("utf-8"))

    def generate_css_hash(self, css_content: str) -> str:
        """Generate hash for CSS content"""
        return hashlib.md5(css_content.encode("utf-8")).hexdigest()[:8]

    def update_template_css_loading(self, critical_css: str, non_critical_css: str):
        """Update base template to inline critical CSS and defer non-critical CSS"""
        base_template = self.templates_dir / "base.html"
        if not base_template.exists():
            print(f"Warning: {base_template} not found")
            return

        # Generate hashes
        critical_hash = self.generate_css_hash(critical_css)
        non_critical_hash = self.generate_css_hash(non_critical_css)

        # Create optimized CSS files
        critical_filename = f"critical.{critical_hash}.css"
        non_critical_filename = f"non-critical.{non_critical_hash}.css"

        # Write CSS files
        self.output_dir.mkdir(exist_ok=True)
        css_output_dir = self.output_dir / "css"
        css_output_dir.mkdir(exist_ok=True)

        with open(css_output_dir / critical_filename, "w", encoding="utf-8") as f:
            f.write(critical_css)

        with open(css_output_dir / non_critical_filename, "w", encoding="utf-8") as f:
            f.write(non_critical_css)

        # Create compressed versions
        with open(css_output_dir / f"{critical_filename}.gz", "wb") as f:
            f.write(self.compress_css(critical_css))

        with open(css_output_dir / f"{non_critical_filename}.gz", "wb") as f:
            f.write(self.compress_css(non_critical_css))

        # Update base template
        with open(base_template, encoding="utf-8") as f:
            template_content = f.read()

        # Replace CSS loading
        critical_css_inline = f"<style>{critical_css}</style>"
        non_critical_css_link = f'<link rel="preload" href="/static/css/{non_critical_filename}" as="style" onload="this.onload=null;this.rel=\'stylesheet\'">'
        non_critical_css_fallback = f'<noscript><link rel="stylesheet" href="/static/css/{non_critical_filename}"></noscript>'

        # Find and replace CSS loading section
        css_pattern = r"<!--\s*CSS\s*Loading\s*-->(.*?)<!--\s*End\s*CSS\s*Loading\s*-->"
        css_replacement = f"""<!-- CSS Loading -->
        {critical_css_inline}
        {non_critical_css_link}
        {non_critical_css_fallback}
        <!-- End CSS Loading -->"""

        if re.search(css_pattern, template_content, re.DOTALL):
            template_content = re.sub(
                css_pattern, css_replacement, template_content, flags=re.DOTALL
            )
        else:
            # Add CSS loading section if not found
            head_pattern = r"(<head[^>]*>)"
            head_replacement = f"\\1\n        {critical_css_inline}\n        {non_critical_css_link}\n        {non_critical_css_fallback}"
            template_content = re.sub(head_pattern, head_replacement, template_content)

        # Write updated template
        with open(base_template, "w", encoding="utf-8") as f:
            f.write(template_content)

        print(f"Updated {base_template} with optimized CSS loading")
        print(f"Critical CSS: {critical_filename} ({len(critical_css)} bytes)")
        print(
            f"Non-critical CSS: {non_critical_filename} ({len(non_critical_css)} bytes)"
        )

    def generate_css_report(self, critical_css: str, non_critical_css: str):
        """Generate CSS optimization report"""
        report = {
            "timestamp": str(Path().cwd()),
            "critical_css": {
                "size_bytes": len(critical_css),
                "size_kb": len(critical_css) / 1024,
                "compressed_bytes": len(self.compress_css(critical_css)),
                "compressed_kb": len(self.compress_css(critical_css)) / 1024,
                "selectors_count": len(re.findall(r"[^{}]+{", critical_css)),
                "rules_count": len(re.findall(r"{[^}]+}", critical_css)),
            },
            "non_critical_css": {
                "size_bytes": len(non_critical_css),
                "size_kb": len(non_critical_css) / 1024,
                "compressed_bytes": len(self.compress_css(non_critical_css)),
                "compressed_kb": len(self.compress_css(non_critical_css)) / 1024,
                "selectors_count": len(re.findall(r"[^{}]+{", non_critical_css)),
                "rules_count": len(re.findall(r"{[^}]+}", non_critical_css)),
            },
            "optimization_targets": {
                "critical_css_target_kb": 14,
                "total_css_target_kb": 50,
                "critical_css_achieved": len(critical_css) / 1024 <= 14,
                "total_css_achieved": (len(critical_css) + len(non_critical_css)) / 1024
                <= 50,
            },
        }

        # Write report
        report_path = (
            self.project_root / "documentation" / "css_optimization_report.json"
        )
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print("\nCSS Optimization Report:")
        print(f"Critical CSS: {report['critical_css']['size_kb']:.2f}KB (target: 14KB)")
        print(f"Non-critical CSS: {report['non_critical_css']['size_kb']:.2f}KB")
        print(
            f"Total CSS: {(report['critical_css']['size_kb'] + report['non_critical_css']['size_kb']):.2f}KB (target: 50KB)"
        )
        print(
            f"Compression ratio: {((1 - report['critical_css']['compressed_kb'] / report['critical_css']['size_kb']) * 100):.1f}%"
        )

        if report["optimization_targets"]["critical_css_achieved"]:
            print("✅ Critical CSS target achieved")
        else:
            print("❌ Critical CSS target not achieved")

        if report["optimization_targets"]["total_css_achieved"]:
            print("✅ Total CSS target achieved")
        else:
            print("❌ Total CSS target not achieved")

    def optimize(self):
        """Run complete CSS optimization"""
        print("Starting CSS optimization...")

        # Extract critical CSS
        print("Extracting critical CSS...")
        critical_css = self.extract_critical_css()
        critical_css = self.minify_css(critical_css)

        # Create non-critical CSS
        print("Creating non-critical CSS bundle...")
        non_critical_css = self.create_non_critical_css()
        non_critical_css = self.minify_css(non_critical_css)

        # Update template
        print("Updating template with optimized CSS loading...")
        self.update_template_css_loading(critical_css, non_critical_css)

        # Generate report
        print("Generating optimization report...")
        self.generate_css_report(critical_css, non_critical_css)

        print("CSS optimization completed!")


def main():
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = "."

    optimizer = CSSOptimizer(project_root)
    optimizer.optimize()


if __name__ == "__main__":
    main()
