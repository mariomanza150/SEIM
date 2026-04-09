"""
Fix for Wagtail 6.3 rich text AssertionError: Unmatched tags: expected br, got p

This is a known bug in Wagtail's html_to_contentstate converter when <br> tags
are present inside <p> tags. Applies a monkey patch to fix the tag matching logic.

Issue reference: https://github.com/wagtail/wagtail/issues/11742
"""
import logging
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    HtmlToContentStateHandler,
)

logger = logging.getLogger(__name__)


def apply_richtext_fix():
    """Apply monkey patch to fix Wagtail rich text tag matching error"""
    original_handle_endtag = HtmlToContentStateHandler.handle_endtag

    def patched_handle_endtag(self, tag):
        try:
            return original_handle_endtag(self, tag)
        except AssertionError as e:
            if "Unmatched tags: expected br, got p" in str(e):
                logger.warning("Recovering from rich text br/p tag mismatch error")
                # Fix for Wagtail 6.3 internal structure
                while hasattr(self, 'block_stack') and len(self.block_stack) > 0 and self.block_stack[-1]['type'] == 'br':
                    self.block_stack.pop()
                # Now try closing the p tag again
                return original_handle_endtag(self, tag)
            raise

    HtmlToContentStateHandler.handle_endtag = patched_handle_endtag
    logger.info("Wagtail rich text fix applied successfully")