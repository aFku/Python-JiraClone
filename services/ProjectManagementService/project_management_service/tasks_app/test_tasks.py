import pytest

from tasks_app.models import Task, TaskObserver, Comment
from projects_app.models import Project
from sprints_app.models import Sprint
from .services.task_status_workflow import IncorrectTaskTransition, Status
from .services.task_relationship import IncorrectTaskRelationship, TaskType

import uuid
from datetime import timedelta
from django.utils import timezone
from django.db.utils import IntegrityError


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
    type=TaskType.EPIC,
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
    task_type = TaskType.EPIC
    task_priority = Task.Priority.MEDIUM
    task_expected_status = Status.TO_DO

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

    task_bug_type = TaskType.BUG
    task_bug = create_task_for_test(
        project=project,
        sprint=sprint,
        type=task_bug_type,
        parent=task_epic
    )

    assert task_bug.id == f'{project.id}-{project.last_task_index}'
    assert task_bug.parent == task_epic
    assert task_bug.type == task_bug_type


@pytest.mark.django_db
def test_task_create_without_project():
    with pytest.raises(Task.ProjectRequiredException):
        task = Task.create_for_project(
            project=None,
            summary="Test",
            description="Test",
            type=TaskType.TASK,
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
        type=TaskType.TASK,
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
        type=TaskType.TASK,
        priority=Task.Priority.MEDIUM,
    )

    assert task.id == f'{project_id}-{project.last_task_index}'

@pytest.mark.django_db
def test_task_parent_relation():
    task_creator = uuid.uuid4()
    task_summary = "FairTask"
    subtask_summary = "CoolSubtask"

    project_name = "TestProject"
    project_id = "TTP"

    project = Project.objects.create(project_name=project_name, id=project_id)

    subtask = create_task_for_test(
        summary=subtask_summary,
        project=project,
        creator=task_creator,
        type=TaskType.SUBTASK
    )

    task = create_task_for_test(
        summary=task_summary,
        project=project,
        creator=task_creator,
        type=TaskType.TASK
    )

    subtask.add_parent(task)

    assert subtask.parent.id == task.id
    assert task.children.all()[0].id == subtask.id

@pytest.mark.django_db
def test_task_sprint_relation():
    task_creator = uuid.uuid4()
    task_type = TaskType.BUG

    project_name = "TestProject"
    project_id = "TTP"
    sprint_name = "TestSprintName"

    project = Project.objects.create(project_name=project_name, id=project_id)
    sprint = Sprint.objects.create(name=sprint_name, project=project)

    task = create_task_for_test(
        project=project,
        sprint=sprint,
        creator=task_creator,
        type=task_type
    )

    assert len(sprint.tasks.all()) == 1
    assert sprint.tasks.all()[0] == task

    assert len(task.sprint.all()) == 1
    assert task.sprint.all()[0] == sprint


@pytest.mark.django_db
def test_task_status_change_correct():
    task_creator = uuid.uuid4()
    task_type = TaskType.BUG

    project_name = "TestProject"
    project_id = "TTP"

    project = Project.objects.create(project_name=project_name, id=project_id)

    task = create_task_for_test(
        project=project,
        creator=task_creator,
        type=task_type
    )

    assert task.status == Status.TO_DO
    task.change_status(Status.IN_PROGRESS)
    assert task.status == Status.IN_PROGRESS


@pytest.mark.django_db
def test_task_status_change_incorrect():
    task_creator = uuid.uuid4()
    task_type = TaskType.BUG

    project_name = "TestProject"
    project_id = "TTP"

    project = Project.objects.create(project_name=project_name, id=project_id)

    task = create_task_for_test(
        project=project,
        creator=task_creator,
        type=task_type
    )

    assert task.status == Status.TO_DO

    with pytest.raises(IncorrectTaskTransition):
        task.change_status(Status.IN_REVIEW)

@pytest.mark.django_db
def test_task_add_parent_correct():
    task_creator = uuid.uuid4()
    epic_summary = "SuperDuperEpic"
    task_summary = "AmazingTask"

    project_name = "TestProject"
    project_id = "TTP"

    project = Project.objects.create(project_name=project_name, id=project_id)

    epic = create_task_for_test(
        summary=epic_summary,
        project=project,
        creator=task_creator,
        type=TaskType.EPIC
    )

    task = create_task_for_test(
        summary=task_summary,
        project=project,
        creator=task_creator,
        type=TaskType.TASK
    )

    task.add_parent(epic)

    assert task.parent.id == epic.id
    assert len(epic.children.all()) == 1



