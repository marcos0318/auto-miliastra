# miliastra-agent

Python automation toolkit for Genshin Impact Miliastra Wonderland: parse GIL/GIA saves, generate entities programmatically, and (planned) agent-assisted level design.

## Roadmap

- [x] Project scaffold / CLI
- [ ] Parse `.gil` / `.gia` entities and transforms
- [ ] Programmatic entity generation (`.gia`)
- [ ] genshin-ts logic injection integration
- [ ] Agent pipeline (design -> generate -> validate)

## Install

```powershell
cd e:\repo\miliastra-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Usage

```powershell
miliastra version
miliastra use double_gun
miliastra parse-input
miliastra parse artifacts/projects/double_gun/input/levels/double_gun.gil --json
miliastra generate-platforms --count 20
```

## Layout

```text
miliastra-agent/
├── artifacts/              # Local data (see artifacts/README.md)
│   ├── catalog/            #   Shared node catalog
│   └── projects/           #   Per-project input / parsed / output
├── src/miliastra_agent/
│   ├── cli/                # Typer CLI entrypoint
│   ├── core/               # Models and GIL/GIA container format
│   ├── parsers/            # Extract entities, node graphs, etc.
│   ├── generators/         # Procedural level content
│   ├── agents/             # Agent orchestration (planned)
│   └── integrations/       # genshin-ts, MCP, etc.
└── tests/
```

## References

- [UGC-File-Generate-Utils](https://github.com/luern0313/UGC-File-Generate-Utils)
- [genshin-miliastra-file-format](https://github.com/script-1024/genshin-miliastra-file-format)
- [genshin-ts](https://github.com/josStorer/genshin-ts)

## License

MIT -- for research and learning only. Follow HoYoverse terms and Miliastra creator guidelines.