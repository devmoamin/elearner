from django.test import TestCase
from django.test import TestCase
from django.contrib.auth.models import User

from courses.models import Course, CourseLesson, CourseCategory, CourseInstructor

# Create your tests here.

class CoursesTestCase(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username="testuser", password="password123")

        # Create a category
        self.category = CourseCategory.objects.create(title="Programming Languages")

        # Create an instructor
        self.instructor = CourseInstructor.objects.create(
            name="Test Instructor",
            bio="Test Instructor Bio"
        )

        # Create a course
        self.course = Course.objects.create(
            title="Test Course",
            description="This is a test course.",
            duration_weeks=6,
            thumbnail="course_thumbnails/test_course.jpg",
            category_id=1,
            instructor_id=1,
            difficulty="BE"
        )

        # Create 3 lessons for the course
        for i in range(1, 4):
            lesson = CourseLesson.objects.create(
                course=self.course,
                title=f"Lesson {i}",
                brief=f"Brief for lesson {i}.",
                description=f"This is the detailed description for lesson {i}.",
                youtube_link="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            )
            setattr(self, f'lesson{i}', lesson)

    def test_user_cannot_access_course_before_enrollment(self):
        """Test that user can't access any course before enrollment"""
        pending, current, completed, suggested = Course.objects.get_user_courses(self.user)
        self.assertEqual(len(pending), 0)
        self.assertEqual(len(completed), 0)
        self.assertEqual(len(current), 0)

        with self.assertRaises((Course.DoesNotExist, CourseLesson.DoesNotExist)):
            Course.objects.get_lesson(self.user, self.course.id, self.lesson1.id)

    def test_user_enrollment_in_course(self):
        """Test that a user can enroll in a course and it is added to pending enrollments."""
        Course.objects.enroll(self.user, self.course.id)
        pending, current, completed, suggested = Course.objects.get_user_courses(self.user)
        self.assertEqual(len(pending), 1)
        self.assertEqual(len(current), 0)
        self.assertEqual(len(completed), 0)

    def _get_approved_enrollment(self):
        enrollment = Course.objects.enroll(self.user, self.course.id)
        enrollment.approved = True
        enrollment.save()
        return enrollment

    def test_course_access_after_approval(self):
        """Test that a user can access the course after enrollment is approved."""
        self._get_approved_enrollment()

        pending, current, completed, suggested = Course.objects.get_user_courses(self.user)
        self.assertEqual(len(current), 1)
        self.assertEqual(len(pending), 0)
        self.assertEqual(len(completed), 0)

        can_access = True
        try:
            Course.objects.get_lesson(self.user, self.course.id, self.lesson1.id)
        except (Course.DoesNotExist, CourseLesson.DoesNotExist):
            can_access = False

        self.assertEqual(can_access, True)

    def test_certificate_download_before_completion(self):
        """Test that a user cannot download a certificate before completing the course."""
        enrollment = self._get_approved_enrollment()

        self.assertEqual(enrollment.can_download_certificate, False)

    def _complete_course_lesson(self, all=False):
        Course.objects.complete_lesson(self.user, self.course.id, self.lesson1.id)

        if all:
            Course.objects.complete_lesson(self.user, self.course.id, self.lesson2.id)
            Course.objects.complete_lesson(self.user, self.course.id, self.lesson3.id)

    def test_user_course_progress_and_completion(self):
        """Test course lessons progress is tracked correctly"""
        enrollment = self._get_approved_enrollment()
        
        # complete first lesson
        self._complete_course_lesson()
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.progress, 33.33)

        # complete second lesson
        Course.objects.complete_lesson(self.user, self.course.id, self.lesson2.id)
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.progress, 66.67)

        # complete third lesson
        Course.objects.complete_lesson(self.user, self.course.id, self.lesson3.id)
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.progress, 100.0)

    def test_certificate_generation_after_completion(self):
        """Test that a user can generate a certificate after completing the course."""
        enrollment = self._get_approved_enrollment()

        self._complete_course_lesson(True)
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.can_download_certificate, True)
