# Research lab maintenance

`src/content/posts/ResearchLab/ResearchLab.md` is intentionally a draft dated 2026-03-20, before Linker (2026-03-24). It is available in Astro development mode and excluded from production routes, feeds and search. Keep `draft: true` until publication is requested.

`practice: true` renders `ResearchLab.astro`. Its browser runtime and download ZIP are embedded in that page; there is no public download endpoint for the draft.

After changing `files/`, `graph-data.json`, or the notebook generator:

```sh
python3.11 scripts/package_research_lab.py
pnpm exec biome format --write src/labs/research/bundle.json
node --test tests/research-lab.test.mjs
```

The ZIP is deterministic and its SHA-256 plus individual file hashes are recorded in `bundle.json`. `cnn_lab.ipynb`, `seed.cypher`, and `queries.cypher` are generated from the maintained Python sources and graph data. Python requirements install only on the learner's machine, not in the website build.

The browser graph is a JSON simulation with matching Cypher examples. The browser CNN performs convolution, backpropagation and SGD locally on synthetic lines. The downloadable exercises use real Neo4j and PyTorch/MNIST. These datasets and accuracy measurements must remain clearly distinguished.
