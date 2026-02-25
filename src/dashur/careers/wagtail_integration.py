"""
Wagtail integration for the careers app.
"""
from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.search import index


class CareersPage(Page):
    """
    Wagtail page for managing careers content.
    """
    intro = RichTextField(blank=True, help_text="Introduction text for the careers page")
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]
    
    class Meta:
        verbose_name = "Careers Page"
    
    def get_context(self, request):
        context = super().get_context(request)
        from .models import JobPosition
        
        # Add active job positions to context
        context['active_positions'] = JobPosition.objects.filter(status='active').order_by('-created_at')
        return context


class JobPositionPage(Page):
    """
    Individual job position page in Wagtail.
    """
    position_id = models.PositiveIntegerField(unique=True)
    description = RichTextField()
    requirements = RichTextField(blank=True)
    benefits = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('position_id'),
        FieldPanel('description'),
        FieldPanel('requirements'),
        FieldPanel('benefits'),
    ]
    
    search_fields = Page.search_fields + [
        index.SearchField('description'),
        index.SearchField('requirements'),
    ]
    
    class Meta:
        verbose_name = "Job Position Page"
