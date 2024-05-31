# Constants file
from enum import Enum

ADMIN = "admin"
VIEWER = "viewer"
EDITOR = "editor"


TASK = "task"

ALL_STATUS = "All"
TO_DO_STATUS = "To Do"
IN_PROGRESS_STATUS = "In Progress"
DONE_STATUS = "Done"
ALLOWED_TASK_STATUS_LIST = [TO_DO_STATUS, IN_PROGRESS_STATUS, DONE_STATUS]

ID = "_id"
TITLE = "title"
DESCRIPTION = "description"
STATUS = "status"
CREATED_AT = "created_at"
CREATED_BY = "created_by"
UPDATED_AT = "updated_at"
UPDATED_BY = "updated_by"


class TaskFilterField(str, Enum):
    title = TITLE
    description = DESCRIPTION
    status = STATUS
    created_at = CREATED_AT
    created_by = CREATED_BY
    updated_at = UPDATED_AT
    updated_by = UPDATED_BY
