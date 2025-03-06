import json
from typing import Generator, TypedDict


class TaskMetadata(TypedDict):
    task_id: str
    repository: str
    file: str
    context_start_linen: int
    groundtruth_start_lineno: int
    right_context_start_lineno: int


class Task(TypedDict):
    prompt: str
    groundtruth: str
    right_context: str
    metadata: TaskMetadata


def iter_tasks(file_path: str) -> Generator[Task, None, None]:
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            yield json.loads(line)
