from models.task import Task, TaskUpdate
from utils import document_to_model, mongo_client
from bson import ObjectId
import constants as api_c
from typing import List


class TaskController:
    @staticmethod
    def get_all_tasks(by_user: str | None = None, by_status: str = api_c.ALL_STATUS, sort_by: str = api_c.UPDATED_AT, sort_order: str = "desc") -> list[Task]:
        query = {}
        if by_user:
            query[api_c.CREATED_BY] = by_user
        if by_status != api_c.ALL_STATUS:
            if by_status not in api_c.ALLOWED_TASK_STATUS_LIST:
                raise Exception("Invalid status requested")
            query[api_c.STATUS] = by_status
        sort_query = {sort_by: -1 if sort_order == "desc" else 1}
        tasks = list(mongo_client.db.tasks.find(query).sort(sort_query))
        return [document_to_model(Task, task) for task in tasks]

    @staticmethod
    def get_task_by_id(task_id: str) -> Task | None:
        task = mongo_client.db.tasks.find_one({api_c.ID: ObjectId(task_id)})
        if task:
            return document_to_model(Task, task)
        else:
            return None

    @staticmethod
    def add_tasks(tasks: List[Task]) -> List[Task]:
        tasks_dicts = [task.dict() for task in tasks]
        inserted_tasks = mongo_client.db.tasks.insert_many(tasks_dicts)
        for task_dict, inserted_id in zip(tasks_dicts, inserted_tasks.inserted_ids):
            task_dict["id"] = str(inserted_id)
        return [Task(**task_dict) for task_dict in tasks_dicts]

    @staticmethod
    def update_task(
        task_id: str, updated_task_data: TaskUpdate
    ) -> Task | None:
        try:
            ObjectId(task_id)
        except Exception as e:
            raise ValueError("Invalid task_id")

        task = mongo_client.db.tasks.find_one({api_c.ID: ObjectId(task_id)})

        if not task:
            raise ValueError("Task not found")
        new_task_data = {
            key: value for key, value in updated_task_data.dict().items() if value
        }
        task.update(new_task_data)

        updated_task = mongo_client.db.tasks.update_one(
            {api_c.ID: ObjectId(task_id)}, {"$set": task}
        )

        if updated_task.matched_count > 0:
            return document_to_model(Task, task)

    @staticmethod
    def delete_task(task_id: str) -> bool:
        result = mongo_client.db.tasks.delete_one({api_c.ID: ObjectId(task_id)})
        return result.deleted_count > 0