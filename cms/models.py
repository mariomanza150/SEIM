"""
CMS Models

Wagtail page models for content management, including:
- HomePage: Main landing page
- StandardPage: Flexible info pages
- BlogIndexPage & BlogPostPage: Blog system
- ProgramPage & ProgramIndexPage: Program listing
- FormPage: Dynamic form builder
- FAQPage & FAQIndexPage: FAQ system
"""

from django.db import models
from django.shortcuts import render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager

from taggit.models import TaggedItemBase

from wagtail.models import Page, Orderable
from wagtail.fields import StreamField, RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.search import index
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from wagtail.snippets.models import register_snippet

from wagtailseo.models import SeoMixin, SeoType, TwitterCard

from .blocks import BaseStreamBlock


# ============================================================================
# INTERNATIONAL SECTION - CGRI & MOVILIDAD
# ============================================================================

class InternationalHomePage(SeoMixin, Page):
    """
    Landing page for International Relations section.
    Replaces /cgri/ and /movilidad/ with unified /internacional/
    """
    
    # Hero Section
    hero_title = models.CharField(
        max_length=200,
        default="Relaciones Internacionales",
        help_text="Main hero title"
    )
    hero_subtitle = models.TextField(
        max_length=500,
        default="Tu puerta al mundo académico",
        help_text="Hero subtitle"
    )
    hero_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Hero background image"
    )
    
    # Introduction
    introduction = RichTextField(
        blank=True,
        help_text="Page introduction"
    )
    
    # Content sections
    body = StreamField(
        BaseStreamBlock(),
        null=True,
        blank=True,
        use_json_field=True,
        help_text="Main content area"
    )
    
    # Quick Stats
    show_stats = models.BooleanField(
        default=True,
        help_text="Show statistics section"
    )
    stat_programs_count = models.IntegerField(
        default=0,
        help_text="Number of active programs"
    )
    stat_countries_count = models.IntegerField(
        default=0,
        help_text="Number of partner countries"
    )
    stat_students_count = models.IntegerField(
        default=0,
        help_text="Number of students in exchange"
    )
    stat_institutions_count = models.IntegerField(
        default=0,
        help_text="Number of partner institutions"
    )
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('hero_title'),
            FieldPanel('hero_subtitle'),
            FieldPanel('hero_image'),
        ], heading="Hero Section"),
        FieldPanel('introduction'),
        FieldPanel('body'),
        MultiFieldPanel([
            FieldPanel('show_stats'),
            FieldPanel('stat_programs_count'),
            FieldPanel('stat_countries_count'),
            FieldPanel('stat_students_count'),
            FieldPanel('stat_institutions_count'),
        ], heading="Statistics"),
    ]
    
    promote_panels = SeoMixin.seo_panels
    
    # Limit to one instance per site
    max_count_per_parent = 1
    
    class Meta:
        verbose_name = "International Home Page"
        verbose_name_plural = "International Home Pages"


class CGRIPage(SeoMixin, Page):
    """
    CGRI (Coordinación General de Relaciones Internacionales) institutional pages.
    For administrative and institutional content.
    """
    
    subtitle = models.CharField(
        max_length=200,
        blank=True,
        help_text="Page subtitle/tagline"
    )
    
    introduction = models.TextField(
        max_length=500,
        blank=True,
        help_text="Page introduction"
    )
    
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Featured image for the page"
    )
    
    body = StreamField(
        BaseStreamBlock(),
        use_json_field=True,
        help_text="Main content area"
    )
    
    # Contact Information
    show_contact = models.BooleanField(
        default=False,
        help_text="Show contact information sidebar"
    )
    contact_name = models.CharField(max_length=200, blank=True)
    contact_title = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    contact_office = models.CharField(max_length=200, blank=True)
    
    search_fields = Page.search_fields + [
        index.SearchField('introduction'),
        index.SearchField('body'),
    ]
    
    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('introduction'),
        FieldPanel('featured_image'),
        FieldPanel('body'),
        MultiFieldPanel([
            FieldPanel('show_contact'),
            FieldPanel('contact_name'),
            FieldPanel('contact_title'),
            FieldPanel('contact_email'),
            FieldPanel('contact_phone'),
            FieldPanel('contact_office'),
        ], heading="Contact Information"),
    ]
    
    promote_panels = SeoMixin.seo_panels
    
    parent_page_types = ['cms.InternationalHomePage', 'cms.CGRIPage']
    
    class Meta:
        verbose_name = "CGRI Page"
        verbose_name_plural = "CGRI Pages"


