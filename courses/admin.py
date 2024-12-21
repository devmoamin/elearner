from django.contrib import admin
from courses.models import CourseCategory, Course, CourseLesson, CourseEnrollment, CourseInstructor

# Register your models here.

class CourseLessonInline(admin.StackedInline):
    model = CourseLesson
    extra = 0


class CourseAdmin(admin.ModelAdmin):
    model = Course
    inlines = [CourseLessonInline]


class CourseEnrollmentAdmin(admin.ModelAdmin):
    model = CourseEnrollment
    search_fields = ("user__username", "course__title")
    list_filter = ("approved",)
    readonly_fields = ("course", "user", "current_lesson", "attended_lessons")

    def get_readonly_fields(self, request, obj):
        fields = super().get_readonly_fields(request, obj)
        if obj.approved:
            return ("approved", "course", "user", "current_lesson", "attended_lessons", "completed_date")
        return fields
    
    def has_add_permission(self, request):
        return False
    
    def get_actions(self, request):
        return {}


admin.site.register(CourseCategory)
admin.site.register(Course, CourseAdmin)
admin.site.register(CourseEnrollment, CourseEnrollmentAdmin)
admin.site.register(CourseInstructor)
admin.site.site_title = "E-Learner"
admin.site.site_header = "E-Learner"
admin.site.index_title = "E-Learner Administration"
