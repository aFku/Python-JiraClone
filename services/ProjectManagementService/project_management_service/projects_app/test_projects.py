import django.core.exceptions
import pytest

from projects_app.models import Project, ProjectMember

@pytest.mark.django_db
def test_project_creation():
    name = "TestProject"
    id = "TTP"
    index = 0

    obj = Project.objects.create(project_name=name, id=id)
    obj.full_clean()

    assert obj.project_name == name
    assert obj.id == id
    assert obj.last_task_index == index

@pytest.mark.django_db
def test_project_validators():
    short_id = "XX"
    long_id = "XXXX"
    short_name = "NA"
    long_name = "X" * 26

    with pytest.raises(django.core.exceptions.ValidationError):
        obj1 = Project.objects.create(project_name=short_name, id="XXX")
        obj1.full_clean()
    with pytest.raises(django.core.exceptions.ValidationError):
        obj2 = Project.objects.create(project_name="XXX", id=short_id)
        obj2.full_clean()
    with pytest.raises(django.core.exceptions.ValidationError):
        obj3 = Project.objects.create(project_name=long_name, id="YYY")
        obj3.full_clean()
    with pytest.raises(django.core.exceptions.ValidationError):
        obj4 = Project.objects.create(project_name="XXX", id=long_id)
        obj4.full_clean()

@pytest.mark.django_db
def test_project_member_management():
    name = "TestProject"
    id = "TTP"

    obj = Project.objects.create(project_name=name, id=id)
    assert len(obj.get_members()) == 0

    obj.add_member("User1", ProjectMember.Role.VIEWER)
    obj.add_member("User2", ProjectMember.Role.DEVELOPER)
    obj.add_member("User3", ProjectMember.Role.ADMIN)
    assert len(obj.get_members()) == 3
    assert obj.role_by_user_id("User1") == ProjectMember.Role.VIEWER
    assert obj.role_by_user_id("User2") == ProjectMember.Role.DEVELOPER
    assert obj.role_by_user_id("User3") == ProjectMember.Role.ADMIN
    obj.remove_member("User2")
    assert len(obj.get_members()) == 2







