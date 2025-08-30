import pytest

from projects_app.models import Project

@pytest.mark.django_db
def test_project_creation():
    name = "TestProject"
    id = "TTP"
    index = 0

    obj = Project.objects.create(project_name=name, id=id)

    assert obj.project_name == name
    assert obj.id == id
    assert obj.last_task_index == index


