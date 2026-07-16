"""Validation tests for the shared conceptual and granular controller models."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import rdflib
from pyshacl import validate


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "control"


def _turtle_graph(path: Path) -> rdflib.Graph:
    graph = rdflib.Graph()
    graph.parse(path, format="turtle")
    return graph


@pytest.mark.parametrize("path", sorted(ROOT.rglob("*.json")))
def test_all_contexts_are_valid_json(path: Path) -> None:
    json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "path",
    sorted(
        [*ROOT.rglob("*.ttl"), *ROOT.rglob("*.shacl.ttl")],
        key=lambda candidate: candidate.as_posix(),
    ),
)
def test_all_shapes_and_fixtures_are_valid_turtle(path: Path) -> None:
    _turtle_graph(path)


@pytest.mark.parametrize(
    ("fixture", "shape"),
    [
        ("pid-valid.ttl", "control/controller.shacl.ttl"),
        ("feedback-loop-valid.ttl", "control/system.shacl.ttl"),
    ],
)
def test_valid_control_fixtures_conform(fixture: str, shape: str) -> None:
    conforms, _, _ = validate(
        data_graph=_turtle_graph(FIXTURES / fixture),
        shacl_graph=_turtle_graph(ROOT / shape),
        inference="rdfs",
    )

    assert conforms


@pytest.mark.parametrize(
    ("fixture", "shape"),
    [
        ("pid-missing-derivative.ttl", "control/controller.shacl.ttl"),
        ("feedback-loop-missing-manipulated.ttl", "control/system.shacl.ttl"),
    ],
)
def test_invalid_control_fixtures_do_not_conform(fixture: str, shape: str) -> None:
    conforms, _, report = validate(
        data_graph=_turtle_graph(FIXTURES / fixture),
        shacl_graph=_turtle_graph(ROOT / shape),
        inference="rdfs",
    )

    assert not conforms
    assert "Constraint Violation" in str(report)


def test_control_contexts_have_no_retired_controller_namespace() -> None:
    for path in (ROOT / "control").glob("*.json"):
        assert "https://controller.org/metamodels/" not in path.read_text(encoding="utf-8")


def test_supervision_operator_expands_to_an_xsd_string() -> None:
    graph = rdflib.Graph()
    graph.parse(
        data=json.dumps(
            {
                "@context": (ROOT / "control" / "supervision.json").as_uri(),
                "@id": "https://example.test/control/comparison",
                "operator": "less-than",
            }
        ),
        format="json-ld",
    )

    operator = rdflib.URIRef(
        "https://secorolab.github.io/metamodels/control/supervision#comparison-operator"
    )
    value = graph.value(
        subject=rdflib.URIRef("https://example.test/control/comparison"),
        predicate=operator,
    )

    assert value == rdflib.Literal("less-than", datatype=rdflib.XSD.string)


def test_detailed_controller_properties_do_not_depend_on_type_order() -> None:
    graph = rdflib.Graph()
    graph.parse(
        data=json.dumps(
            {
                "@context": (ROOT / "control" / "controller.json").as_uri(),
                "@id": "https://example.test/control/controller",
                "@type": ["Controller", "DetailedController"],
                "operation": ["https://example.test/control/operation"],
                "control-signal": "https://example.test/control/output",
            }
        ),
        format="json-ld",
    )

    controller = rdflib.URIRef("https://example.test/control/controller")
    assert (
        controller,
        rdflib.URIRef("https://secorolab.github.io/metamodels/control/controller#operation"),
        rdflib.URIRef("https://example.test/control/operation"),
    ) in graph
    assert (
        controller,
        rdflib.URIRef(
            "https://comp-rob2b.github.io/metamodels/task/constraint-handler#control-signal"
        ),
        rdflib.URIRef("https://example.test/control/output"),
    ) in graph


def test_supervision_properties_do_not_depend_on_type_order() -> None:
    graph = rdflib.Graph()
    graph.parse(
        data=json.dumps(
            {
                "@context": (ROOT / "control" / "supervision.json").as_uri(),
                "@id": "https://example.test/control/monitor",
                "@type": ["ConstraintMonitor", "EventMonitor"],
                "monitored-constraint": "https://example.test/control/constraint",
                "emits-event": "https://example.test/control/event",
            }
        ),
        format="json-ld",
    )

    monitor = rdflib.URIRef("https://example.test/control/monitor")
    assert (
        monitor,
        rdflib.URIRef(
            "https://secorolab.github.io/metamodels/control/supervision#emits-event"
        ),
        rdflib.URIRef("https://example.test/control/event"),
    ) in graph


def test_computation_properties_do_not_depend_on_type_order() -> None:
    graph = rdflib.Graph()
    graph.parse(
        data=json.dumps(
            {
                "@context": (ROOT / "control" / "computation.json").as_uri(),
                "@id": "https://example.test/control/activity",
                "@type": ["ControlActivity", "FunctionInvocation"],
                "algorithm-details": "https://example.test/control/operation",
                "invokes-operation": "https://example.test/control/operation",
            }
        ),
        format="json-ld",
    )

    activity = rdflib.URIRef("https://example.test/control/activity")
    assert (
        activity,
        rdflib.URIRef(
            "https://secorolab.github.io/metamodels/control/computation#invokes-operation"
        ),
        rdflib.URIRef("https://example.test/control/operation"),
    ) in graph