class MovilidadLandingPage(SeoMixin, Page):
    """
    Main landing page for student mobility (Movilidad Estudiantil).
    Student-facing information hub.
    """
    
    hero_title = models.CharField(
        max_length=200,
        default="Movilidad Estudiantil",
        help_text="Hero title"
    )
    hero_subtitle = models.TextField(
        max_length=500,
        default="Vive una experiencia académica internacional",
        help_text="Hero subtitle"
    )
    hero_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Hero background image"
    )
    
    introduction = RichTextField(
        blank=True,
        help_text="Introduction text"
    )
    
    body = StreamField(
        BaseStreamBlock(),
        null=True,
        blank=True,
        use_json_field=True,
        help_text="Main content blocks"
    )
    
    # Quick Links
    show_quick_links = models.BooleanField(
        default=True,
        help_text="Show quick access links"
    )
    
    # CTA to SEIM
    show_application_cta = models.BooleanField(
        default=True,
        help_text="Show application CTA linking to SEIM"
    )
    application_cta_text = models.CharField(
        max_length=100,
        default="Aplicar Ahora",
        blank=True
    )
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('hero_title'),
            FieldPanel('hero_subtitle'),
            FieldPanel('hero_image'),
        ], heading="Hero Section"),
        FieldPanel('introduction'),
        FieldPanel('body'),
        MultiFieldPanel([
            FieldPanel('show_quick_links'),
            FieldPanel('show_application_cta'),
            FieldPanel('application_cta_text'),
        ], heading="CTAs and Links"),
    ]
    
    promote_panels = SeoMixin.seo_panels
    
    max_count_per_parent = 1
    
    class Meta:
        verbose_name = "Movilidad Landing Page"
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        
        # Get active programs from Exchange app
        from exchange.models import Program
        context['active_programs'] = Program.objects.filter(
            is_active=True
        ).select_related('destination_university', 'destination_country')[:6]
        
        # Get recent blog posts about mobility
        context['recent_posts'] = BlogPostPage.objects.live().public().filter(
            categories__slug='movilidad'
        )[:3]
        
        return context


