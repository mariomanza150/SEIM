"""
Screenshot management utilities for E2E tests.

Provides functions for capturing, organizing, and managing screenshots.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from playwright.sync_api import Page


class ScreenshotManager:
    """Manager for organizing and capturing screenshots during tests."""
    
    def __init__(self, base_dir: str = 'tests/e2e_playwright/screenshots'):
        """
        Initialize screenshot manager.
        
        Args:
            base_dir: Base directory for storing screenshots
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def capture(
        self,
        page: Page,
        name: str,
        full_page: bool = True,
        element: Optional[str] = None
    ) -> Path:
        """
        Capture a screenshot.
        
        Args:
            page: Playwright page object
            name: Name for the screenshot
            full_page: Whether to capture full page
            element: Optional CSS selector to capture specific element
        
        Returns:
            Path to saved screenshot
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{name}_{timestamp}.png"
        filepath = self.base_dir / filename
        
        if element:
            locator = page.locator(element)
            locator.screenshot(path=str(filepath))
        else:
            page.screenshot(path=str(filepath), full_page=full_page)
        
        return filepath
    
    def capture_failure(
        self,
        page: Page,
        test_name: str,
        full_page: bool = True
    ) -> Path:
        """
        Capture screenshot for test failure.
        
        Args:
            page: Playwright page object
            test_name: Name of the failed test
            full_page: Whether to capture full page
        
        Returns:
            Path to saved screenshot
        """
        # Clean test name for filename
        clean_name = test_name.replace('::', '_').replace('/', '_').replace(' ', '_')
        filename = f"FAIL_{clean_name}.png"
        filepath = self.base_dir / filename
        
        page.screenshot(path=str(filepath), full_page=full_page)
        print(f"Failure screenshot saved: {filepath}")
        return filepath
    
    def capture_step(
        self,
        page: Page,
        test_name: str,
        step_name: str,
        full_page: bool = False
    ) -> Path:
        """
        Capture screenshot for a specific test step.
        
        Args:
            page: Playwright page object
            test_name: Name of the test
            step_name: Name of the step
            full_page: Whether to capture full page
        
        Returns:
            Path to saved screenshot
        """
        clean_test = test_name.replace('::', '_').replace('/', '_').replace(' ', '_')
        clean_step = step_name.replace(' ', '_')
        timestamp = datetime.now().strftime('%H%M%S')
        filename = f"{clean_test}_{clean_step}_{timestamp}.png"
        filepath = self.base_dir / filename
        
        page.screenshot(path=str(filepath), full_page=full_page)
        return filepath
    
    def cleanup_old_screenshots(self, days: int = 7) -> None:
        """
        Remove screenshots older than specified days.
        
        Args:
            days: Number of days to keep screenshots
        """
        import time
        cutoff_time = time.time() - (days * 86400)
        
        for screenshot in self.base_dir.glob('*.png'):
            if screenshot.stat().st_mtime < cutoff_time:
                screenshot.unlink()
                print(f"Deleted old screenshot: {screenshot.name}")
    
    def organize_by_test(self) -> None:
        """Organize screenshots into subdirectories by test name."""
        for screenshot in self.base_dir.glob('*.png'):
            # Extract test name from filename
            parts = screenshot.stem.split('_')
            if len(parts) >= 2:
                test_dir = self.base_dir / parts[0]
                test_dir.mkdir(exist_ok=True)
                screenshot.rename(test_dir / screenshot.name)


def capture_page_screenshot(
    page: Page,
    path: str,
    full_page: bool = True,
    clip: Optional[dict] = None
) -> None:
    """
    Capture a page screenshot with options.
    
    Args:
        page: Playwright page object
        path: Path to save screenshot
        full_page: Whether to capture full page
        clip: Optional clipping region {x, y, width, height}
    """
    options = {'path': path, 'full_page': full_page}
    if clip:
        options['clip'] = clip
    page.screenshot(**options)


def capture_element_screenshot(page: Page, selector: str, path: str) -> None:
    """
    Capture a screenshot of a specific element.
    
    Args:
        page: Playwright page object
        selector: CSS selector for the element
        path: Path to save screenshot
    """
    element = page.locator(selector)
    element.screenshot(path=path)


def capture_viewport_screenshot(page: Page, path: str) -> None:
    """
    Capture screenshot of visible viewport only.
    
    Args:
        page: Playwright page object
        path: Path to save screenshot
    """
    page.screenshot(path=path, full_page=False)


def create_screenshot_comparison_html(
    baseline_path: str,
    current_path: str,
    diff_path: str,
    output_path: str
) -> None:
    """
    Create an HTML page comparing three screenshots side by side.
    
    Args:
        baseline_path: Path to baseline screenshot
        current_path: Path to current screenshot
        diff_path: Path to diff screenshot
        output_path: Path to save HTML comparison
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Screenshot Comparison</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .comparison {{ display: flex; gap: 20px; }}
            .image-container {{ flex: 1; }}
            .image-container h3 {{ margin-top: 0; }}
            img {{ max-width: 100%; border: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <h1>Screenshot Comparison</h1>
        <div class="comparison">
            <div class="image-container">
                <h3>Baseline</h3>
                <img src="{baseline_path}" alt="Baseline">
            </div>
            <div class="image-container">
                <h3>Current</h3>
                <img src="{current_path}" alt="Current">
            </div>
            <div class="image-container">
                <h3>Difference</h3>
                <img src="{diff_path}" alt="Difference">
            </div>
        </div>
    </body>
    </html>
    """
    Path(output_path).write_text(html)

