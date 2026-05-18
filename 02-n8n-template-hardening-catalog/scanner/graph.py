"""Workflow connection graph utilities for n8n JSON exports."""

from __future__ import annotations

from collections import deque
from typing import Any


class WorkflowGraph:
    """Directed graph of n8n node names from export connections."""

    def __init__(self, nodes: list[dict[str, Any]], connections: dict[str, Any]) -> None:
        self._nodes_by_name = {n.get("name", ""): n for n in nodes if n.get("name")}
        self._adjacency: dict[str, list[str]] = {name: [] for name in self._nodes_by_name}

        for source_name, outputs in connections.items():
            if source_name not in self._adjacency:
                self._adjacency[source_name] = []
            for output_lists in outputs.get("main", []) or []:
                for edge in output_lists or []:
                    target = edge.get("node")
                    if target and target not in self._adjacency[source_name]:
                        self._adjacency[source_name].append(target)

    def get_node(self, name: str) -> dict[str, Any] | None:
        return self._nodes_by_name.get(name)

    def successors_within(self, start: str, max_depth: int = 5) -> list[str]:
        """Return node names reachable from start up to max_depth hops."""
        if start not in self._adjacency:
            return []

        visited: set[str] = set()
        queue: deque[tuple[str, int]] = deque([(start, 0)])
        reachable: list[str] = []

        while queue:
            current, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for nxt in self._adjacency.get(current, []):
                if nxt in visited:
                    continue
                visited.add(nxt)
                reachable.append(nxt)
                queue.append((nxt, depth + 1))

        return reachable

    def has_node_type(self, type_fragment: str) -> bool:
        fragment = type_fragment.lower()
        return any(fragment in (n.get("type") or "").lower() for n in self._nodes_by_name.values())

    def find_nodes_by_type(self, type_fragment: str) -> list[dict[str, Any]]:
        fragment = type_fragment.lower()
        return [
            n
            for n in self._nodes_by_name.values()
            if fragment in (n.get("type") or "").lower()
        ]
