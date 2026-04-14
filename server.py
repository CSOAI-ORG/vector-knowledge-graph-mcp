#!/usr/bin/env python3
"""Vector Knowledge Graph MCP Server — Neo4j-style graph + vector hybrid for compliance reasoning."""
import json, hashlib
from typing import List, Optional
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("vector-knowledge-graph-mcp")

_NODES: dict = {}
_EDGES: list = []

def _embed(text: str) -> List[float]:
    h = hashlib.md5(text.lower().encode()).hexdigest()
    return [int(h[i:i+2], 16) / 255.0 for i in range(0, 32, 2)]

def _cosine(a, b):
    dot = sum(x*y for x,y in zip(a,b))
    return dot / ((sum(x*x for x in a)**0.5 * sum(y*y for y in b)**0.5) + 1e-9)

@mcp.tool(name="add_node")
async def add_node(label: str, properties: dict, node_id: Optional[str] = None) -> str:
    nid = node_id or hashlib.md5(label.encode()).hexdigest()[:12]
    _NODES[nid] = {"label": label, "properties": properties, "embedding": _embed(label + " " + json.dumps(properties))}
    return json.dumps({"node_id": nid, "created": True})

@mcp.tool(name="add_edge")
async def add_edge(from_id: str, to_id: str, relation: str, weight: float = 1.0) -> str:
    _EDGES.append({"from": from_id, "to": to_id, "relation": relation, "weight": weight})
    return json.dumps({"edge_created": True, "relation": relation})

@mcp.tool(name="semantic_node_search")
async def semantic_node_search(query: str, top_k: int = 5) -> str:
    q_vec = _embed(query)
    results = []
    for nid, node in _NODES.items():
        score = _cosine(q_vec, node["embedding"])
        results.append({"node_id": nid, "score": round(score, 4), "label": node["label"]})
    results.sort(key=lambda x: x["score"], reverse=True)
    return json.dumps({"results": results[:top_k]})

@mcp.tool(name="trace_compliance_chain")
async def trace_compliance_chain(start_node_id: str, max_depth: int = 3) -> str:
    visited = set()
    paths = []
    def dfs(node, depth, path):
        if depth > max_depth or node in visited:
            return
        visited.add(node)
        for e in _EDGES:
            if e["from"] == node:
                dfs(e["to"], depth + 1, path + [{"relation": e["relation"], "to": e["to"], "weight": e["weight"]}])
        if path:
            paths.append({"from": start_node_id, "path": path})
    dfs(start_node_id, 0, [])
    return json.dumps({"start": start_node_id, "paths": paths})

@mcp.tool(name="find_gaps")
async def find_gaps(required_frameworks: list) -> str:
    present = set()
    for node in _NODES.values():
        for fw in required_frameworks:
            if fw.lower() in node["label"].lower():
                present.add(fw)
    missing = [fw for fw in required_frameworks if fw not in present]
    return json.dumps({"present": list(present), "missing": missing, "coverage": round(len(present)/len(required_frameworks)*100,1) if required_frameworks else 100})

if __name__ == "__main__":
    mcp.run()
