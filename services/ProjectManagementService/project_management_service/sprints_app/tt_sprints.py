import pytest
import django

from datetime import timedelta
from django.utils import timezone

from projects_app.models import Project
from sprints_app.models import Sprint

@pytest.mark.django_db
def test_sprint_creation_without_project():
    sprint_name = "TestSprintName"

    with pytest.raises(django.db.utils.IntegrityError):
        Sprint.objects.create(name=sprint_name)

@pytest.mark.django_db
def test_sprint_creation_successful():
    project_name = "TestProject"
    project_id = "TTP"
    sprint_name = "TestSprintName"

    proj = Project.objects.create(project_name=project_name, id=project_id)
    sp = Sprint.objects.create(name=sprint_name, project=proj)

    assert sp.name == sprint_name
    assert sp.id == 1
    assert sp.project.project_name == project_name

@pytest.mark.django_db
def test_sprint_validators():
    short_name = "XX"
    long_name = "X" * 33
    project_name = "TestProject"
    project_id = "TTP"

    proj = Project.objects.create(project_name=project_name, id=project_id)
    with pytest.raises(django.core.exceptions.ValidationError):
        sp1 = Sprint.objects.create(name=short_name, project=proj)
        sp1.full_clean()
    with pytest.raises(django.core.exceptions.ValidationError):
        sp2 = Sprint.objects.create(name=long_name, project=proj)
        sp2.full_clean()

@pytest.mark.django_db
def test_sprint_accessible_from_project():
    project_name = "TestProject"
    project_id = "TTP"
    sprint_name = "TestSprintName"

    proj = Project.objects.create(project_name=project_name, id=project_id)
    sp = Sprint.objects.create(name=sprint_name, project=proj)

    assert proj.sprints.first().id == sp.id

@pytest.mark.django_db
def test_sprint_status_from_created_to_started():
    project_name = "TestProject"
    project_id = "TTP"
    sprint_name = "TestSprintName"

    proj = Project.objects.create(project_name=project_name, id=project_id)
    sp = Sprint.objects.create(name=sprint_name, project=proj)

    assert sp.status == Sprint.SprintStatus.CREATED
    assert sp.start_date is None
    assert sp.close_date is None

    sp.start_sprint()

    assert sp.start_date is not None
    assert abs(sp.start_date - timezone.now()) < timedelta(seconds=5)
    assert sp.close_date is None


@pytest.mark.django_db
def test_sprint_status_from_started_to_closed():
    project_name = "TestProject"
    project_id = "TTP"
    sprint_name = "TestSprintName"

    proj = Project.objects.create(project_name=project_name, id=project_id)
    sp = Sprint.objects.create(name=sprint_name, project=proj,
                               status=Sprint.SprintStatus.STARTED, start_date=timezone.now())

    assert sp.status == Sprint.SprintStatus.STARTED
    assert sp.start_date is not None
    assert sp.close_date is None

    sp.close_sprint()

    assert sp.start_date is not None
    assert sp.close_date is not None
    assert abs(sp.close_date - timezone.now()) < timedelta(seconds=5)


@pytest.mark.django_db
def test_sprint_status_invalid_transition():
    project_name = "TestProject"
    project_id = "TTP"
    sprint_name = "TestSprintName"

    proj = Project.objects.create(project_name=project_name, id=project_id)
    with pytest.raises(Sprint.InvalidSprintStatusTransition):
        sp1 = Sprint.objects.create(name=sprint_name, project=proj)
        assert sp1.status == Sprint.SprintStatus.CREATED
        sp1.close_sprint()

    with pytest.raises(Sprint.InvalidSprintStatusTransition):
        sp2 = Sprint.objects.create(name=sprint_name, project=proj,
                                   status=Sprint.SprintStatus.STARTED, start_date=timezone.now())
        assert sp2.status == Sprint.SprintStatus.STARTED
        sp2.start_sprint()

    with pytest.raises(Sprint.InvalidSprintStatusTransition):
        sp3 = Sprint.objects.create(name=sprint_name, project=proj,
                                   status=Sprint.SprintStatus.CLOSED, start_date=timezone.now(),
                                    close_date=timezone.now())
        assert sp3.status == Sprint.SprintStatus.CLOSED
        sp3.start_sprint()

    with pytest.raises(Sprint.InvalidSprintStatusTransition):
        sp4 = Sprint.objects.create(name=sprint_name, project=proj,
                                   status=Sprint.SprintStatus.CLOSED, start_date=timezone.now(),
                                    close_date=timezone.now())
        assert sp4.status == Sprint.SprintStatus.CLOSED
        sp3.close_sprint()






