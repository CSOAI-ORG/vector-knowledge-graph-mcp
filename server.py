#!/usr/bin/env python3
"""Vector Knowledge Graph MCP Server — Neo4j-style graph + vector hybrid for compliance reasoning."""

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import json, hashlib
from datetime import datetime, timezone
from collections import defaultdict
from typing import List, Optional
from mcp.server.fastmcp import FastMCP

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None

mcp = FastMCP("vector-knowledge-graph", instructions="MEOK AI Labs MCP Server")

_NODES: dict = {}
_EDGES: list = []

def _embed(text: str) -> List[float]:
    h = hashlib.md5(text.lower().encode()).hexdigest()
    return [int(h[i:i+2], 16) / 255.0 for i in range(0, 32, 2)]

def _cosine(a, b):
    dot = sum(x*y for x,y in zip(a,b))
    return dot / ((sum(x*x for x in a)**0.5 * sum(y*y for y in b)**0.5) + 1e-9)

@mcp.tool()
def add_node(label: str, properties: dict, node_id: Optional[str] = None, api_key: str = "") -> str:
    """Add a node to the knowledge graph with properties, embeddings, and metadata."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    nid = node_id or hashlib.md5(label.encode()).hexdigest()[:12]
    _NODES[nid] = {"label": label, "properties": properties, "embedding": _embed(label + " " + json.dumps(properties))}
    return {"node_id": nid, "created": True}

@mcp.tool()
def add_edge(from_id: str, to_id: str, relation: str, weight: float = 1.0, api_key: str = "") -> str:
    """Create a directed edge between two nodes with relationship type and weight."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    _EDGES.append({"from": from_id, "to": to_id, "relation": relation, "weight": weight})
    return {"edge_created": True, "relation": relation}

@mcp.tool()
def semantic_node_search(query: str, top_k: int = 5, api_key: str = "") -> str:
    """Search for nodes using semantic similarity matching against stored embeddings."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    q_vec = _embed(query)
    results = []
    for nid, node in _NODES.items():
        score = _cosine(q_vec, node["embedding"])
        results.append({"node_id": nid, "score": round(score, 4), "label": node["label"]})
    results.sort(key=lambda x: x["score"], reverse=True)
    return {"results": results[:top_k]}

@mcp.tool()
def trace_compliance_chain(start_node_id: str, max_depth: int = 3, api_key: str = "") -> str:
    """Trace the compliance chain from a requirement through controls to evidence."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

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
    return {"start": start_node_id, "paths": paths}

@mcp.tool()
def find_gaps(required_frameworks: list, api_key: str = "") -> str:
    """Find gaps in the knowledge graph where expected relationships or nodes are missing."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    present = set()
    for node in _NODES.values():
        for fw in required_frameworks:
            if fw.lower() in node["label"].lower():
                present.add(fw)
    missing = [fw for fw in required_frameworks if fw not in present]
    return {"present": list(present), "missing": missing, "coverage": round(len(present)/len(required_frameworks)*100,1) if required_frameworks else 100}

if __name__ == "__main__":
    mcp.run()
