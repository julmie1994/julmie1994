import numpy as np

from openvisionstudio.engine.executor import GraphExecutor
from openvisionstudio.engine.graph_model import ConnectionModel, GraphModel, NodeModel
from openvisionstudio.nodes.base import NodeDefinition


class SourceNode(NodeDefinition):
    type_name = "Test.Source"

    def compute(self, inputs, params, context):
        context["source_calls"] = context.get("source_calls", 0) + 1
        return {"value": np.array([[1, 2], [3, 4]], dtype=np.uint8)}


class PassNode(NodeDefinition):
    type_name = "Test.Pass"

    def compute(self, inputs, params, context):
        context["pass_calls"] = context.get("pass_calls", 0) + 1
        return {"value": inputs["value"]}


class SumNode(NodeDefinition):
    type_name = "Test.Sum"

    def compute(self, inputs, params, context):
        image = inputs["value"]
        return {"sum": int(image.sum())}


def make_graph() -> GraphModel:
    return GraphModel(
        nodes={
            "n1": NodeModel("n1", "Test.Source", {}),
            "n2": NodeModel("n2", "Test.Pass", {}),
            "n3": NodeModel("n3", "Test.Sum", {}),
        },
        connections=[
            ConnectionModel("n1", "value", "n2", "value"),
            ConnectionModel("n2", "value", "n3", "value"),
        ],
    )


def test_topological_execution_and_compute() -> None:
    ex = GraphExecutor({"Test.Source": SourceNode, "Test.Pass": PassNode, "Test.Sum": SumNode})
    result = ex.execute(make_graph(), context={})
    assert result.errors == {}
    assert result.outputs["n3"]["sum"] == 10


def test_caching_prevents_recompute() -> None:
    ex = GraphExecutor({"Test.Source": SourceNode, "Test.Pass": PassNode, "Test.Sum": SumNode})
    context = {}
    ex.execute(make_graph(), context=context)
    ex.execute(make_graph(), context=context)
    assert context["source_calls"] == 1
    assert context["pass_calls"] == 1
