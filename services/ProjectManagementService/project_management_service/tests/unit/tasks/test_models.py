import uuid

import pytest
import django.core.exceptions
import django.db.models

from projects_app.models import Project, ProjectMember


@pytest.mark.django_db
def test_project_creates_successfully():
    # Given
    name = "TestProject"
    id = "TTP"
    index = 0

    # When
    obj = Project.objects.create(project_name=name, id=id)
    obj.full_clean()

    # Then
    assert obj.project_name == name
    assert obj.id == id
    assert obj.last_task_index == index


@pytest.mark.django_db
def test_project_blank_name_validator():
    # Given
    name = ""
    id = "TTT"

    # When - Then
    with pytest.raises(django.core.exceptions.ValidationError):
        obj = Project.objects.create(project_name=name, id=id)
        obj.full_clean()


@pytest.mark.django_db
def test_project_to_short_name_validator():
    # Given
    name = "AA"
    id = "TTA"

    # When - Then
    with pytest.raises(django.core.exceptions.ValidationError):
        obj = Project.objects.create(project_name=name, id=id)
        obj.full_clean()


@pytest.mark.django_db
def test_project_to_long_name_validator():
    # Given
    name = "B" * 30
    id = "TTC"

    # When - Then
    with pytest.raises(django.core.exceptions.ValidationError):
        obj = Project.objects.create(project_name=name, id=id)
        obj.full_clean()


@pytest.mark.django_db
def test_project_to_short_id_validator():
    # Given
    name = "AAAAA"
    id = "TT"

    # When - Then
    with pytest.raises(django.core.exceptions.ValidationError):
        obj = Project.objects.create(project_name=name, id=id)
        obj.full_clean()

@pytest.mark.django_db
def test_project_to_long_id_validator():
    # Given
    name = "AACC"
    id = "TTTT"

    # When - Then
    with pytest.raises(django.core.exceptions.ValidationError):
        obj = Project.objects.create(project_name=name, id=id)
        obj.full_clean()

@pytest.mark.django_db
@pytest.mark.parametrize('role', list(ProjectMember.Role))
def test_add_member_to_project_successfully(role):
    # Given
    name = "Project"
    id = "TTT"
    user_id = uuid.uuid4()

    # When
    project = Project.objects.create(project_name=name, id=id)
    project.full_clean()
    ProjectMember.objects.create(user_id=user_id, project=project, role=role)

    # Then
    obj = ProjectMember.objects.all().first()
    assert obj.user_id == str(user_id)
    assert obj.project.id == id
    assert obj.role == role


@pytest.mark.django_db
def test_add_member_already_exists():
    # TO DO: LOGIC TO FIX - No safety mechanisms to prevent duplicated records (project methods not used in serializers)
    # Given
    name = "Project"
    id = "TTT"
    user_id = uuid.uuid4()
    role = ProjectMember.Role.DEVELOPER
    project = Project.objects.create(project_name=name, id=id)
    project.full_clean()
    member1 = ProjectMember.objects.create(user_id=user_id, project=project, role=role)
    member1.full_clean()

    # When
    member2 = ProjectMember.objects.create(user_id=user_id, project=project, role=role)
    member2.full_clean()

    print(member1.id)
    print(member2.id)


@pytest.mark.django_db
def test_remove_member_successfully():
    # TO DO: LOGIC TO FIX - members removed via serializers
    pass


@pytest.mark.django_db
def test_project_find_role_by_user_id_successfully():
    # Given
    name = "Project"
    id = "TTT"
    user_id = uuid.uuid4()
    role = ProjectMember.Role.VIEWER
    project = Project.objects.create(project_name=name, id=id)
    project.full_clean()
    member = ProjectMember.objects.create(user_id=user_id, project=project, role=role)
    member.full_clean()

    # When
    saved_role = project.role_by_user_id(user_id)

    # Then
    assert saved_role == role


@pytest.mark.django_db
def test_project_find_role_by_user_id_not_exists():
    # Given
    name = "Project"
    id = "TTT"
    user_id = uuid.uuid4()
    role = ProjectMember.Role.VIEWER
    project = Project.objects.create(project_name=name, id=id)
    project.full_clean()
    member = ProjectMember.objects.create(user_id=user_id, project=project, role=role)
    member.full_clean()

    # When
    saved_role = project.role_by_user_id(str(uuid.uuid4()))

    # Then
    assert saved_role is None

@pytest.mark.django_db
def test_project_get_members_list():
    # Given
    name = "Project"
    id = "TTT"
    users = {
        str(uuid.uuid4()): ProjectMember.Role.VIEWER,
        str(uuid.uuid4()): ProjectMember.Role.DEVELOPER,
        str(uuid.uuid4()): ProjectMember.Role.ADMIN
    }
    project = Project.objects.create(project_name=name, id=id)
    project.full_clean()
    for user_id, role in users.items():
        member = ProjectMember.objects.create(project=project, user_id=user_id, role=role)
        member.full_clean()

    # When
    members = project.get_members()

    # Then
    assert len(users) == len(members)
    for m in members:
        assert m.role == users[m.user_id]


@pytest.mark.django_db
def test_project_get_members_list_with_role():
    # Given
    name = "Project"
    id = "TTT"
    users = {
        str(uuid.uuid4()): ProjectMember.Role.VIEWER,
        str(uuid.uuid4()): ProjectMember.Role.DEVELOPER,
        str(uuid.uuid4()): ProjectMember.Role.ADMIN,
        str(uuid.uuid4()): ProjectMember.Role.DEVELOPER
    }
    project = Project.objects.create(project_name=name, id=id)
    project.full_clean()
    for user_id, role in users.items():
        member = ProjectMember.objects.create(project=project, user_id=user_id, role=role)
        member.full_clean()

    # When
    members = project.get_members(role=ProjectMember.Role.DEVELOPER)

    # Then
    assert 2 == len(members)
    for m in members:
        assert m.role == users[m.user_id]


@pytest.mark.django_db
def test_project_members_when_project_deleted():
    # Given
    name = "Project"
    id = "TTT"
    user_id = uuid.uuid4()
    role = ProjectMember.Role.VIEWER
    project = Project.objects.create(project_name=name, id=id)
    project.full_clean()
    member = ProjectMember.objects.create(user_id=user_id, project=project, role=role)
    member.full_clean()
    project_id = project.pk

    # When
    project.delete()

    # Then
    assert ProjectMember.objects.filter(project=project_id).count() == 0


@pytest.mark.django_db
def test_project_get_project_implementation():
    # Given
    name = "Project"
    id = "TTT"
    created_project = Project.objects.create(project_name=name, id=id)
    created_project.full_clean()

    # When
    fetched_project = created_project.get_project()

    # Then
    assert fetched_project is created_project


@pytest.mark.django_db
def test_project_member_get_project_implementation():
    # Given
    name = "Project"
    id = "TTT"
    user_id = uuid.uuid4()
    role = ProjectMember.Role.VIEWER
    created_project = Project.objects.create(project_name=name, id=id)
    member = ProjectMember.objects.create(user_id=user_id, project=created_project, role=role)
    member.full_clean()

    # When
    fetched_project = member.get_project()

    # Then
    assert fetched_project is created_project


