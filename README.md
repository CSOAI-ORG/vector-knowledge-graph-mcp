# Vector Knowledge Graph

> By [MEOK AI Labs](https://meok.ai) — MEOK AI Labs MCP Server

Vector Knowledge Graph MCP Server — Neo4j-style graph + vector hybrid for compliance reasoning.

## Installation

```bash
pip install vector-knowledge-graph-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install vector-knowledge-graph-mcp
```

## Tools

### `add_node`
Add a node to the knowledge graph with properties, embeddings, and metadata.

**Parameters:**
- `label` (str)
- `properties` (str)
- `node_id` (str)

### `add_edge`
Create a directed edge between two nodes with relationship type and weight.

**Parameters:**
- `from_id` (str)
- `to_id` (str)
- `relation` (str)
- `weight` (float)

### `semantic_node_search`
Search for nodes using semantic similarity matching against stored embeddings.

**Parameters:**
- `query` (str)
- `top_k` (int)

### `trace_compliance_chain`
Trace the compliance chain from a requirement through controls to evidence.

**Parameters:**
- `start_node_id` (str)
- `max_depth` (int)

### `find_gaps`
Find gaps in the knowledge graph where expected relationships or nodes are missing.

**Parameters:**
- `required_frameworks` (str)


## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## Links

- **Website**: [meok.ai](https://meok.ai)
- **GitHub**: [CSOAI-ORG/vector-knowledge-graph-mcp](https://github.com/CSOAI-ORG/vector-knowledge-graph-mcp)
- **PyPI**: [pypi.org/project/vector-knowledge-graph-mcp](https://pypi.org/project/vector-knowledge-graph-mcp/)

## License

MIT — MEOK AI Labs
