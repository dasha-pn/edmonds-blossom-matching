# Maximum Matching with Forbidden Vertices

This project implements the **maximum matching problem** in an undirected graph with **forbidden vertices**.

The algorithm is implemented in **C++ using Edmonds' Blossom Algorithm**, and the results are compared with a **Python implementation using NetworkX**.

The repository also contains a **benchmark script** that compares the runtime of both implementations.

---

# Problem Statement

Given an undirected graph

$$
G = (V, E)
$$

and a subset of forbidden vertices

$$
B \subseteq V
$$

the task is to find a **maximum matching** such that:

- no two edges share a common vertex
- no edge is incident to any vertex from $B$

Formally:

$$
\forall (u,v) \in M: \quad u \notin B, \; v \notin B
$$

where $M$ is the matching.

---

# Algorithms Used

## Edmonds' Blossom Algorithm

The C++ implementation uses **Edmonds' Blossom Algorithm**, which finds a maximum matching in a general undirected graph.

Key idea:

- build **alternating trees**
- search for **augmenting paths**
- detect **odd cycles (blossoms)**
- contract them and continue the search

Time complexity:

$$
O(V^3)
$$

where:

- $V$ — number of vertices.

The implementation maintains structures such as:

- `match[v]` — partner of vertex $v$
- `parent[v]` — parent in BFS tree
- `base[v]` — base vertex of blossom
- `used[v]` — visited flag
- `blossom[v]` — blossom marker :contentReference[oaicite:1]{index=1}.

---

# Handling Forbidden Vertices

Forbidden vertices are processed **during graph construction**.

```
if (forbidden[u] || forbidden[v]) {
continue;
}
```


If an edge is incident to a forbidden vertex, it is **not added to the graph**:
