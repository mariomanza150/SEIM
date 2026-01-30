"""
CMS StreamField Blocks

Reusable content blocks for Wagtail StreamFields.
These blocks provide flexible, structured content authoring.
"""

from django import forms
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock


class RichTextBlock(blocks.StructBlock):
    """Rich text block with formatting options."""
    
    content = blocks.RichTextBlock(
        features=[
            'h2', 'h3', 'h4', 'bold', 'italic', 'link', 'ol', 'ul',
            'document-link', 'image', 'embed', 'code', 'superscript', 'subscript',
            'strikethrough', 'blockquote'
        ],
        help_text="Rich text content with formatting options"
    )
    
    class Meta:
        template = 'cms/blocks/rich_text_block.html'
        icon = 'doc-full'
        label = 'Rich Text'


class ImageBlock(blocks.StructBlock):
    """Image block with caption and alignment options."""
    
    image = ImageChooserBlock(required=True)
    caption = blocks.CharBlock(required=False, max_length=250)
    attribution = blocks.CharBlock(required=False, max_length=250)
    alignment = blocks.ChoiceBlock(
        choices=[
            ('left', 'Left'),
            ('center', 'Center'),
            ('right', 'Right'),
            ('full', 'Full Width'),
        ],
        default='center',
    )
    
    class Meta:
        template = 'cms/blocks/image_block.html'
        icon = 'image'
        label = 'Image'


class CallToActionBlock(blocks.StructBlock):
    """Call-to-action block with button/link."""
    
    title = blocks.CharBlock(required=True, max_length=100)
    text = blocks.TextBlock(required=False, max_length=500)
    button_text = blocks.CharBlock(required=True, max_length=50)
    button_link = blocks.URLBlock(required=False)
    button_page = blocks.PageChooserBlock(required=False)
    style = blocks.ChoiceBlock(
        choices=[
            ('primary', 'Primary (Blue)'),
            ('success', 'Success (Green)'),
            ('info', 'Info (Cyan)'),
            ('warning', 'Warning (Yellow)'),
            ('danger', 'Danger (Red)'),
            ('light', 'Light'),
            ('dark', 'Dark'),
        ],
        default='primary',
    )
    
    class Meta:
        template = 'cms/blocks/call_to_action_block.html'
        icon = 'pick'
        label = 'Call to Action'


class CardBlock(blocks.StructBlock):
    """Individual card in a card grid."""
    
    icon = blocks.CharBlock(
        required=False,
        max_length=50,
        help_text="Bootstrap icon class (e.g., 'bi-globe')"
    )
    title = blocks.CharBlock(required=True, max_length=100)
    text = blocks.TextBlock(required=True, max_length=500)
    link = blocks.URLBlock(required=False)
    link_text = blocks.CharBlock(required=False, max_length=50)


class CardGridBlock(blocks.StructBlock):
    """Grid of feature cards."""
    
    heading = blocks.CharBlock(required=False, max_length=100)
    subheading = blocks.TextBlock(required=False, max_length=250)
    cards = blocks.ListBlock(CardBlock())
    columns = blocks.ChoiceBlock(
        choices=[
            ('2', '2 Columns'),
            ('3', '3 Columns'),
            ('4', '4 Columns'),
        ],
        default='3',
    )
    
    class Meta:
        template = 'cms/blocks/card_grid_block.html'
        icon = 'grip'
        label = 'Card Grid'


class TestimonialBlock(blocks.StructBlock):
    """Testimonial or quote block."""
    
    quote = blocks.TextBlock(required=True, max_length=500)
    author = blocks.CharBlock(required=True, max_length=100)
    author_title = blocks.CharBlock(required=False, max_length=100)
    author_image = ImageChooserBlock(required=False)
    
    class Meta:
        template = 'cms/blocks/testimonial_block.html'
        icon = 'openquote'
        label = 'Testimonial'


class FAQItemBlock(blocks.StructBlock):
    """Individual FAQ item."""
    
    question = blocks.CharBlock(required=True, max_length=250)
    answer = blocks.RichTextBlock(
        required=True,
        features=['bold', 'italic', 'link', 'ol', 'ul']
    )


