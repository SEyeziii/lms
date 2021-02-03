import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core import exceptions
from django.forms import Form, CharField, PasswordInput
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
)
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from users.models import User
from users.serializers import DefaultUserSerializer


@login_required(login_url=reverse_lazy('account_login'))
def index(request, *args, **kwargs):
    user = User.objects.prefetch_related('staff_for', 'student_for').get(pk=request.user.id)
    user_data = json.dumps(DefaultUserSerializer(instance=user, exclude_staff=False).data)
    return render(request, 'index.html', context=dict(user_data=user_data))


class LoginForm(Form):
    username = CharField()
    password = CharField(widget=PasswordInput)


def user_login(request):
    if request.method == 'GET':
        return render(request, 'login.html', {'form': LoginForm()})

    form = LoginForm(request.POST)
    ctx = dict(error=True, form=form)
    if not form.is_valid():
        return render(request, 'login.html', dict(**ctx, message='Ошибка чтения формы (ง’̀-‘́)ง'))
    user = authenticate(**form.cleaned_data)
    if user and user.is_active:
        login(request, user)
        return redirect('index')
    if user and not user.is_active:
        return render(request, 'login.html', dict(
            **ctx, error_message='Аккаунт заблокирован. Обратитесь к системному администратору.'
        ))
    try:
        User.objects.get(username=form.cleaned_data['username'])
    except User.DoesNotExist:
        return render(request, 'login.html', dict(**ctx, error_message='Указанный пользователь не существует.'))
    return render(request, 'login.html', dict(**ctx, error_message='Логин и пароль не совпадают'))


class UsersViewSet(GenericViewSet, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin):
    serializer_class = DefaultUserSerializer
    queryset = User.objects.all()


@login_required
@api_view(['GET'])
@renderer_classes([JSONRenderer])
def students_for_course(request: HttpRequest, course_id):
    queryset = User.objects.exclude(student_for__id=course_id).exclude(staff_for__id=course_id) \
        .all().values_list('id', 'username', 'first_name', 'middle_name', 'last_name', 'avatar_url')
    return Response(list(queryset))


@login_required
@api_view(['GET'])
@renderer_classes([JSONRenderer])
def staff_for_course(request: HttpRequest, course_id):
    try:
        group = Group.objects.get(name='staff')
    except exceptions.ObjectDoesNotExist:
        return Response(list())
    queryset = User.objects \
        .filter(group=group) \
        .exclude(student_for__id=course_id) \
        .exclude(staff_for__id=course_id) \
        .values_list('id', 'username', 'first_name', 'middle_name', 'last_name', 'avatar_url')
    return Response(list(queryset))


@login_required
@api_view(['POST'])
@renderer_classes([JSONRenderer])
def change_password(request):
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    user = request.user
    if not user.check_password(old_password):
        return HttpResponse('Unauthorized', status=401)
    user.set_password(new_password)
    user.save()
    return Response({'code': 0, 'message': 'Password changed successfully'})