class ConvenioPage(SeoMixin, Page):
    """
    International Agreement/Convenio page.
    Details about specific institutional partnerships.
    """
    
    institution_name = models.CharField(
        max_length=200,
        help_text="Partner institution name"
    )
    institution_logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Institution logo"
    )
    
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    
    agreement_type = models.CharField(
        max_length=50,
        choices=[
            ('bilateral', 'Bilateral'),
            ('multilateral', 'Multilateral'),
            ('erasmus', 'Erasmus+'),
            ('specific', 'Specific Program'),
        ],
        default='bilateral'
    )
    
    start_date = models.DateField(
        null=True,
        blank=True,
        help_text="Agreement start date"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Agreement end date (leave blank if ongoing)"
    )
    
    introduction = models.TextField(
        max_length=500,
        blank=True,
        help_text="Brief description"
    )
    
    body = StreamField(
        BaseStreamBlock(),
        use_json_field=True,
        help_text="Agreement details, benefits, requirements"
    )
    
    # Available programs
    available_for_students = models.BooleanField(default=True)
    available_for_faculty = models.BooleanField(default=False)
    available_for_research = models.BooleanField(default=False)
    
    # Website
    institution_website = models.URLField(blank=True)
    
    # Related programs in Exchange app
    related_programs = ParentalManyToManyField(
        'exchange.Program',
        blank=True,
        related_name='convenio_pages'
    )
    
    search_fields = Page.search_fields + [
        index.SearchField('institution_name'),
        index.SearchField('country'),
        index.SearchField('introduction'),
        index.SearchField('body'),
    ]
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('institution_name'),
            FieldPanel('institution_logo'),
            FieldPanel('country'),
            FieldPanel('city'),
            FieldPanel('institution_website'),
        ], heading="Institution Information"),
        MultiFieldPanel([
            FieldPanel('agreement_type'),
            FieldPanel('start_date'),
            FieldPanel('end_date'),
        ], heading="Agreement Details"),
        FieldPanel('introduction'),
        FieldPanel('body'),
        MultiFieldPanel([
            FieldPanel('available_for_students'),
            FieldPanel('available_for_faculty'),
            FieldPanel('available_for_research'),
        ], heading="Availability"),
        FieldPanel('related_programs'),
    ]
    
    promote_panels = SeoMixin.seo_panels
    
    parent_page_types = ['cms.ConvenioIndexPage']
    
    class Meta:
        verbose_name = "Convenio (Agreement)"
        verbose_name_plural = "Convenios (Agreements)"


class ConvenioIndexPage(SeoMixin, Page):
    """
    Index page for international agreements/convenios.
    """
    
    introduction = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
    ]
    
    promote_panels = SeoMixin.seo_panels
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        
        # Get all convenios
        convenios = ConvenioPage.objects.live().public().order_by('institution_name')
        
        # Filter by country
        country = request.GET.get('country')
        if country:
            convenios = convenios.filter(country=country)
        
        # Filter by type
        agreement_type = request.GET.get('type')
        if agreement_type:
            convenios = convenios.filter(agreement_type=agreement_type)
        
        # Get unique countries for filter
        countries = ConvenioPage.objects.live().public().values_list(
            'country', flat=True
        ).distinct().order_by('country')
        
        context['convenios'] = convenios
        context['countries'] = countries
        
        return context
    
    class Meta:
        verbose_name = "Convenio Index Page"


class TestimonialPage(SeoMixin, Page):
    """
    Student testimonial page for sharing exchange experiences.
    """
    
    student_name = models.CharField(max_length=200)
    student_photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Student photo"
    )
    
    student_major = models.CharField(
        max_length=200,
        blank=True,
        help_text="Student's major/field of study"
    )
    exchange_period = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., Fall 2024, Spring 2025"
    )
    
    destination_country = models.CharField(max_length=100)
    destination_institution = models.CharField(max_length=200)
    
    # Testimonial content
    quote = models.TextField(
        max_length=500,
        help_text="Short quote/excerpt for listings"
    )
    
    body = StreamField(
        BaseStreamBlock(),
        use_json_field=True,
        help_text="Full testimonial story"
    )
    
    # Related program
    program = models.ForeignKey(
        'exchange.Program',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='testimonials'
    )
    
    # Rating/Recommendation
    would_recommend = models.BooleanField(
        default=True,
        help_text="Would recommend this program"
    )
    
    search_fields = Page.search_fields + [
        index.SearchField('student_name'),
        index.SearchField('destination_country'),
        index.SearchField('quote'),
        index.SearchField('body'),
    ]
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('student_name'),
            FieldPanel('student_photo'),
            FieldPanel('student_major'),
            FieldPanel('exchange_period'),
        ], heading="Student Information"),
        MultiFieldPanel([
            FieldPanel('destination_country'),
            FieldPanel('destination_institution'),
            FieldPanel('program'),
        ], heading="Exchange Information"),
        FieldPanel('quote'),
        FieldPanel('body'),
        FieldPanel('would_recommend'),
    ]
    
    promote_panels = SeoMixin.seo_panels
    
    parent_page_types = ['cms.TestimonialIndexPage']
    
    class Meta:
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"


