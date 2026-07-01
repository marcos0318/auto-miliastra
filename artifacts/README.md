# Local data layout

Game exports and tool outputs live here, **one directory per project**. Shared node catalog stays at the repo level. Nothing under each project's `input/`, `parsed/`, or `output/` is committed (see `.gitignore`).

```text
artifacts/
├── catalog/                 # Shared node kernel catalog (tracked)
│   └── node_data.json
├── active_project           # Current project name (tracked, default: double_gun)
├── README.md
└── projects/
    └── double_gun/          # One folder per level / game mode / experiment
        ├── input/           # Original exports from Miliastra — read-only
        │   ├── levels/      #   .gil level saves
        │   └── assets/      #   .gia / .gip asset files
        ├── parsed/          # Intermediate parse results
        │   ├── levels/      #   .json, .summary.txt, .graphs.json
        │   └── assets/
        └── output/          # Files ready to import back into the game
            ├── levels/
            └── assets/
```

## Workflow

1. Create or switch project:

   ```powershell
   miliastra use double_gun
   miliastra use my_other_level
   miliastra projects          # list projects (* = active)
   ```

2. Copy exports → `artifacts/projects/<project>/input/levels/my_level.gil`

3. Parse:

   ```powershell
   miliastra parse-input
   # or one-off with another project:
   miliastra -p my_other_level parse-input
   ```

   Writes `parsed/levels/<stem>.json`, `<stem>.summary.txt`, `<stem>.graphs.json`.

4. Generate assets → `miliastra generate-platforms` (defaults to active project's `output/assets/`)

5. Import **only** from `output/` back into the editor (never overwrite `input/`)

## Environment

Set `MILIastra_PROJECT=my_level` to override the active project without editing `active_project`.

## Naming

Use the same stem across stages within a project:

```text
projects/double_gun/input/levels/double_gun.gil
projects/double_gun/parsed/levels/double_gun.json
projects/double_gun/parsed/levels/double_gun.graphs.json
projects/double_gun/output/levels/double_gun.gil   # if you patch and re-export
```

## Debug / probe files

Ad-hoc decode dumps belong in that project's `parsed/`, not the repo root.
