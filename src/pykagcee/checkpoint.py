from typing import final
from py2neo import Graph


@final
class Checkpoint:
    __slots__ = ["_graph", "_node_label"]

    def __init__(self, graph: Graph, node_label: str = "__COMPLETED_TASK__"):
        self._graph = graph
        self._node_label = node_label

    def mark_as_completed(self, task_id: str):
        query = f"""
        MERGE (t:{self._node_label} {{taskId: $id}})
        """
        self._graph.run(query, id=task_id)

    def get_completed_tasks(self, task_ids: set[str]) -> set[str]:
        query = f"""
        MATCH (t:{self._node_label}) WHERE t.taskId IN $ids RETURN t.taskId
        """

        result = self._graph.run(query, ids=list(task_ids))

        return {record["t.taskId"] for record in result}

    def get_all_completed_tasks(self) -> set[str]:
        query = f"""
        MATCH (t:{self._node_label}) RETURN t.taskId
        """

        result = self._graph.run(query)

        return {record["t.taskId"] for record in result}

    def __contains__(self, task_id: str) -> bool:
        query = f"""
        MATCH (t:{self._node_label}) WHERE t.taskId = $id RETURN t.taskId LIMIT 1
        """

        result = self._graph.run(query, id=task_id)

        return result.evaluate() is not None
