# Research lab maintenance

The post `src/content/posts/ResearchLab/ResearchLab.md` remains a draft dated 2026-03-20, before Linker (2026-03-24). Keep `draft: true` until publication is requested.

`labDownload: true` renders `ResearchLabDownload.astro`. The archive is an embedded download link; there is no browser training runtime and no public asset endpoint for the draft.

The Python files in `files/` are maintained source templates. `scripts/package_research_lab.py` specializes them into self-contained `day01/lab.py` through `day14/lab.py`, retaining only the corresponding lesson's algorithm and model. Each folder also contains its own requirements and README. All Python learning days include a self-contained notebook. Day 12 includes Neo4j Compose, graph data and Cypher instead of a notebook.

Daily READMEs and `curriculum.md` are generated from the curriculum block in the post. Update that block before packaging. Default CLI output is each script's sibling `results/` folder, independent of the working directory. MNIST is shared in the archive root's `data/` directory. Notebooks use the current directory for data and output.

```sh
python3.11 scripts/package_research_lab.py
pnpm exec biome format --write src/labs/research/bundle.json
node --test tests/research-lab.test.mjs
python -m unittest discover -s tests -p "test_research_course.py"
```

The archive is deterministic; `bundle.json` records ZIP and file SHA-256 digests. Python tests require `requirements-ml.txt`, CPU PyTorch and the Neo4j driver. They extract the actual ZIP, run daily scripts from a different working directory and verify per-day outputs. Database integration can be checked separately using the isolated day12 Compose setup.
