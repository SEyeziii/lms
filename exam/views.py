from rest_framework import viewsets, exceptions
from users.permissions import CourseStaffOrReadOnlyForStudents
from exam.models import ExaminationForm, ExamSolution, Question, UserAnswerToQuestion
from django.db.models import Q
from imcslms.default_settings import TEACHER
from exam.serializers import ExamSerializer, ExamSolutionSerializer
from model_bakery import baker
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response


class AddAttachmentToQuestion(APIView):

    def post(self, request: Request):
        pass


class ExamViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSerializer
    permission_classes = [CourseStaffOrReadOnlyForStudents]
    filterset_fields = ['lesson_id', ]

    def get_queryset(self):
        user = self.request.user
        return ExaminationForm.objects.all()\
            .filter(
            (Q(lesson__course__in=user.student_for.all()))
            | Q(lesson__course__in=user.staff_for.all())
            | Q(lesson__course__in=user.author_for.all())
        )

    def create(self, request, *args, **kwargs):
        if request.user.groups.filter(name=TEACHER).exists():
            return super().create(request, *args, **kwargs)
        raise exceptions.PermissionDenied


class ExamSolutionViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSolutionSerializer
    permission_classes = [CourseStaffOrReadOnlyForStudents]
    filterset_fields = ['exam', ]

    def get_queryset(self):
        user = self.request.user
        return ExamSolution.objects.all().filter(
            (Q(exam__is_hidden=False)
             & Q(exam__lesson__course__in=user.student_for.all())
             )
            | Q(exam__lesson__course__in=user.staff_for.all())
            | Q(exam__lesson__course__in=user.author_for.all())
        )

    def create(self, request, *args, **kwargs):
        if request.user.groups.filter(name=TEACHER).exists():
            return super().create(request, *args, **kwargs)
        raise exceptions.PermissionDenied

    def perform_create(self, serializer):
        request = serializer.context['request']
        validated_data = serializer.validated_data
        if validated_data['exam'].test_mode == 'manual':
            serializer.save(student=request.user, status=ExamSolution.SOLUTION_STATUS[0], score=0)
            return

        questions = validated_data['exam'].questions
        question_answers = validated_data['user_answers']
        current_score = 0
        correct_questions = []
        for answer in question_answers:
            current_question = questions[answer['question_index']]
            if answer['submitted_answers'] == current_question['correct_answers']:
                current_score += questions[answer['question_index']]['points']
                correct_questions.append(answer['question_index'])
        serializer.save(student=request.user, status=ExamSolution.SOLUTION_STATUS[1], score=current_score,
                        correct_questions_indexes=correct_questions)
        return

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset)