"""
Fix for Wagtail rich text AssertionError: Unmatched tags: expected br, got p

Wagtail's HtmlToContentStateHandler pushes void HTML elements (e.g. <br>, <hr>)
onto `open_elements` in handle_starttag, but the parser never emits matching
end tags for them. The next closing tag (e.g. </p>) then fails the stack check.

Upstream: https://github.com/wagtail/wagtail/issues/11742
"""
import logging

from wagtail.admin.rich_text.converters.html_to_contentstate import (
    HtmlToContentStateHandler,
)

logger = logging.getLogger(__name__)

# HTML void elements — no closing tag in normal parsing, so they must not stay on the stack.
_VOID_HTML_TAGS = frozenset(
    {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
)


def apply_richtext_fix():
    """Monkey-patch HtmlToContentStateHandler to pop void tags before closing parents."""
    original_handle_endtag = HtmlToContentStateHandler.handle_endtag

    def patched_handle_endtag(self, tag):
        while (
            self.open_elements
            and self.open_elements[-1][0] in _VOID_HTML_TAGS
            and self.open_elements[-1][0] != tag
        ):
            self.open_elements.pop()
        return original_handle_endtag(self, tag)

    HtmlToContentStateHandler.handle_endtag = patched_handle_endtag
    logger.info("Wagtail rich text void-tag stack fix applied")
