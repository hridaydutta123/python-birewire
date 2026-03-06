import os
import argparse
import networkx as nx
import numpy as np
from tqdm import tqdm

from rpy2.robjects import pandas2ri, numpy2ri
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr


def parse_args():
    parser = argparse.ArgumentParser(
        description="Rewire bipartite graphs using BiRewire"
    )

    parser.add_argument("--input_dir", required=True)
    parser.add_argument("--output_dir", required=True)

    parser.add_argument(
        "--num_rewires",
        type=int,
        default=1000
    )

    parser.add_argument(
        "--bipartite_attr",
        default="bipartite"
    )

    return parser.parse_args()


def main():

    args = parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir
    NUM_REWIRES = args.num_rewires
    bip_attr = args.bipartite_attr

    os.makedirs(output_dir, exist_ok=True)

    pandas2ri.activate()
    numpy2ri.activate()

    print("Loading BiRewire...")
    birewire = importr("BiRewire")
    print("BiRewire loaded\n")

    # Find all graph folders
    graph_dirs = [
        d for d in os.listdir(input_dir)
        if os.path.isdir(os.path.join(input_dir, d))
    ]

    print(f"Found {len(graph_dirs)} graph directories\n")

    for idx, graph_dir in enumerate(graph_dirs):

        graph_path = os.path.join(
            input_dir,
            graph_dir,
            "bipartite_graph.gml"
        )

        if not os.path.exists(graph_path):
            print(f"Skipping {graph_dir} (no bipartite_graph.gml)")
            continue

        print(f"\n[{idx+1}/{len(graph_dirs)}] Processing {graph_dir}")

        output_subdir = os.path.join(output_dir, graph_dir)
        os.makedirs(output_subdir, exist_ok=True)

        existing = [
            f for f in os.listdir(output_subdir)
            if f.startswith("random_")
        ]

        if len(existing) >= NUM_REWIRES:
            print("Already completed — skipping")
            continue

        G = nx.read_gml(graph_path)

        bipartite_dict = nx.get_node_attributes(G, bip_attr)

        # Remove intra-layer edges
        G.remove_edges_from([
            (u, v) for u, v in G.edges()
            if bipartite_dict.get(u) == bipartite_dict.get(v)
        ])

        # Remove zero degree nodes
        G.remove_nodes_from([n for n, d in G.degree() if d == 0])

        # Split sets
        top_nodes = {n for n, d in G.nodes(data=True) if d.get(bip_attr) == 0}
        bottom_nodes = set(G.nodes()) - top_nodes

        print(f"Nodes: {len(top_nodes)} top | {len(bottom_nodes)} bottom")

        top_list = list(top_nodes)
        bottom_list = list(bottom_nodes)

        top_index = {n: i for i, n in enumerate(top_list)}
        bottom_index = {n: i for i, n in enumerate(bottom_list)}

        adj_np = np.zeros((len(top_list), len(bottom_list)), dtype=int)

        for u, v in G.edges():

            if u in top_nodes:
                adj_np[top_index[u], bottom_index[v]] = 1
            else:
                adj_np[top_index[v], bottom_index[u]] = 1

        robjects.globalenv["adj_matrix"] = numpy2ri.py2rpy(adj_np)

        for i in tqdm(range(len(existing), NUM_REWIRES), desc="Rewiring"):

            robjects.r(
                "rewired_matrix <- birewire.rewire.bipartite(adj_matrix)"
            )

            rewired_np = numpy2ri.rpy2py(
                robjects.r["rewired_matrix"]
            )

            rewired_graph = nx.Graph()

            for ti, u in enumerate(top_list):
                for bi, v in enumerate(bottom_list):

                    if rewired_np[ti, bi] == 1:
                        rewired_graph.add_edge(u, v)

            nx.set_node_attributes(
                rewired_graph,
                {n: 0 for n in top_list},
                bip_attr
            )

            nx.set_node_attributes(
                rewired_graph,
                {n: 1 for n in bottom_list},
                bip_attr
            )

            output_file = os.path.join(
                output_subdir,
                f"random_{i}.gml"
            )

            nx.write_gml(rewired_graph, output_file)

        print(f"Finished {graph_dir}")

    print("\nAll graphs completed")


if __name__ == "__main__":
    main()
