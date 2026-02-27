# Contributing to OpenVisionStudio

Thank you for contributing!

## Local setup

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -e .[dev]
pytest
```

## Adding a node plugin

A plugin node should implement `NodeDefinition` and expose it through a module-level list called `PLUGIN_NODES`.

```python
from openvisionstudio.nodes.base import NodeDefinition, PortSpec, ParamSpec, DataType

class MyNode(NodeDefinition):
    type_name = "Plugin.MyNode"
    display_name = "My Node"
    inputs = [PortSpec("image", DataType.IMAGE)]
    outputs = [PortSpec("result", DataType.IMAGE)]
    params = [ParamSpec("factor", float, 1.0)]

    def compute(self, inputs, params, context):
        image = inputs.get("image")
        # process
        return {"result": image}

PLUGIN_NODES = [MyNode]
```

Drop plugin files in `src/openvisionstudio/plugins/` and restart app.

## Coding standards

- Use type hints and concise docstrings.
- Keep nodes deterministic unless explicitly stream-based.
- Return informative error messages.
- Ensure new nodes have at least one unit test for compute behavior.
