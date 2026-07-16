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
