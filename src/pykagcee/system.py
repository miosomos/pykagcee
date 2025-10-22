from pathlib import Path
from typing import final, Optional
from py2neo import Graph, SystemGraph
import re


def sanitize_folder_name(folder_name: str) -> str:
    # Neo4j automatically lowercases database names, so this avoids case issues.
    # Keep only lowercase letters, numbers, dots, and dashes; replace others with dashes.
    sanitized = re.sub(r"[^a-z0-9.-]+", "-", folder_name.lower())

    # Remove leading/trailing dots or dashes
    sanitized = sanitized.strip(".-")

    # Ensure the name is not empty
    if not sanitized:
        raise ValueError(
            f"Sanitized database name is empty. Please provide a valid database name. Original name: '{folder_name}'"
        )

    # Ensure the name does not exceed 63 characters
    return f"repo-{sanitized[:58]}"


@final
class SystemGraphDatabase:
    __slots__ = ("system_graph",)

    def __init__(self, system_graph: SystemGraph):
        self.system_graph = system_graph

    def create_database(self, name: str, if_not_exists: bool = False) -> bool:
        try:
            self.system_graph.run(
                f"CREATE DATABASE `{name}`{' IF NOT EXISTS' if if_not_exists else ''}"
            )
        except Exception as e:
            raise CreateDatabaseSystemGraphError(
                f"Error creating database `{name}`"
            ) from e

    def drop_database(self, name: str, if_exists: bool = False):
        try:
            self.system_graph.run(
                f"DROP DATABASE `{name}`{' IF EXISTS' if if_exists else ''}"
            )
        except Exception as e:
            raise DropDatabaseSystemGraphError(
                f"Error dropping database `{name}`"
            ) from e

    def show_databases(self) -> set[str]:
        try:
            result = self.system_graph.run("SHOW DATABASES").data()
            return {record["name"] for record in result}
        except Exception as e:
            raise SystemGraphError("Error showing databases") from e


class SystemGraphError(Exception):
    pass


class CreateDatabaseSystemGraphError(SystemGraphError):
    pass


class DropDatabaseSystemGraphError(SystemGraphError):
    pass


@final
class RepositoryGraphDatabase:
    __slots__ = "system", "metadata_graph", "node_label"

    def __init__(
        self,
        system: SystemGraphDatabase,
        metadata_graph: Graph,
        node_label: str = "Repository",
    ):
        self.system = system
        self.metadata_graph = metadata_graph
        self.node_label = node_label

    def create(
        self,
        repository_id: str,
        project_path: Path,
        database_name: str = None,
    ) -> str:
        database_name = database_name or sanitize_folder_name(repository_id)

        self.system.create_database(database_name, if_not_exists=True)

        self.metadata_graph.run(
            f"CREATE (r:{self.node_label} {{repository_id: $repository_id, project_path: $project_path, database_name: $database_name}})",
            repository_id=repository_id,
            database_name=database_name,
            project_path=str(project_path),
        )

        return database_name

    def resolve_database_name(self, repository_id: str) -> Optional[str]:
        query = f"""
        MATCH (r:{self.node_label} {{repository_id: $repository_id}})
        RETURN r.database_name AS database_name
        LIMIT 1
        """
        result = self.metadata_graph.run(query, repository_id=repository_id).data()

        if not result:
            return None

        return result[0]["database_name"]

    def exists(self, repository_id: str) -> bool:
        return self.resolve_database_name(repository_id) is not None

    def delete_or_raise(self, repository_id: str) -> None:
        database_name = self.resolve_database_name(repository_id)

        if not database_name:
            raise ValueError(f"Repository with ID '{repository_id}' does not exist.")

        self.system.drop_database(database_name, if_exists=True)

        self.metadata_graph.run(
            f"MATCH (r:{self.node_label} {{repository_id: $repository_id}}) DETACH DELETE r",
            repository_id=repository_id,
        )

    def list_repositories(self) -> set[str]:
        query = f"""
        MATCH (r:{self.node_label})
        RETURN r.repository_id AS repository_id
        """
        result = self.metadata_graph.run(query).data()

        return {record["repository_id"] for record in result}

    def delete_all_repositories(self) -> None:
        repositories = self.list_repositories()

        for repository_id in repositories:
            print(f"Deleting repository '{repository_id}'...")
            self.delete_or_raise(repository_id)
