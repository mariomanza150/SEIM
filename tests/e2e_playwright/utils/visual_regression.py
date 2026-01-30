"""
Visual regression testing utilities for E2E tests.

Provides functions for screenshot comparison and baseline management.
"""

import io
from pathlib import Path
from typing import Optional

from PIL import Image
import pixelmatch


def compare_screenshot(
    current: bytes,
    baseline: bytes,
    name: str,
    threshold: float = 0.1,
    diff_dir: str = 'tests/e2e_playwright/visual/diffs'
) -> bool:
    """
    Compare current screenshot with baseline.
    
    Args:
        current: Current screenshot bytes
        baseline: Baseline screenshot bytes
        name: Name for the comparison
        threshold: Acceptable difference threshold (0.0 to 1.0)
        diff_dir: Directory to save diff images
    
    Returns:
        True if screenshots match within threshold, False otherwise
    """
    # Load images
    current_img = Image.open(io.BytesIO(current))
    baseline_img = Image.open(io.BytesIO(baseline))
    
    # Ensure images are the same size
    if current_img.size != baseline_img.size:
        print(f"Warning: Image sizes don't match for {name}")
        print(f"Current: {current_img.size}, Baseline: {baseline_img.size}")
        return False
    
    # Convert to RGBA for comparison
    current_img = current_img.convert('RGBA')
    baseline_img = baseline_img.convert('RGBA')
    
    # Create diff image
    width, height = current_img.size
    diff_img = Image.new('RGBA', (width, height))
    
    # Get pixel data
    current_pixels = list(current_img.getdata())
    baseline_pixels = list(baseline_img.getdata())
    
    # Count different pixels
    diff_count = 0
    diff_pixels = []
    
    for i in range(len(current_pixels)):
        if current_pixels[i] != baseline_pixels[i]:
            diff_count += 1
            diff_pixels.append((255, 0, 0, 255))  # Red for differences
        else:
            diff_pixels.append(current_pixels[i])
    
    # Calculate difference percentage
    total_pixels = width * height
    diff_percentage = diff_count / total_pixels
    
    # Save diff image if there are differences
    if diff_percentage > threshold:
        diff_img.putdata(diff_pixels)
        diff_path = Path(diff_dir)
        diff_path.mkdir(parents=True, exist_ok=True)
        diff_img.save(diff_path / f"{name}_diff.png")
        print(f"Visual difference detected: {diff_percentage:.2%} (threshold: {threshold:.2%})")
        print(f"Diff image saved to: {diff_path / f'{name}_diff.png'}")
        return False
    
    return True


def hide_dynamic_elements(page, selectors: list[str]) -> None:
    """
    Hide dynamic elements before taking screenshot.
    
    Args:
        page: Playwright page object
        selectors: List of CSS selectors to hide
    """
    for selector in selectors:
        page.evaluate(f"""
            document.querySelectorAll('{selector}').forEach(el => {{
                el.style.visibility = 'hidden';
            }});
        """)


def mask_elements(page, selectors: list[str]) -> None:
    """
    Mask elements with a solid color before taking screenshot.
    
    Args:
        page: Playwright page object
        selectors: List of CSS selectors to mask
    """
    for selector in selectors:
        page.evaluate(f"""
            document.querySelectorAll('{selector}').forEach(el => {{
                el.style.backgroundColor = '#cccccc';
                el.style.color = '#cccccc';
            }});
        """)


def update_baseline(name: str, screenshot: bytes, baseline_dir: str = 'tests/e2e_playwright/visual/snapshots') -> None:
    """
    Update baseline screenshot.
    
    Args:
        name: Name of the baseline
        screenshot: Screenshot bytes
        baseline_dir: Directory to save baselines
    """
    baseline_path = Path(baseline_dir)
    baseline_path.mkdir(parents=True, exist_ok=True)
    (baseline_path / f"{name}.png").write_bytes(screenshot)
    print(f"Baseline updated: {name}")


def delete_baseline(name: str, baseline_dir: str = 'tests/e2e_playwright/visual/snapshots') -> None:
    """
    Delete baseline screenshot.
    
    Args:
        name: Name of the baseline
        baseline_dir: Directory containing baselines
    """
    baseline_path = Path(baseline_dir) / f"{name}.png"
    if baseline_path.exists():
        baseline_path.unlink()
        print(f"Baseline deleted: {name}")


def generate_visual_report(results: dict, output_dir: str = 'tests/e2e_playwright/visual/reports') -> None:
    """
    Generate HTML report for visual regression tests.
    
    Args:
        results: Dictionary of test results
        output_dir: Directory to save the report
    """
    report_dir = Path(output_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Visual Regression Test Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            .test { border: 1px solid #ddd; padding: 15px; margin: 10px 0; }
            .pass { background-color: #d4edda; }
            .fail { background-color: #f8d7da; }
            img { max-width: 300px; margin: 10px; border: 1px solid #ddd; }
        </style>
    </head>
    <body>
        <h1>Visual Regression Test Report</h1>
    """
    
    for test_name, result in results.items():
        status = 'pass' if result['passed'] else 'fail'
        html += f"""
        <div class="test {status}">
            <h2>{test_name}</h2>
            <p>Status: {'PASS' if result['passed'] else 'FAIL'}</p>
            <p>Difference: {result.get('difference', 0):.2%}</p>
        """
        if not result['passed']:
            html += f"""
            <div>
                <img src="{result.get('baseline_path', '')}" alt="Baseline">
                <img src="{result.get('current_path', '')}" alt="Current">
                <img src="{result.get('diff_path', '')}" alt="Diff">
            </div>
            """
        html += "</div>"
    
    html += """
    </body>
    </html>
    """
    
    report_path = report_dir / 'visual_report.html'
    report_path.write_text(html)
    print(f"Visual report generated: {report_path}")

