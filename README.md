# miliastra-agent

Python automation toolkit for Genshin Impact Miliastra Wonderland: parse GIL/GIA saves, generate entity assets programmatically, and (planned) agent-assisted level design.

## Roadmap

- [x] Project scaffold / CLI
- [x] Parse `.gil` / `.gia` entities and transforms
- [x] Parse GIL node graphs and entity↔graph bindings
- [x] Programmatic entity generation (`.gia`)
- [ ] Write back / patch `.gil` level saves
- [ ] genshin-ts logic injection integration
- [ ] Agent pipeline (design → generate → validate)

## Capabilities

### Parse (read)

| Input | Extracted |
|-------|-----------|
| `.gil` level save | Level name, entity placements (field 5 + 27), node graphs (field 10), entity↔graph bindings |
| `.gia` asset | Entity assets: template ID, name, transform |

Parse output lands under `artifacts/projects/<project>/parsed/`:

- `<stem>.json` — entities, graph summaries, bindings
- `<stem>.summary.txt` — human-readable overview
- `<stem>.graphs.json` — full node graphs with kernel names from `artifacts/catalog/node_data.json`

### Generate (write)

| Output | Description |
|--------|-------------|
| `.gia` entity assets | Valid protobuf payloads (UGC-File-Generate-Utils compatible). Import from `output/assets/` into the editor. |

Currently supports basic entities: name, template ID, position / rotation / scale. Combat, preset state, and node components are not encoded yet.

## Install

```powershell
cd e:\repo\miliastra-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Usage

```powershell
# Project management
miliastra version
miliastra use double_gun
miliastra projects

# Parse exports from input/ → parsed/
miliastra parse-input
miliastra parse artifacts/projects/double_gun/input/levels/double_gun.gil --json

# Generate importable .gia assets → output/assets/
miliastra generate-platforms --count 20
```

See [artifacts/README.md](artifacts/README.md) for the full input → parsed → output workflow.

## Layout

```text
miliastra-agent/
├── artifacts/              # Local data (see artifacts/README.md)
│   ├── catalog/            #   Shared node kernel catalog (node_data.json)
│   └── projects/           #   Per-project input / parsed / output
├── src/miliastra_agent/
│   ├── cli/                # Typer CLI entrypoint
│   ├── catalog/            # Node kernel ID → display name
│   ├── core/               # Models, GI container, protobuf defs
│   ├── parsers/            # GIL/GIA decode (entities, graphs, bindings)
│   ├── generators/         # GIA entity encode (gia_encode.py)
│   ├── agents/             # Agent orchestration (planned)
│   └── integrations/       # genshin-ts, MCP, etc. (planned)
└── tests/
```

## References

- [UGC-File-Generate-Utils](https://github.com/luern0313/UGC-File-Generate-Utils) — GIA entity encoding reference
- [genshin-miliastra-file-format](https://github.com/script-1024/genshin-miliastra-file-format)
- [genshin-ts](https://github.com/josStorer/genshin-ts)

## License

MIT — for research and learning only. Follow HoYoverse terms and Miliastra creator guidelines.
