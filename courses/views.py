from django.urls import reverse
from django.http.response import HttpResponseRedirect, HttpResponse
from django.views.generic import ListView, DetailView, View, TemplateView
from django.http import Http404
from .models import Course, CourseCategory, CourseLesson, COURSE_DIFFICULTY_OPTIONS
from .certificate import generate_certificate

# Create your views here.

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_template_names(self):
        if not self.request.user.is_authenticated:
            return ['landing.html']
        return super().get_template_names()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.request.user.is_authenticated:
            return context

        pending, current, completed, suggested = Course.objects.get_user_courses(self.request.user)
        context['pending_courses'] = pending
        context['current_courses'] = current
        context['completed_courses'] = completed
        context['suggested_courses'] = suggested
        return context


class CourseListView(ListView):
    model = Course
    template_name = 'courses.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = Course.objects.all()
        search_query = self.request.GET.get('q', None)
        category = self.request.GET.get('cat', None)
        difficulty = self.request.GET.get('dif', None)

        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
        if category:
            queryset = queryset.filter(category=category)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        courses = self.object_list
        context['courses'] = courses
        context['categories'] = CourseCategory.objects.all()
        context['levels'] = COURSE_DIFFICULTY_OPTIONS
        context['search_q'] = self.request.GET.get('q', '')
        context['dif'] = self.request.GET.get('dif', '')
        context['cat'] = int(self.request.GET.get('cat', '0'))
        return context


class CourseDetailView(DetailView):
    model = Course
    template_name = 'course_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = context['course']
        enrollment = course.get_enrollment(self.request.user)
        context['is_enrolled'] = enrollment is not None
        context['is_approved'] = enrollment is not None and enrollment.approved
        return context
    

class CourseCertificateView(DetailView):
    model = Course
    template_name = 'certificate.html'
    pk_url_kwarg = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = context['course']
        enrollment = course.get_enrollment(self.request.user)
        if enrollment is None or not enrollment.approved:
            raise Http404
        
        context['is_completed'] = enrollment.is_completed
        context['progress_percentage'] = enrollment.progress
        context['next_lesson'] = enrollment.next_lesson
        return context
    

class GenerateCertificateView(View):
    def get(self, request, *args, **kwargs):
        course_id = kwargs.get('course')
        
        if not request.user.is_authenticated:
            raise Http404

        course = Course.objects.get(id=course_id)  # Fetch the course object
        enrollment = course.get_enrollment(request.user)
        if enrollment is None or not enrollment.approved or not enrollment.is_completed:
            raise Http404
        
        response = HttpResponse(content_type='application/pdf')        
        response['Content-Disposition'] = f'attachment; filename="certificate_{course.title}.pdf"'
        generate_certificate(response, request.user, course, enrollment)
        return response
    

class ClassroomView(DetailView):
    model = CourseLesson
    template_name = "classroom.html"

    def get_object(self, queryset = ...):
        course_id = self.kwargs.get('course')
        lesson_id = self.kwargs.get('lesson')
        return Course.objects.get_lesson(self.request.user, course_id, lesson_id)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = context['courselesson']
        enrollment = lesson.course.get_enrollment(self.request.user)
        attended_lessons = enrollment.attended_lessons.values_list('id', flat=True)
        next_lesson = lesson.course.lessons.filter(id__gt=lesson.id).exists()

        context['current_lesson'] = lesson
        context['attended_lessons'] = attended_lessons
        context['has_next_lesson'] = next_lesson
        return context


class CourseEnrollView(View):
    def post(self, request, *args, **kwargs):
        course_id = kwargs.get('pk')

        if not request.user.is_authenticated:
            next_url = reverse('course_detail', kwargs={'pk': course_id})
            return HttpResponseRedirect(reverse('login') + f"?next={next_url}")
        
        Course.objects.enroll(request.user, course_id)
        return HttpResponseRedirect(reverse('enroll_success'))
    

class CompleteLessonView(View):
    def post(self, request, *args, **kwargs):
        course_id = kwargs.get('course')
        lesson_id = kwargs.get('lesson')
        next_lesson_id = Course.objects.complete_lesson(request.user, course_id, lesson_id)
        if next_lesson_id is None:
            return HttpResponseRedirect(reverse('completed_course', kwargs={'course': course_id}))
        return HttpResponseRedirect(reverse('classroom', kwargs={'course': course_id, 'lesson': next_lesson_id}))
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    