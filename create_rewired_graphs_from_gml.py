import os
import networkx as nx
import numpy as np
from tqdm import tqdm
import rpy2.robjects as ro

# ---------- Load BiRewire ----------
ro.r("""
if (!requireNamespace("BiRewire", quietly = TRUE)) {
    if (!requireNamespace("BiocManager", quietly = TRUE)) {
        install.packages("BiocManager", repos="https://cloud.r-project.org")
    }
    BiocManager::install("BiRewire", ask = FALSE)
}
library(BiRewire)
""")

# Probe the return structure once so we know how to extract the matrix
ro.r("""
.birewire_returns_list <- tryCatch({
    m <- matrix(c(1L,0L,1L,1L,0L,1L,1L,0L,1L,1L,0L,1L), nrow=3L, ncol=4L)
    r <- birewire.rewire.bipartite(m)
    is.list(r)
}, error = function(e) FALSE)
""")
returns_list = bool(ro.r(".birewire_returns_list")[0])
print(f"birewire.rewire.bipartite returns list: {returns_list}")


def extract_newmatrix(rewired, nrow, ncol):
    """Extract the rewired matrix regardless of return type."""
    if returns_list:
        # Named list: result$newmatrix
        new_mat_r = rewired.rx2("newmatrix")
    else:
        # Already the matrix itself
        new_mat_r = rewired
    flat = list(new_mat_r)
    return np.array(flat, dtype=np.int32).reshape((nrow, ncol), order="F")


def rewire_matrix(mat_np, n=100):
    nrow, ncol = mat_np.shape
    mat_int = mat_np.astype(np.int32)

    r_mat = ro.r["matrix"](
        ro.IntVector(mat_int.flatten(order="F").tolist()),
        nrow=nrow,
        ncol=ncol,
    )

    results = []
    attempts = 0
    max_attempts = n * 20

    while len(results) < n and attempts < max_attempts:
        attempts += 1
        try:
            rewired = ro.r["birewire.rewire.bipartite"](r_mat)
            mat_out = extract_newmatrix(rewired, nrow, ncol)
            results.append(mat_out)
        except Exception as e:
            if attempts == 1:
                # Print once to show the actual structure
                print(f"  rewire failed, probing return type: {e}")
                try:
                    rewired = ro.r["birewire.rewire.bipartite"](r_mat)
                    print(f"  return type: {type(rewired)}, len: {len(rewired)}")
                    try:
                        print(f"  names: {list(rewired.names)}")
                    except Exception:
                        pass
                except Exception as e2:
                    print(f"  probe also failed: {e2}")
            continue

    return results


def graph_to_matrix(G):
    top_nodes = sorted([n for n, d in G.nodes(data=True) if d.get("bipartite") == 0])
    bottom_nodes = sorted([n for n, d in G.nodes(data=True) if d.get("bipartite") == 1])
    mat = nx.bipartite.biadjacency_matrix(G, row_order=top_nodes, column_order=bottom_nodes)
    return mat.toarray().astype(np.int32), top_nodes, bottom_nodes


def matrix_to_graph(mat, top_nodes, bottom_nodes):
    G = nx.Graph()
    for n in top_nodes:
        G.add_node(n, bipartite=0)
    for n in bottom_nodes:
        G.add_node(n, bipartite=1)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            if mat[i, j] > 0:
                G.add_edge(top_nodes[i], bottom_nodes[j])
    return G


def process_graph(gml_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    existing = [f for f in os.listdir(output_dir) if f.endswith(".gml")]
    if len(existing) >= 100:
        print(f"  skipping {output_dir}, already complete")
        return

    G = nx.read_gml(gml_path)
    mat_np, top_nodes, bottom_nodes = graph_to_matrix(G)

    print(f"  matrix {mat_np.shape}, sum={mat_np.sum()}, "
          f"top={len(top_nodes)}, bottom={len(bottom_nodes)}")

    if mat_np.sum() == 0:
        print("  skipping: empty matrix")
        return

    rewired_mats = rewire_matrix(mat_np, n=100)
    print(f"  got {len(rewired_mats)} rewired matrices")

    for i, mat_r in enumerate(rewired_mats):
        G_new = matrix_to_graph(mat_r, top_nodes, bottom_nodes)
        nx.write_gml(G_new, os.path.join(output_dir, f"random_{i}.gml"))

    print(f"  saved {len(rewired_mats)} files to {output_dir}")


def main():
    input_root = "input_graphs"
    output_root = "rewired_graphs"

    if not os.path.isdir(input_root):
        print(f"ERROR: input directory '{input_root}' not found")
        return

    dirs = sorted(os.listdir(input_root))
    to_process = []
    for d in dirs:
        input_dir = os.path.join(input_root, d)
        if not os.path.isdir(input_dir):
            continue
        gml_path = os.path.join(input_dir, "bipartite_graph.gml")
        if not os.path.exists(gml_path):
            print(f"  no bipartite_graph.gml in {input_dir}, skipping")
            continue
        to_process.append((d, gml_path))

    print(f"Found {len(to_process)} graphs to process")

    for d, gml_path in tqdm(to_process):
        print(f"\nProcessing: {d}")
        output_dir = os.path.join(output_root, d)
        try:
            process_graph(gml_path, output_dir)
        except Exception as e:
            print(f"  ERROR processing {d}: {e}")


if __name__ == "__main__":
    main()