class TestimonialIndexPage(SeoMixin, Page):
    """
    Index page for student testimonials.
    """
    
    introduction = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
    ]
    
    promote_panels = SeoMixin.seo_panels
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        
        # Get all testimonials
        testimonials = TestimonialPage.objects.live().public().order_by('-first_published_at')
        
        # Filter by country
        country = request.GET.get('country')
        if country:
            testimonials = testimonials.filter(destination_country=country)
        
        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(testimonials, 9)
        
        try:
            testimonial_pages = paginator.page(page)
        except PageNotAnInteger:
            testimonial_pages = paginator.page(1)
        except EmptyPage:
            testimonial_pages = paginator.page(paginator.num_pages)
        
        context['testimonials'] = testimonial_pages
        
        return context
    
    class Meta:
        verbose_name = "Testimonial Index Page"


# ============================================================================
# HOME PAGE
# ============================================================================

class HomePage(SeoMixin, Page):
    """
    Main landing page for the SEIM application.
    Features hero section, features, and call-to-action areas.
    """
    
    # Hero Section
    hero_title = models.CharField(
        max_length=200,
        default="Student Exchange Information Manager"
    )
    hero_subtitle = models.TextField(
        max_length=500,
        default="Streamline your student exchange program management"
    )
    hero_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    hero_cta_text = models.CharField(
        max_length=50,
        default="Get Started",
        blank=True
    )
    hero_cta_link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    # Content sections
    body = StreamField(
        BaseStreamBlock(),
        null=True,
        blank=True,
        use_json_field=True,
        help_text="Main content area with flexible blocks"
    )
    
    # Settings
    show_in_menus_default = True
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('hero_title'),
            FieldPanel('hero_subtitle'),
            FieldPanel('hero_image'),
            FieldPanel('hero_cta_text'),
            FieldPanel('hero_cta_link'),
        ], heading="Hero Section"),
        FieldPanel('body'),
    ]
    
    promote_panels = SeoMixin.seo_panels
    
    class Meta:
        verbose_name = "Home Page"
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['is_homepage'] = True
        return context


# ============================================================================
# STANDARD PAGE
# ============================================================================

class StandardPage(SeoMixin, Page):
    """
    Flexible page for general information and content.
    """
    
    introduction = models.TextField(
        max_length=500,
        blank=True,
        help_text="Page introduction/summary"
    )
    
    body = StreamField(
        BaseStreamBlock(),
        use_json_field=True,
        help_text="Main content area with flexible blocks"
    )
    
    # Sidebar options
    show_sidebar = models.BooleanField(default=False)
    sidebar_content = RichTextField(blank=True)
    
    # Related pages
    related_pages = ParentalManyToManyField(
        'wagtailcore.Page',
        blank=True,
        related_name='+'
    )
    
    search_fields = Page.search_fields + [
        index.SearchField('introduction'),
        index.SearchField('body'),
    ]
    
    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
        FieldPanel('body'),
        MultiFieldPanel([
            FieldPanel('show_sidebar'),
            FieldPanel('sidebar_content'),
        ], heading="Sidebar"),
        FieldPanel('related_pages'),
    ]
    
    promote_panels = SeoMixin.seo_panels
    
    class Meta:
        verbose_name = "Standard Page"


# ============================================================================
# BLOG SYSTEM
# ============================================================================

@register_snippet
class BlogCategory(models.Model):
    """Blog post category."""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
        FieldPanel('description'),
    ]
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"
        ordering = ['name']


