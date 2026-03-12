import subprocess
import time
import random
import csv
import pathlib
from typing import List, Tuple, Set

import networkx as nx
import matplotlib.pyplot as plt

EXECUTABLE = "./max_matching_forbidden.exe"

def generate_random_instance(
    n: int,
    edge_prob: float = 0.2,
    forbidden_ratio: float = 0.2,
) -> Tuple[int, Set[int], List[Tuple[int, int]]]:
    """
    Генерує випадковий граф у термінах нашої задачі:
    - n вершин (1..n)
    - випадковий список заборонених вершин
    - випадкові ребра з ймовірністю edge_prob між парами (i<j)

    Повертає:
        n, forbidden_set, edges (u, v) у 1-based індексації.
    """
    vertices = list(range(1, n + 1))

    k = max(0, int(forbidden_ratio * n))
    forbidden = set(random.sample(vertices, k)) if k > 0 else set()

    edges = []
    for u in vertices:
        for v in range(u + 1, n + 1):
            if random.random() < edge_prob:
                edges.append((u, v))

    return n, forbidden, edges


def write_instance_to_csv(path: pathlib.Path, n: int, forbidden: Set[int],
                          edges: List[Tuple[int, int]]) -> None:
    """
    Записує один експеримент у CSV у форматі:

    n,k,m
    ...
    forbidden_vertices
    ...
    u,v
    ...
    """
    k = len(forbidden)
    m = len(edges)

    with path.open("w", newline="") as f:
        writer = csv.writer(f)

        # заголовок
        writer.writerow(["n", "k", "m"])
        writer.writerow([n, k, m])

        writer.writerow(["forbidden_vertices"])
        if k > 0:
            writer.writerow(list(sorted(forbidden)))
        else:
            writer.writerow([])

        writer.writerow(["u", "v"])
        for u, v in edges:
            writer.writerow([u, v])

def python_matching_size(n: int, forbidden: Set[int],
                         edges: List[Tuple[int, int]]) -> int:
    """
    Рахує розмір максимального паросполучення через networkx,
    імітуючи ту ж логіку, що й C++:
    - ребра, інцидентні забороненим вершинам, просто ігноруються.
    """
    G = nx.Graph()
    G.add_nodes_from(range(1, n + 1))

    for u, v in edges:
        if u in forbidden or v in forbidden:
            continue
        G.add_edge(u, v)

    matching = nx.max_weight_matching(G, maxcardinality=True)
    return len(matching)

def cpp_matching_size(csv_path: pathlib.Path) -> int:
    """
    Викликає max_matching_forbidden.exe на заданому CSV
    і повертає розмір matching’у (перша строка stdout).
    """
    result = subprocess.run(
        [EXECUTABLE, str(csv_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    first_line = result.stdout.strip().splitlines()[0]
    return int(first_line)


def run_single_experiment(
    n: int,
    edge_prob: float,
    forbidden_ratio: float,
    tmp_dir: pathlib.Path,
) -> Tuple[float, float, int]:
    """
    Генерує один випадковий граф, запускає C++ та Python,
    міряє час, порівнює розмір matching’у.

    Повертає:
        (time_cpp, time_py, matching_size)
    """
    n, forbidden, edges = generate_random_instance(
        n=n,
        edge_prob=edge_prob,
        forbidden_ratio=forbidden_ratio,
    )

    csv_path = tmp_dir / f"instance_n{n}_{random.randint(0, 10**9)}.csv"
    write_instance_to_csv(csv_path, n, forbidden, edges)

    t0 = time.perf_counter()
    size_cpp = cpp_matching_size(csv_path)
    t1 = time.perf_counter()
    time_cpp = t1 - t0

    t2 = time.perf_counter()
    size_py = python_matching_size(n, forbidden, edges)
    t3 = time.perf_counter()
    time_py = t3 - t2

    if size_cpp != size_py:
        print(f"[WARNING] Розмір matching’у відрізняється для n={n}: "
              f"C++={size_cpp}, Python={size_py}")

    try:
        csv_path.unlink()
    except OSError:
        pass

    return time_cpp, time_py, size_cpp

def main():
    random.seed(42)

    tmp_dir = pathlib.Path("tmp_instances")
    tmp_dir.mkdir(exist_ok=True)

    ns = [20, 40, 80, 120, 160, 200, 250, 300]

    edge_prob = 0.15
    forbidden_ratio = 0.2
    repeats = 5

    times_cpp = []
    times_py = []
    match_sizes = []

    for n in ns:
        total_cpp = 0.0
        total_py = 0.0
        size_example = None

        print(f"n={n}...")

        for _ in range(repeats):
            t_cpp, t_py, size = run_single_experiment(
                n=n,
                edge_prob=edge_prob,
                forbidden_ratio=forbidden_ratio,
                tmp_dir=tmp_dir,
            )
            total_cpp += t_cpp
            total_py += t_py
            size_example = size

        avg_cpp = total_cpp / repeats
        avg_py = total_py / repeats

        times_cpp.append(avg_cpp)
        times_py.append(avg_py)
        match_sizes.append(size_example)

        print(f"  avg C++:   {avg_cpp:.6f} s")
        print(f"  avg Python:{avg_py:.6f} s")
        print(f"  matching size ~ {size_example}")

    plt.figure(figsize=(8, 5))
    plt.plot(ns, times_cpp, marker="o", label="C++ (EdmondsBlossom)")
    plt.plot(ns, times_py, marker="o", label="Python + networkx")

    plt.xlabel("Кількість вершин n")
    plt.ylabel("Середній час виконання, секунди")
    plt.title("Порівняння часу роботи: C++ vs Python (networkx)\nМаксимальне паросполучення з забороненими вершинами")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig("benchmark_time.png", dpi=200)
    print("Збережено графік часу у файл benchmark_time.png")

    plt.figure(figsize=(8, 5))
    ratio = [py / cpp if cpp > 0 else float("nan")
             for cpp, py in zip(times_cpp, times_py)]
    plt.plot(ns, ratio, marker="o")
    plt.xlabel("Кількість вершин n")
    plt.ylabel("Python / C++ (відношення часу)")
    plt.title("Співвідношення часу роботи Python до C++")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("benchmark_ratio.png", dpi=200)
    print("Збережено графік співвідношення у файл benchmark_ratio.png")

if __name__ == "__main__":
    main()
