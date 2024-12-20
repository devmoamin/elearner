from django.urls import path
from django.views.generic import TemplateView
from courses.views import (
    CourseListView, CourseDetailView, CourseEnrollView, ClassroomView, 
    CompleteLessonView, CourseCertificateView, GenerateCertificateView
)

urlpatterns = [
    path('', CourseListView.as_view(), name='courses'),
    path('enroll/success', TemplateView.as_view(template_name='enroll_success.html'), name='enroll_success'),
    path('enroll/<pk>', CourseEnrollView.as_view(), name='enroll'),
    path('<pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('classroom/<course>/certificate', CourseCertificateView.as_view(), name='completed_course'),
    path('classroom/<course>/certificate/download', GenerateCertificateView.as_view(), name='generate_certificate'),
    path('classroom/<course>/<lesson>', ClassroomView.as_view(), name='classroom'),
    path('attend/<course>/<lesson>', CompleteLessonView.as_view(), name='complete_lesson')
]