@pytest.mark.django_db
def test_task_add_parent_incorrect():
    task_creator = uuid.uuid4()
    initiative_summary = "ElegantInitiative"
    subtask_summary = "CoolSubtask"

    project_name = "TestProject"
    project_id = "TTP"

    project = Project.objects.create(project_name=project_name, id=project_id)

    initiative = create_task_for_test(
        summary=initiative_summary,
        project=project,
        creator=task_creator,
        type=TaskType.INITIATIVE
    )

    subtask = create_task_for_test(
        summary=subtask_summary,
        project=project,
        creator=task_creator,
        type=TaskType.SUBTASK
    )

    with pytest.raises(IncorrectTaskRelationship):
        subtask.add_parent(initiative)

@pytest.mark.django_db
def test_task_add_watcher():
    task_creator = uuid.uuid4()
    task_type = TaskType.BUG
    task_observer = uuid.uuid4()

    project_name = "TestProject"
    project_id = "TTP"

    project = Project.objects.create(project_name=project_name, id=project_id)

    task = create_task_for_test(
        project=project,
        creator=task_creator,
        type=task_type
    )

    assert len(TaskObserver.objects.filter(user_id=task_observer)) == 0
    assert len(task.observers.all()) == 0

    task.add_observer(task_observer)

    assert len(TaskObserver.objects.filter(user_id=task_observer)) == 1
    assert len(task.observers.all()) == 1

@pytest.mark.django_db
def test_task_remove_watcher():
    task_creator = uuid.uuid4()
    task_type = TaskType.BUG
    task_observer = uuid.uuid4()

    project_name = "TestProject"
    project_id = "TTP"

    project = Project.objects.create(project_name=project_name, id=project_id)

    task = create_task_for_test(
        project=project,
        creator=task_creator,
        type=task_type
    )

    task.add_observer(task_observer)

    assert len(TaskObserver.objects.filter(user_id=task_observer)) == 1
    assert len(task.observers.all()) == 1

    task.remove_observer(task_observer)

    assert len(TaskObserver.objects.filter(user_id=task_observer)) == 0
    assert len(task.observers.all()) == 0

@pytest.mark.django_db
def test_task_check_watcher():
    task_creator = uuid.uuid4()
    task_type = TaskType.BUG
    task_observer = uuid.uuid4()

    project_name = "TestProject"
    project_id = "TTP"

    project = Project.objects.create(project_name=project_name, id=project_id)

    task = create_task_for_test(
        project=project,
        creator=task_creator,
        type=task_type
    )

    assert len(TaskObserver.objects.filter(user_id=task_observer)) == 0
    assert len(task.observers.all()) == 0

    task.add_observer(task_observer)

    assert task.is_watched_by(task_observer)

@pytest.mark.django_db
def test_comment_create_successful():
    task_creator = uuid.uuid4()
    task_type = TaskType.BUG
    comment_author = uuid.uuid4()
    comment_content = "BestContentEver"

    project_name = "TestProject"
    project_id = "TTP"

    project = Project.objects.create(project_name=project_name, id=project_id)

    task = create_task_for_test(
        project=project,
        creator=task_creator,
        type=task_type
    )

    comment = Comment.objects.create(
        task=task,
        author=comment_author,
        content=comment_content
    )

    comment.save()

    assert comment.id == 1
    assert comment.task.id == task.id
    assert comment.author == comment_author
    assert comment.content == comment_content
    assert comment.creation_date - timezone.now() < timedelta(seconds=5)
    assert comment.last_edit_time - timezone.now() < timedelta(seconds=5)
    assert task.comments.all()[0].id == comment.id



@pytest.mark.django_db
def test_comment_create_without_task():
    comment_author = uuid.uuid4()
    comment_content = "WorstCommentEver"

    with pytest.raises(IntegrityError):
        Comment.objects.create(
            author=comment_author,
            content=comment_content
        )
