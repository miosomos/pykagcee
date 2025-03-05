import time
from concurrent.futures import ThreadPoolExecutor
from graph_database import GraphDatabaseHandler
from graph_database.build import build_graph_database
import typer
import sys
import os
from graph_database import indexer
from pykagcee import cceval
from .config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from pykagcee.checkpoint import Checkpoint

app = typer.Typer()

# Define the environment path dictionary
env_path_dict = {
    "env_path": sys.executable,
    "working_directory": os.path.dirname(indexer.__file__),
    "url": NEO4J_URI,
    "user": NEO4J_USERNAME,
    "password": NEO4J_PASSWORD,
    "db_name": "",
}

# Initialize the Graph Database Handler
graph_db = GraphDatabaseHandler(
    uri=env_path_dict["url"],
    user=env_path_dict["user"],
    password=env_path_dict["password"],
    database_name=env_path_dict["db_name"],
    use_lock=True,
)

checkpoint = Checkpoint(graph_db.graph)

@app.command()
def mark_as_completed(task_id: str) -> None:
    """
    Mark a task as completed.
    """
    checkpoint.mark_as_completed(task_id)

@app.command()
def build(project_path: str, task_id: str) -> None:
    """
    Build the graph database for the given project path.
    """
    if task_id in checkpoint:
        print(f"Task {task_id} already completed.")
        return

    build_graph_database(
        graph_db=graph_db,
        repo_path=project_path,
        task_id=task_id,
        is_clear=True,
        max_workers=8,
        env_path_dict=env_path_dict,
    )

    checkpoint.mark_as_completed(task_id)

@app.command()
def build_fake(project_path: str, task_id: str) -> None:
    """
    Build the graph database for the given project path.
    """
    if task_id in checkpoint:
        print(f"Task {task_id} already completed.")
        return

    time.sleep(1)

    checkpoint.mark_as_completed(task_id)

@app.command()
def init_cceval(tasks_file_path: str, raw_data_directory: str) -> None:
    """
    Initialize the CCEval data needed to build the graph.
    """
    repositories = { task["metadata"]["repository"] for task in cceval.iter_tasks(tasks_file_path) }

    projects = [ os.path.join(raw_data_directory, repository) for repository in repositories ]

    with ThreadPoolExecutor(max_workers=16) as executor:
        executor.map(build_fake, projects, repositories)

    print("Done.")

@app.command()
def wipe() -> None:
    print("Wiping the database...")
    graph_db.clear_database()
    # Delete indexes
    result = graph_db.execute_query("SHOW INDEXES")
    for record in result:
        index_name = record["name"]
        graph_db.execute_query(f"DROP INDEX {index_name}")

    print("Database wiped.")

@app.command()
def play() -> None:
    print(os.path.join("src", "pykagcee", "main.py"))
