from graph_database import GraphDatabaseHandler
from graph_database.build import build_graph_database
import typer
import sys
import os
from graph_database import indexer
from .config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

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


@app.command()
def build(project_path: str) -> None:
    # Build the graph database
    build_graph_database(
        graph_db=graph_db,
        repo_path=project_path,
        task_id="pykagcee",
        is_clear=True,
        max_workers=8,
        env_path_dict=env_path_dict,
    )

@app.command()
def wipe() -> None:
    print("Wiping the database...")
    graph_db.clear_database()
    print("Database wiped.")