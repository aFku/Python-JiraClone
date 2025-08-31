import pytest

@pytest.mark.django_db
def test_task_create_successful():
    pass

@pytest.mark.django_db
def test_task_create_successful_with_null_fields():
    pass
@pytest.mark.django_db
def test_task_create_without_project():
    pass

@pytest.mark.django_db
def test_task_create_without_sprint():
    pass

@pytest.mark.django_db
def test_task_create_without_parent():
    pass

@pytest.mark.django_db
def test_task_parent_relation():
    pass

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