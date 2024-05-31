from controllers.task_controller import TaskController
from fastapi import APIRouter, Depends
from utils import HTTPResponse, verify_token, has_role
from models.task import Task, TaskUpdate
import constants as api_c
from typing import List

router = APIRouter(tags=[api_c.TASK])


@router.get("/api/tasks")
@has_role([api_c.ADMIN, api_c.VIEWER, api_c.EDITOR])
async def get_tasks(by_user: str | None = None, sort_by: api_c.TaskFilterField = api_c.UPDATED_AT, sort_order: str = "desc", role: str = Depends(verify_token)):
    tasks = TaskController.get_all_tasks(by_user=by_user, sort_by=sort_by, sort_order=sort_order)
    if tasks:
        return HTTPResponse(content=tasks)
    return HTTPResponse(content="No tasks created", status_code=200)


@router.get("/api/tasks/{task_id}")
@has_role([api_c.ADMIN, api_c.VIEWER, api_c.EDITOR])
async def get_task(
    task_id, role: str = Depends(verify_token)
):

    task = TaskController.get_task_by_id(task_id)
    if task:
        return HTTPResponse(content=task)
    else:
        return HTTPResponse({"message": "Task not found"}, 404)


@router.post("/api/tasks/")
@has_role([api_c.ADMIN, api_c.EDITOR])
async def add_task(
    tasks_data: List[Task], role: str = Depends(verify_token)
):
    created_tasks = TaskController.add_tasks(tasks_data)
    return HTTPResponse(created_tasks, 201)


@router.patch("/api/tasks/{task_id}")
@has_role([api_c.ADMIN, api_c.EDITOR])
async def update_task(
    product_id: str,
    updated_task_data: TaskUpdate,
    role: str = Depends(verify_token),
):
    try:
        product = TaskController.update_task(product_id, updated_task_data)
        return HTTPResponse(product, 200)
    except ValueError as e:
        return HTTPResponse({"message": e}, 404)


@router.delete("/api/tasks/{task_id}")
@has_role(["Admin"])
async def delete_product(task_id: str, role: str = Depends(verify_token)):
    deleted_status = TaskController.delete_product(task_id)
    if deleted_status:
        return HTTPResponse(status_code=204)
    else:
        return HTTPResponse({"message": "Task not found"}, 404)