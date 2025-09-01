import uuid
import pytest

from datetime import timedelta
from django.utils import timezone

from tasks_app.models import Task
from projects_app.models import Project
from sprints_app.models import Sprint

import uuid
from datetime import timedelta
from django.utils import timezone


def create_task_for_test(
    *,
    project=None,
    sprint=None,
    parent=None,
    summary="Test ticket",
    description="Nice description",
    assignee=None,
    creator=None,
    due_date=None,
    estimate=5,
    type=Task.TaskType.EPIC,
    priority=Task.Priority.MEDIUM,
):
    """
    Helper function to create a Task for tests with default values.
    All parameters can be overridden by keyword arguments.
    """
    if creator is None:
        creator = uuid.uuid4()

    if due_date is None:
        due_date = timezone.now() + timedelta(days=3)

    # Tworzymy taska
    task = Task.create_for_project(
        project=project,
        summary=summary,
        description=description,
        assignee=assignee,
        creator=creator,
        due_date=due_date,
        parent=parent,
        estimate=estimate,
        type=type,
        priority=priority,
    )

    task.sprint.add(sprint)
    project.refresh_from_db()

    return task


@pytest.mark.django_db
def test_task_create_successful():
    task_summary = "Test ticket"
    task_description = "Nice description"
    task_assignee = None
    task_creator = uuid.uuid4()
    task_due_date = timezone.now() + timedelta(days=3)
    task_estimate = 5
    task_type = Task.TaskType.EPIC
    task_priority = Task.Priority.MEDIUM
    task_expected_status = Task.Status.TO_DO

    project_name = "TestProject"
    project_id = "TTP"
    sprint_name = "TestSprintName"

    project = Project.objects.create(project_name=project_name, id=project_id)
    sprint = Sprint.objects.create(name=sprint_name, project=project)

    task_epic = create_task_for_test(
        project=project,
        sprint=sprint,
        creator=task_creator,
        due_date=task_due_date
    )

    assert task_epic.project == project
    assert task_epic.sprint.filter(id=sprint.id).exists()
    assert task_epic.id == f'{project_id}-{project.last_task_index}'
    assert task_epic.number == project.last_task_index
    assert task_epic.summary == task_summary
    assert task_epic.description == task_description
    assert task_epic.assignee == task_assignee
    assert task_epic.creator == task_creator
    assert task_epic.due_date == task_due_date
    assert abs(task_epic.creation_date - timezone.now()) < timedelta(seconds=5)
    assert abs(task_epic.last_edit_time - timezone.now()) < timedelta(seconds=5)
    assert task_epic.close_date is None
    assert task_epic.estimate == task_estimate
    assert task_epic.type == task_type
    assert task_epic.priority == task_priority
    assert task_epic.status == task_expected_status
    assert task_epic.parent is None

    task_bug_type = Task.TaskType.BUG
    task_bug = create_task_for_test(
        project=project,
        sprint=sprint,
        type=task_bug_type,
        parent=task_epic
    )

    assert task_bug.id == f'{project.id}-{project.last_task_index}'
    # assert task_bug.parent == task_epic #  TO DO: uncomment when add_parent() implemented
    assert task_bug.type == task_bug_type


@pytest.mark.django_db
def test_task_create_without_project():
    with pytest.raises(Task.ProjectRequiredException):
        task = Task.create_for_project(
            project=None,
            summary="Test",
            description="Test",
            type=Task.TaskType.TASK,
            priority=Task.Priority.MEDIUM,
        )


@pytest.mark.django_db
def test_task_create_without_sprint():
    project_name = "TestProject"
    project_id = "TTP"

    project = Project.objects.create(project_name=project_name, id=project_id)

    task = create_task_for_test(
        project=project,
        sprint=None,
        summary="Test",
        description="Test",
        type=Task.TaskType.TASK,
        priority=Task.Priority.MEDIUM,
    )

    project.refresh_from_db()
    assert task.id == f'{project_id}-{project.last_task_index}'


@pytest.mark.django_db
def test_task_create_without_parent():
    project_name = "TestProject"
    project_id = "TTP"

    project = Project.objects.create(project_name=project_name, id=project_id)

    task = create_task_for_test(
        project=project,
        parent=None,
        sprint=None,
        summary="Test",
        description="Test",
        type=Task.TaskType.TASK,
        priority=Task.Priority.MEDIUM,
    )

    assert task.id == f'{project_id}-{project.last_task_index}'

@pytest.mark.django_db
def test_task_parent_relation():
    pass
    # TO DO: When parent management methods implemented

@pytest.mark.django_db
def test_task_sprint_relation():
    pass

@pytest.mark.django_db
def test_task_status_change_correct():
    pass

@pytest.mark.django_db
def test_task_status_change_incorrect():
    pass

@pytest.mark.django_db
def test_task_add_parent_correct():
    pass

@pytest.mark.django_db
def test_task_add_parent_incorrect():
    pass

@pytest.mark.django_db
def test_task_add_watcher():
    pass

@pytest.mark.django_db
def test_task_remove_watcher():
    pass

@pytest.mark.django_db
def test_task_check_watcher():
    pass

@pytest.mark.django_db
def test_comment_create_successful():
    pass

@pytest.mark.django_db
def test_comment_create_without_task():
    pass