class BlogPostTag(TaggedItemBase):
    """Tag for blog posts."""
    
    content_object = ParentalKey(
        'cms.BlogPostPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


class BlogIndexPage(SeoMixin, Page):
    """
    Index page for blog posts.
    Lists all published blog posts with filtering by category and tag.
    """
    
    introduction = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
    ]
    
    promote_panels = SeoMixin.seo_panels
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        
        # Get all published blog posts
        blog_posts = BlogPostPage.objects.live().public().order_by('-first_published_at')
        
        # Filter by category
        category = request.GET.get('category')
        if category:
            blog_posts = blog_posts.filter(categories__slug=category)
        
        # Filter by tag
        tag = request.GET.get('tag')
        if tag:
            blog_posts = blog_posts.filter(tags__slug=tag)
        
        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(blog_posts, 10)  # Show 10 posts per page
        
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        
        context['blog_posts'] = posts
        context['categories'] = BlogCategory.objects.all()
        
        return context
    
    class Meta:
        verbose_name = "Blog Index Page"


class BlogPostPage(SeoMixin, Page):
    """
    Individual blog post page.
    """
    
    published_date = models.DateField("Post date")
    author = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='blog_posts'
    )
    
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    introduction = models.TextField(
        max_length=500,
        help_text="Post summary/excerpt"
    )
    
    body = StreamField(
        BaseStreamBlock(),
        use_json_field=True,
        help_text="Post content"
    )
    
    categories = ParentalManyToManyField(
        'cms.BlogCategory',
        blank=True,
        related_name='posts'
    )
    
    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)
    
    search_fields = Page.search_fields + [
        index.SearchField('introduction'),
        index.SearchField('body'),
    ]
    
    content_panels = Page.content_panels + [
        FieldPanel('published_date'),
        FieldPanel('author'),
        FieldPanel('featured_image'),
        FieldPanel('introduction'),
        FieldPanel('body'),
        FieldPanel('categories'),
        FieldPanel('tags'),
    ]
    
    promote_panels = SeoMixin.seo_panels
    
    parent_page_types = ['cms.BlogIndexPage']
    
    class Meta:
        verbose_name = "Blog Post"
        ordering = ['-first_published_at']
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        
        # Get related posts (same category, excluding current)
        related_posts = BlogPostPage.objects.live().public().filter(
            categories__in=self.categories.all()
        ).exclude(pk=self.pk).distinct()[:3]
        
        context['related_posts'] = related_posts
        
        return context


# ============================================================================
# PROGRAM PAGES
# ============================================================================

class ProgramIndexPage(SeoMixin, Page):
    """
    Index page for exchange programs.
    Lists all active programs with filtering options.
    """
    
    introduction = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
    ]
    
    promote_panels = SeoMixin.seo_panels
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        
        # Get all published program pages
        programs = ProgramPage.objects.live().public().order_by('-first_published_at')
        
        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(programs, 12)  # Show 12 programs per page
        
        try:
            program_pages = paginator.page(page)
        except PageNotAnInteger:
            program_pages = paginator.page(1)
        except EmptyPage:
            program_pages = paginator.page(paginator.num_pages)
        
        context['programs'] = program_pages
        
        return context
    
    class Meta:
        verbose_name = "Program Index Page"


class ProgramPage(SeoMixin, Page):
    """
    Individual exchange program page.
    Links to the Exchange app's Program model for application workflow.
    """
    
    # Link to Exchange Program model
    program = models.OneToOneField(
        'exchange.Program',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cms_page',
        help_text="Link to the exchange program in the system"
    )
    
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    introduction = models.TextField(
        max_length=500,
        help_text="Program summary"
    )
    
    body = StreamField(
        BaseStreamBlock(),
        use_json_field=True,
        help_text="Detailed program information"
    )
    
    # Quick info fields
    location = models.CharField(max_length=200, blank=True)
    duration = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=100, blank=True)
    application_deadline = models.DateField(null=True, blank=True)
    
    search_fields = Page.search_fields + [
        index.SearchField('introduction'),
        index.SearchField('body'),
        index.SearchField('location'),
    ]
    
    content_panels = Page.content_panels + [
        FieldPanel('program'),
        FieldPanel('featured_image'),
        FieldPanel('introduction'),
        MultiFieldPanel([
            FieldPanel('location'),
            FieldPanel('duration'),
            FieldPanel('language'),
            FieldPanel('application_deadline'),
        ], heading="Quick Information"),
        FieldPanel('body'),
    ]
    
    promote_panels = SeoMixin.seo_panels
    
    parent_page_types = ['cms.ProgramIndexPage']
    
    class Meta:
        verbose_name = "Program Page"
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['exchange_program'] = self.program
        return context


