# Bipartite graph randomization using BiReWire

This repository contains code to generate random bipartite network graphs by rewiring existing community graph structures while preserving degree distributions. It uses the BiRewire R package through rpy2 to perform statistically rigorous network randomization.

## Overview

The code takes a collection of GML graph files representing bipartite networks and creates randomized versions of these networks while preserving the degree distribution of nodes. This is useful for creating null models to compare against real networks when testing hypotheses about network structure.

## Requirements

### Python Dependencies
- networkx
- numpy
- pandas
- rpy2
- tqdm

### R Dependencies
- BiRewire

## Installation

1. Install Python dependencies:
```bash
pip install networkx numpy pandas rpy2 tqdm
# Or use requirements.txt
pip install -r requirements.txt
```

2. Install R and the BiRewire package:
```bash
# In R console
install.packages("BiRewire")
# Or use the provided script
Rscript install_r_dependencies.R
```

## Directory Structure

- Your input directory (default: `communities_graphs/`): Contains the original GML graph files
- Your output directory (default: `communities_graphs_random/`): Where randomized graphs will be stored

## Usage

Run the main script with optional arguments:

```bash
# Using default directories
python rewire_graphs.py

# Specify custom input and output directories
python rewire_graphs.py --input-dir my_graphs --output-dir my_random_graphs

# Or use short options
python rewire_graphs.py -i my_graphs -o my_random_graphs

# Control the number of random networks generated per input graph
python rewire_graphs.py --iterations 500

# Control the number of worker processes
python rewire_graphs.py --workers 8
```

### Command-line Arguments

| Option | Short | Description |
|--------|-------|-------------|
| `--input-dir` | `-i` | Directory containing input GML files (default: communities_graphs) |
| `--output-dir` | `-o` | Directory for storing randomized graphs (default: communities_graphs_random) |
| `--iterations` | `-n` | Number of random rewirings per graph (default: 1000) |
| `--workers` | `-w` | Maximum number of worker processes (default: auto) |

## How It Works

1. For each GML file in the input directory:
   - The graph is loaded and converted to a bipartite adjacency matrix
   - Node names are sanitized to ensure compatibility with R
   - The BiRewire package is used to rewire the network while maintaining degree distributions
   - The rewired networks are converted back to NetworkX graphs and saved as GML files

2. Parallel processing is used at two levels:
   - Multiple GML files are processed concurrently
   - For each file, multiple rewiring iterations are run in parallel

## License

MIT License

Copyright (c) 2025 Hridoy Sankar Dutta

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
