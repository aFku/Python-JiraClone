class ProjectRelated:
    """
    Mixin for forcing get_project() implementation
    """

    def get_project(self):
        raise NotImplementedError