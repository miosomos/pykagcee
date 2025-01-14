### Pykagcee

This library is used to create a knowledge graph from a python project. It is based on the `modelscope_agent/environment/graph_database` package from the ModelScope-Agent project.

## Usage

You should have the [uv](https://docs.astral.sh/uv/getting-started/installation/) tool installed on your system. 

Once cloned and inside the repository, you should set the enviroment variables in a `.env`:

```bash
cp .env.example .env
``````

You can run the following command to generate the knowledge graph:

```bash
uv run pykagcee build /path/to/python/project
```

Or to wipe the graph database:
    
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
