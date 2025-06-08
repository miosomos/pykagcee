from concurrent.futures import ThreadPoolExecutor, as_completed
from graph_database import GraphDatabaseHandler
from graph_database.build import build_graph_database
import typer
from rich import console
import sys
import os
from graph_database import indexer
from pykagcee import cceval
from .config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from pykagcee.checkpoint import Checkpoint

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

@app.command()
def mark_as_completed(repository_id: str) -> None:
    """
    Mark a task as completed.
    """
    # Initialize the Graph Database Handler
    graph_db = GraphDatabaseHandler(
        uri=env_path_dict["url"],
        user=env_path_dict["user"],
        password=env_path_dict["password"],
        database_name=env_path_dict["db_name"],
        use_lock=True,
        lockfile=repository_id + "_neo4j.lock",
    )

    checkpoint = Checkpoint(graph_db.graph)

    checkpoint.mark_as_completed(repository_id)


@app.command()
def build(project_path: str, repository_id: str) -> None:
    """
    Build the graph database for the given project path.
    """

    # Initialize the Graph Database Handler
    graph_db = GraphDatabaseHandler(
        uri=env_path_dict["url"],
        user=env_path_dict["user"],
        password=env_path_dict["password"],
        database_name=env_path_dict["db_name"],
        use_lock=True,
        lockfile=f"locks/{repository_id}_neo4j.lock",
    )

    checkpoint = Checkpoint(graph_db.graph)

    if repository_id in checkpoint:
        console.print(f"Task '{repository_id}' already completed.")
        return

    build_graph_database(
        graph_db=graph_db,
        repo_path=project_path,
        task_id=repository_id,
        is_clear=False,
        max_workers=4,
        env_path_dict=env_path_dict,
    )

    checkpoint.mark_as_completed(repository_id)


@app.command()
def init_cceval(tasks_file_path: str, raw_data_directory: str) -> None:
    """
    Initialize the CCEval data needed to build the graph.
    """
    repositories = {
        task["metadata"]["repository"] for task in cceval.iter_tasks(tasks_file_path)
    }

    projects = [
        os.path.join(raw_data_directory, repository) for repository in repositories
    ]

    total_tasks = len(projects)

    with ThreadPoolExecutor(max_workers=6) as executor:
        # Submit all tasks and collect Future objects
        futures = [
            executor.submit(build, project, repository)
            for project, repository in zip(projects, repositories)
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
    # Initialize the Graph Database Handler
    graph_db = GraphDatabaseHandler(
        uri=env_path_dict["url"],
        user=env_path_dict["user"],
        password=env_path_dict["password"],
        database_name=env_path_dict["db_name"],
    )

    console.print("Wiping the database...")
    graph_db.clear_database()
    # Delete indexes
    result = graph_db.execute_query("SHOW INDEXES")
    for record in result:
        index_name = record["name"]
        graph_db.execute_query(f"DROP INDEX {index_name}")

    console.print("Database wiped.")
