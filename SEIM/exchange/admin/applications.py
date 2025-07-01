from django.contrib import admin
from ..models import Comment, Review, Timeline, WorkflowLog

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    pass

@admin.register(Timeline)
class TimelineAdmin(admin.ModelAdmin):
    pass

@admin.register(WorkflowLog)
class WorkflowLogAdmin(admin.ModelAdmin):
    pass
