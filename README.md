# Pykagcee

This library is used to create a knowledge graph from a python project. 
It is based on the `modelscope_agent/environment/graph_database` package from the ModelScope-Agent project,
but ported to be used as a standalone packaged CLI interface.

## Requirements

- Neo4j DBMS (local or remote). We recommend using the [Neo4j Desktop](https://neo4j.com/download/) application due to its better performance.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) tool to manage python virtual environment and dependencies.

## Installation

Clone the repository and set the environment variables in a `.env`:

```bash
cp .env.example .env
```

Set your Neo4j connection details in the `.env` file:

```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

Create environment and install dependencies:

```bash
uv sync
```

## Usage

### Build single knowledge graph

Create a knowledge graph for a single Python project.

```bash
uv run pykagcee build /path/to/single/project
```

### Build multiple knowledge graphs

Create knowledge graphs for multiple Python projects under a directory.

```bash
uv run pykagcee build-all /path/to/multiple/projects
```

### Wipe all graphs
    
Clean all databases.

```bash
uv run pykagcee wipe
```

## Modifications

This project includes modifications made by Perer876:

- 01/07/2025: Extract the `graph_database` package from the `ModelScope-Agent` project and add it to this project.
- 30/08/2025: Several changes to support the CLI interface and multiple graph creation.

## License

This project is licensed under the Apache License 2.0. See the LICENSE file for details.

## Acknowledgments

This project is based on the [ModelScope Agent](https://github.com/modelscope/modelscope-agent) project by Alibaba ModelScope. See the NOTICE file for details.
