# Pykagcee

This library is used to create a knowledge graph from a python project. 
It is based on the `modelscope_agent/environment/graph_database` package from the ModelScope-Agent project,
but ported to be used as a standalone packagend CLI interface.

## Installation

You should have the [uv](https://docs.astral.sh/uv/getting-started/installation/) tool installed on your system. 

Once cloned and inside the repository, you should set the enviroment variables in a `.env`:

```bash
cp .env.example .env
``````

And that's all, [uv](https://docs.astral.sh/uv/getting-started/installation/) will create a virtual environment and install the dependencies for you the
first time you run the project.

## Usage

### Build single knowledge graph

Create a knowledge graph for a single Python project.

```bash
uv run pykagcee build /path/to/python/project
```

### Build multiple knowledge graphs

Create knowledge graphs for multiple Python projects.

```bash
uv run pykagcee build-all /path/to/python/projects
```

### Wipe all graphs
    
```bash
uv run pykagcee wipe
```

## Modifications

This project includes modifications made by Perer876:

- 01/07/2025: Extract the `graph_database` package from the `ModelScope-Agent` project and add it to this project.

## License

This project is licensed under the Apache License 2.0. See the LICENSE file for details.

## Acknowledgments

This project is based on the [ModelScope Agent](https://github.com/modelscope/modelscope-agent) project by Alibaba ModelScope. See the NOTICE file for details.