class FAQBlock(blocks.StructBlock):
    """FAQ section with multiple Q&A items."""
    
    heading = blocks.CharBlock(required=False, max_length=100, default="Frequently Asked Questions")
    items = blocks.ListBlock(FAQItemBlock())
    
    class Meta:
        template = 'cms/blocks/faq_block.html'
        icon = 'help'
        label = 'FAQ Section'


class HeroBlock(blocks.StructBlock):
    """Hero banner block for prominent sections."""
    
    title = blocks.CharBlock(required=True, max_length=100)
    subtitle = blocks.TextBlock(required=False, max_length=250)
    background_image = ImageChooserBlock(required=False)
    background_color = blocks.ChoiceBlock(
        choices=[
            ('primary', 'Primary (Blue)'),
            ('secondary', 'Secondary (Gray)'),
            ('success', 'Success (Green)'),
            ('info', 'Info (Cyan)'),
            ('dark', 'Dark'),
        ],
        default='primary',
    )
    button_text = blocks.CharBlock(required=False, max_length=50)
    button_link = blocks.URLBlock(required=False)
    button_page = blocks.PageChooserBlock(required=False)
    
    class Meta:
        template = 'cms/blocks/hero_block.html'
        icon = 'image'
        label = 'Hero Banner'


class EmbedVideoBlock(blocks.StructBlock):
    """Embedded video block."""
    
    video = EmbedBlock(
        required=True,
        help_text="YouTube, Vimeo, or other supported video URL"
    )
    caption = blocks.CharBlock(required=False, max_length=250)
    
    class Meta:
        template = 'cms/blocks/embed_video_block.html'
        icon = 'media'
        label = 'Embedded Video'


class DocumentDownloadBlock(blocks.StructBlock):
    """Document download block."""
    
    document = DocumentChooserBlock(required=True)
    title = blocks.CharBlock(required=False, max_length=100)
    description = blocks.TextBlock(required=False, max_length=250)
    
    class Meta:
        template = 'cms/blocks/document_download_block.html'
        icon = 'doc-full-inverse'
        label = 'Document Download'


class StepBlock(blocks.StructBlock):
    """Individual step in a process."""
    
    number = blocks.CharBlock(required=True, max_length=10)
    title = blocks.CharBlock(required=True, max_length=100)
    description = blocks.TextBlock(required=True, max_length=250)
    icon = blocks.CharBlock(
        required=False,
        max_length=50,
        help_text="Bootstrap icon class (e.g., 'bi-check-circle')"
    )


class ProcessStepsBlock(blocks.StructBlock):
    """Step-by-step process display."""
    
    heading = blocks.CharBlock(required=False, max_length=100)
    subheading = blocks.TextBlock(required=False, max_length=250)
    steps = blocks.ListBlock(StepBlock())
    
    class Meta:
        template = 'cms/blocks/process_steps_block.html'
        icon = 'list-ol'
        label = 'Process Steps'


class ColumnBlock(blocks.StructBlock):
    """Individual column content."""
    
    content = blocks.StreamBlock([
        ('rich_text', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('document', DocumentChooserBlock()),
    ], use_json_field=True)


class TwoColumnBlock(blocks.StructBlock):
    """Two-column layout block."""
    
    left_column = ColumnBlock()
    right_column = ColumnBlock()
    
    class Meta:
        template = 'cms/blocks/two_column_block.html'
        icon = 'horizontalrule'
        label = 'Two Columns'


class FormBlock(blocks.StructBlock):
    """Embedded form block (links to FormPage)."""
    
    form_page = blocks.PageChooserBlock(
        required=True,
        page_type='cms.FormPage',
        help_text="Select a form page to embed"
    )
    show_title = blocks.BooleanBlock(required=False, default=True)
    
    class Meta:
        template = 'cms/blocks/form_block.html'
        icon = 'form'
        label = 'Embedded Form'


# Main StreamField definition used across multiple page types
class BaseStreamBlock(blocks.StreamBlock):
    """Base StreamBlock with all available blocks."""
    
    rich_text = RichTextBlock()
    image = ImageBlock()
    call_to_action = CallToActionBlock()
    card_grid = CardGridBlock()
    testimonial = TestimonialBlock()
    faq = FAQBlock()
    hero = HeroBlock()
    video = EmbedVideoBlock()
    document = DocumentDownloadBlock()
    process_steps = ProcessStepsBlock()
    two_columns = TwoColumnBlock()
    embedded_form = FormBlock()
    
    class Meta:
        use_json_field = True
