"""Program to find the maximum matching in a graph with forbidden vertices."""

import sys
import csv
import networkx as nx


def process_csv(csv_path: str):
    """Reads the CSV file, builds the graph, and returns maximum matching."""

    with open(csv_path, newline="") as f:
        reader = csv.reader(f)

        header = next(reader, None)
        values = next(reader, None)

        n = int(values[0].strip())
        k = int(values[1].strip())
        m = int(values[2].strip())

        next(reader)
        forbidden_row = next(reader)

        forbidden = set(int(tok.strip()) for tok in forbidden_row if tok.strip())

        next(reader)

        G = nx.Graph()

        for row in reader:
            if len(row) < 2:
                continue

            u = int(row[0].strip())
            v = int(row[1].strip())

            if u in forbidden or v in forbidden:
                continue

            G.add_edge(u, v)

    matching = nx.algorithms.matching.max_weight_matching(G, maxcardinality=True)

    edges = []
    for u, v in matching:
        u, v = sorted((u, v))
        edges.append((u, v))

    edges.sort()
    return len(edges), edges


def main():
    """Main function to handle command-line input and output results."""

    if len(sys.argv) != 2:
        print("Usage: python max_matching_forbidden.py input.csv", file=sys.stderr)
        sys.exit(1)

    csv_path = sys.argv[1]

    size, edges = process_csv(csv_path)

    print(size)
    for u, v in edges:
        print(u, v)


if __name__ == "__main__":
    main()
