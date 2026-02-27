# OpenVisionStudio

OpenVisionStudio is a Windows-first, open-source computer-vision pipeline IDE inspired by HALCON/HDevelop concepts.
It provides a node-graph editor, OpenCV-backed processing nodes, live preview, and a plugin architecture.

## Features

- Node editor using **NodeGraphQt**
- Live preview with zoom/pan and pixel readout
- Background pipeline execution with caching
- Step-through execution (run until selected node)
- Project save/load (`.ovs.json`) + recent projects
- Export graph to plain Python/OpenCV script
- Built-in nodes for core image processing workflows
- Plugin-friendly node registration system

## Screenshot

_Add screenshot here after running app on Windows._

## Install

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -e .[dev]
```

## Run

```bash
python -m openvisionstudio
```

## Build Windows executable

```bat
build_windows.bat
```

The build script uses PyInstaller and bundles sample resources.

## Project format

Projects are JSON documents with schema versioning.

- `app_version`
- `schema_version`
- `nodes`: id, type, position, params
- `connections`: from/to endpoints

## Development

- Add nodes under `src/openvisionstudio/nodes/builtin` or in plugins.
- Extend UI components under `src/openvisionstudio/ui`.
- Core execution and caching lives under `src/openvisionstudio/engine`.

## Sample assets

- `src/openvisionstudio/resources/samples/images`
- `src/openvisionstudio/resources/samples/projects`

## License

MIT (see `LICENSE`).