# ============================================================================
# FAQ SYSTEM
# ============================================================================

class FAQIndexPage(SeoMixin, Page):
    """
    Index page for FAQs organized by category.
    """
    
    introduction = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
    ]
    
    promote_panels = SeoMixin.seo_panels
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        
        # Get all published FAQ pages
        faqs = FAQPage.objects.live().public().order_by('title')
        
        context['faq_pages'] = faqs
        
        return context
    
    class Meta:
        verbose_name = "FAQ Index Page"


class FAQPage(SeoMixin, Page):
    """
    FAQ page with questions and answers.
    """
    
    introduction = models.TextField(max_length=500, blank=True)
    
    body = StreamField(
        BaseStreamBlock(),
        use_json_field=True,
        help_text="FAQ content (use FAQ blocks for Q&A sections)"
    )
    
    search_fields = Page.search_fields + [
        index.SearchField('introduction'),
        index.SearchField('body'),
    ]
    
    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
        FieldPanel('body'),
    ]
    
    promote_panels = SeoMixin.seo_panels
    
    parent_page_types = ['cms.FAQIndexPage']
    
    class Meta:
        verbose_name = "FAQ Page"


# ============================================================================
# FORM BUILDER
# ============================================================================

class FormField(AbstractFormField):
    """
    Form field for Wagtail form builder.
    """
    
    page = ParentalKey(
        'cms.FormPage',
        on_delete=models.CASCADE,
        related_name='form_fields'
    )


class FormPage(SeoMixin, AbstractEmailForm):
    """
    Dynamic form page using Wagtail's form builder.
    Replaces django-dynforms functionality.
    """
    
    introduction = RichTextField(blank=True)
    thank_you_text = RichTextField(
        blank=True,
        help_text="Text to display after form submission"
    )
    
    # Link to Exchange Program for application forms
    linked_program = models.ForeignKey(
        'exchange.Program',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='form_pages',
        help_text="Link this form to an exchange program"
    )
    
    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('introduction'),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('thank_you_text'),
        FieldPanel('linked_program'),
        MultiFieldPanel([
            FieldPanel('to_address'),
            FieldPanel('from_address'),
            FieldPanel('subject'),
        ], heading="Email Settings"),
    ]
    
    promote_panels = SeoMixin.seo_panels + [
        FormSubmissionsPanel(),
    ]
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['exchange_program'] = self.linked_program
        return context
    
    def serve(self, request, *args, **kwargs):
        """Handle form submission and link to Exchange Application if applicable."""
        if request.method == 'POST':
            form = self.get_form(request.POST, request.FILES, page=self, user=request.user)
            
            if form.is_valid():
                form_submission = self.process_form_submission(form)
                
                # If linked to a program, create/update Exchange Application
                if self.linked_program and request.user.is_authenticated:
                    from exchange.services import ApplicationService
                    # Create or update application linked to this form submission
                    # This can be implemented based on business logic
                    pass
                
                return self.render_landing_page(request, form_submission, *args, **kwargs)
        else:
            form = self.get_form(page=self, user=request.user)
        
        context = self.get_context(request, *args, **kwargs)
        context['form'] = form
        return render(request, self.get_template(request, *args, **kwargs), context)
    
    class Meta:
        verbose_name = "Form Page"
