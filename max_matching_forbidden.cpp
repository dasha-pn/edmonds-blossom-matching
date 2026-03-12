#include <vector>
#include <queue>
#include <string>
#include <sstream>
#include <fstream>
#include <iostream>
#include <algorithm>

struct EdmondsBlossom {
    int n;
    std::vector<std::vector<int>> g;
    std::vector<int> match;
    std::vector<int> parent;
    std::vector<int> base;
    std::vector<int> q;
    std::vector<bool> used;
    std::vector<bool> blossom;

    EdmondsBlossom(int n_, const std::vector<std::vector<int>>& adj)
        : n(n_), g(adj),
          match(n, -1),
          parent(n),
          base(n),
          q(n),
          used(n),
          blossom(n)
    {}

    int findLCA(int a, int b) {
        std::vector<bool> usedPath(n, false);
        while (true) {
            a = base[a];
            usedPath[a] = true;
            if (match[a] == -1) break;
            a = parent[match[a]];
        }
        while (true) {
            b = base[b];
            if (usedPath[b]) return b;
            if (match[b] == -1) break;
            b = parent[match[b]];
        }
        return -1;
    }

    void markPath(int v, int b, int child) {
        while (base[v] != b) {
            blossom[base[v]] = blossom[base[match[v]]] = true;
            parent[v] = child;
            child = match[v];
            v = parent[match[v]];
        }
    }

    bool findAugmentingPath(int root) {
        std::fill(used.begin(), used.end(), false);
        std::fill(parent.begin(), parent.end(), -1);
        for (int i = 0; i < n; ++i) {
            base[i] = i;
        }

        int qh = 0, qt = 0;
        q[qt++] = root;
        used[root] = true;

        while (qh < qt) {
            int v = q[qh++];

            for (int to : g[v]) {
                if (base[v] == base[to] || match[v] == to) continue;

                if (to == root || (match[to] != -1 && parent[match[to]] != -1)) {
                    int blossomBase = findLCA(v, to);
                    std::fill(blossom.begin(), blossom.end(), false);
                    markPath(v, blossomBase, to);
                    markPath(to, blossomBase, v);

                    for (int i = 0; i < n; ++i) {
                        if (blossom[base[i]]) {
                            base[i] = blossomBase;
                            if (!used[i]) {
                                used[i] = true;
                                q[qt++] = i;
                            }
                        }
                    }
                }
                else if (parent[to] == -1) {
                    parent[to] = v;
                    if (match[to] == -1) {
                        int cur = to;
                        while (cur != -1) {
                            int prev = parent[cur];
                            int next = (prev == -1) ? -1 : match[prev];
                            if (prev != -1) {
                                match[cur] = prev;
                                match[prev] = cur;
                            }
                            cur = next;
                        }
                        return true;
                    } else {
                        int partner = match[to];
                        if (!used[partner]) {
                            used[partner] = true;
                            q[qt++] = partner;
                        }
                    }
                }
            }
        }
        return false;
    }

    int maxMatching() {
        int matchingSize = 0;
        for (int i = 0; i < n; ++i) {
            if (match[i] == -1) {
                if (findAugmentingPath(i)) {
                    ++matchingSize;
                }
            }
        }
        return matchingSize;
    }
};

static std::vector<std::string> splitCSV(const std::string& line) {
    std::vector<std::string> tokens;
    std::string token;
    std::stringstream ss(line);
    while (std::getline(ss, token, ',')) {
        size_t start = token.find_first_not_of(" \t\r\n");
        size_t end   = token.find_last_not_of(" \t\r\n");
        if (start == std::string::npos) {
            tokens.push_back("");
        } else {
            tokens.push_back(token.substr(start, end - start + 1));
        }
    }
    return tokens;
}

int main(int argc, char* argv[]) {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    std::istream* in = &std::cin;
    std::ifstream file;
    if (argc > 1) {
        file.open(argv[1]);
        if (!file) {
            std::cerr << "Cannot open file: " << argv[1] << "\n";
            return 1;
        }
        in = &file;
    }

    std::string line;

    if (!std::getline(*in, line)) {
        std::cerr << "Empty CSV input\n";
        return 0;
    }

    if (!getline(*in, line)) {
        std::cerr << "Missing n,k,m values\n";
        return 0;
    }
    auto parts = splitCSV(line);
    if (parts.size() < 3) {
        std::cerr << "Invalid n,k,m line: " << line << "\n";
        return 0;
    }

    int n = stoi(parts[0]);
    int k = stoi(parts[1]);
    int m = stoi(parts[2]);

    if (!getline(*in, line)) {
        std::cerr << "Missing 'forbidden_vertices' label\n";
        return 0;
    }

    if (!getline(*in, line)) {
        std::cerr << "Missing forbidden vertices line\n";
        return 0;
    }
    parts = splitCSV(line);
    std::vector<bool> forbidden(n, false);
    int countForbidden = 0;
    for (const auto& t : parts) {
        if (!t.empty()) {
            int v = stoi(t);
            --v;
            if (0 <= v && v < n) {
                if (!forbidden[v]) {
                    forbidden[v] = true;
                    ++countForbidden;
                }
            }
        }
    }
    if (countForbidden != k) {
        std::cerr << "Warning: k=" << k << " but parsed " << countForbidden
             << " forbidden vertices from CSV\n";
    }

    if (!getline(*in, line)) {
        std::cerr << "Missing edges header 'u,v'\n";
        return 0;
    }

    std::vector<std::vector<int>> adj(n);
    while (getline(*in, line)) {
        std::string trimmed = line;
        {
            size_t start = trimmed.find_first_not_of(" \t\r\n");
            size_t end   = trimmed.find_last_not_of(" \t\r\n");
            if (start == std::string::npos) {
                continue;
            }
            trimmed = trimmed.substr(start, end - start + 1);
        }

        parts = splitCSV(trimmed);
        if (parts.size() < 2) {
            std::cerr << "Warning: invalid edge line: " << trimmed << "\n";
            continue;
        }

        int u = stoi(parts[0]) - 1;
        int v = stoi(parts[1]) - 1;

        if (u < 0 || u >= n || v < 0 || v >= n) {
            std::cerr << "Skipping edge with invalid vertex index: " << trimmed << "\n";
            continue;
        }

        if (forbidden[u] || forbidden[v]) {
            continue;
        }

        adj[u].push_back(v);
        adj[v].push_back(u);
    }

    EdmondsBlossom blossom(n, adj);
    int size = blossom.maxMatching();

    std::vector<std::pair<int,int>> edges;
    std::vector<bool> used(n, false);
    for (int v = 0; v < n; ++v) {
        int u = blossom.match[v];
        if (u != -1 && !used[v] && !used[u]) {
            used[v] = used[u] = true;
            int a = v + 1;
            int b = u + 1;
            if (a > b) std::swap(a, b);
            edges.emplace_back(a, b);
        }
    }

    sort(edges.begin(), edges.end());

    std::cout << size << "\n";
    for (auto [u, v] : edges) {
        std::cout << u << " " << v << "\n";
    }

    return 0;
}
