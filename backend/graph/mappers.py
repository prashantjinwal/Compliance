from __future__ import annotations


def to_neo4j_merge_statement(payload: dict) -> str:
    """Return a Cypher hint for future Neo4j integration."""
    node_type = payload["type"]
    node_id = payload["id"]
    return f"MERGE (n:{node_type} {{id: {node_id!r}}}) SET n += $properties"

