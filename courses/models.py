import uuid
from django.db import models
from django.http import Http404
from django.contrib.auth.models import User
from django.utils import timezone


COURSE_DIFFICULTY_OPTIONS = [
    ('BE', 'Beginner'), 
    ('IN', 'Intermediate'), 
    ('AD', 'Advanced')
]

class CourseManager(models.Manager):
    def enroll(self, user, course_id):
        exists = CourseEnrollment.objects.filter(course=course_id, user=user).exists()
        if exists:
            return
        
        enrollment = CourseEnrollment(course_id=course_id, user=user)
        enrollment.save()

    def complete_lesson(self, user, course_id, lesson_id):
        try:
            course = self.get(id=course_id)
            if not user.is_authenticated or not course.is_enrolled(user):
                raise Course.DoesNotExist
            
            lesson = course.lessons.get(id=lesson_id)
            enrollment = course.enrollments.get(user=user)

            exists = enrollment.attended_lessons.contains(lesson)
            if not exists:
                enrollment.attended_lessons.add(lesson)

            next_lesson = course.lessons.filter(id__gt=lesson_id).first()
            if next_lesson is not None:
                enrollment.current_lesson = next_lesson
                enrollment.save()
                return next_lesson.id
            
            if enrollment.completed_date is None:
                enrollment.completed_date = timezone.now()
                enrollment.certificate_id = uuid.uuid4().hex
                enrollment.save()

        except (Course.DoesNotExist, CourseLesson.DoesNotExist):
            raise Http404("No lesson found matching the query")

    def get_lesson(self, user, course_id, lesson_id):
        try:
            course = Course.objects.get(id=course_id)
            if not user.is_authenticated or not course.is_enrolled(user):
                raise Course.DoesNotExist
            
            lesson = course.lessons.get(id=lesson_id)
            return lesson
        except (Course.DoesNotExist, CourseLesson.DoesNotExist):
            raise Http404("No lesson found matching the query")
        
    def get_user_courses(self, user):
        enrollments = CourseEnrollment.objects.filter(user=user).all()
        courses = [e.course_id for e in enrollments]
        categories = [e.course.category_id for e in enrollments]
        suggested = Course.objects.filter(category__in=categories).exclude(id__in=courses)[:5]
        pending = []
        current = []
        completed = []
        
        for i in enrollments:
            if i.approved and not i.is_completed:
                current.append(i)
            if i.is_completed:
                completed.append(i)
            if not i.approved:
                pending.append(i)
        
        return (pending, current, completed, suggested)


class CourseCategory(models.Model):
    title = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Course Categories"

    def __str__(self):
        return self.title
    

class CourseInstructor(models.Model):
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='instructors/')
    bio = models.TextField()

    def __str__(self):
        return self.name


class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(CourseCategory, related_name='courses', on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=5, choices=COURSE_DIFFICULTY_OPTIONS)
    duration_weeks = models.PositiveIntegerField()
    instructor = models.ForeignKey(CourseInstructor, on_delete=models.CASCADE, related_name='instructed_courses')
    rating = models.FloatField(default=0.0)
    thumbnail = models.ImageField(upload_to='course_thumbnails/')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CourseManager()

    def __str__(self):
        return self.title
    
    @property
    def entrolled_count(self):
        return self.entrollments.count()
    
    def get_enrollment(self, user):
        if not user.is_authenticated:
            return None
        return self.enrollments.filter(user=user).first()
    
    def is_enrolled(self, user):
        if not user.is_authenticated:
            return False
        return self.enrollments.filter(user=user).exists()
    
    def enroll(self, user):
        self.__class__.objects.enroll(user, self)


class CourseLesson(models.Model):
    title = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    youtube_link = models.URLField()
    description = models.TextField()
    brief = models.CharField(max_length=300)
    file = models.FileField(upload_to='lessons/', null=True, blank=True)

    def __str__(self):
        return self.title
    
    def complete(self, user):
        Course.objects.attend_course(user, self)
    

class CourseEnrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    current_lesson = models.ForeignKey(CourseLesson, on_delete=models.CASCADE, null=True, related_name='enrollments_at')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entrollments')
    approved = models.BooleanField(default=False)
    entrolled_at = models.DateTimeField(auto_now_add=True)
    attended_lessons = models.ManyToManyField(CourseLesson, related_name='attended_by')
    completed_date = models.DateTimeField(null=True, editable=False)

    def __str__(self):
        return f"{self.course.title} | {self.user.username}"

    @property
    def progress(self):
        lessons_count = self.course.lessons.count()
        attended_count = self.attended_lessons.count()
        return 0 if lessons_count == 0 else round((attended_count / lessons_count) * 100, 2)
    
    @property
    def next_lesson(self):
        return self.current_lesson.id if self.current_lesson is not None else self.course.lessons.first().id
    
    @property
    def is_completed(self):
        lessons_count = self.course.lessons.count()
        attended_count = self.attended_lessons.count()
        return lessons_count == attended_count
