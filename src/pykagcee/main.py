from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional
from py2neo import SystemGraph, Graph
from graph_database import GraphDatabaseHandler
from graph_database.build import build_graph_database
import typer
from rich import console
import sys
import os
from graph_database import indexer
from pykagcee.system import RepositoryGraphDatabase, SystemGraphDatabase
from .config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

app = typer.Typer()

console = console.Console()

# Define the environment path dictionary
env_path_dict = {
    "env_path": sys.executable,
    "working_directory": os.path.dirname(indexer.__file__),
    "url": NEO4J_URI,
    "user": NEO4J_USERNAME,
    "password": NEO4J_PASSWORD,
    "db_name": "",
}

system_graph = SystemGraph(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

system_graph_database = SystemGraphDatabase(system_graph)

system_graph_database.create_database("metadata", if_not_exists=True)
metadata_graph = Graph(
    NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD), name="metadata"
)

repository_graph = RepositoryGraphDatabase(
    system=system_graph_database, metadata_graph=metadata_graph
)


@app.command()
def build(
    project_path: Path, repository_id: Optional[str] = None, force: bool = False
) -> None:
    """
    Build the graph database for the given project path.
    """
    project_path = project_path.resolve()

    if not repository_id:
        repository_id = project_path.name

    if repository_graph.exists(repository_id):
        if not force:
            console.print(
                f"Database for repository '{repository_id}' already exists. Use --force to rebuild."
            )
            return

        repository_graph.delete_or_raise(repository_id)

    database_name = repository_graph.create(repository_id, project_path)

    env_path = {**env_path_dict, "db_name": database_name}

    graph_handler = GraphDatabaseHandler(
        uri=env_path["url"],
        user=env_path["user"],
        password=env_path["password"],
        database_name=env_path["db_name"],
        use_lock=True,
        lockfile=f"locks/{repository_id}.lock",
    )

    build_graph_database(
        graph_db=graph_handler,
        repo_path=str(project_path),
        task_id=database_name,
        is_clear=False,
        max_workers=4,
        env_path_dict=env_path,
    )


@app.command()
def build_all(
    projects_path: Path, force: bool = False, max_workers: Optional[int] = 6
) -> None:
    """
    Build the graph database for all projects in the given path.
    """
    repositories = [
        repository.resolve()
        for repository in projects_path.iterdir()
        if repository.is_dir()
    ]

    total_tasks = len(repositories)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks and collect Future objects
        futures = [
            executor.submit(build, repository, force=force)
            for repository in repositories
        ]

        # Initialize a counter for completed tasks
        completed_tasks = 0

        # Track completion of tasks as they finish
        for _ in as_completed(futures):
            completed_tasks += 1
            console.print(f"Tasks completed: {completed_tasks}/{total_tasks}")

    console.print("Done.")


@app.command()
def wipe() -> None:
    repository_graph.delete_all_repositories()

    console.print("All databases were wiped.")
