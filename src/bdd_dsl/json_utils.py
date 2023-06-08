import glob
from importlib import import_module
from typing import List, Tuple
import json
from os.path import join
from pyld import jsonld
import py_trees as pt
import rdflib
from bdd_dsl.behaviours.actions import ActionWithEvents
from bdd_dsl.coordination import EventLoop
from bdd_dsl.metamodels import META_MODELs_PATH
from bdd_dsl.models.queries import (
    EVENT_LOOP_QUERY,
    BEHAVIOUR_TREE_QUERY,
    Q_BT_SEQUENCE,
    Q_BT_PARALLEL,
)
from bdd_dsl.models.frames import (
    EVENT_LOOP_FRAME,
    BEHAVIOUR_TREE_FRAME,
    FR_NAME,
    FR_DATA,
    FR_EVENTS,
    FR_SUBTREE,
    FR_TYPE,
    FR_CHILDREN,
    FR_START_E,
    FR_END_E,
    FR_IMPL_MODULE,
    FR_IMPL_CLASS,
    FR_IMPL_ARG_NAMES,
    FR_IMPL_ARG_VALS,
    FR_EL,
)


def load_metamodels() -> rdflib.Graph:
    graph = rdflib.Graph()
    mm_files = glob.glob(join(META_MODELs_PATH, "*.json"))
    for mm_file in mm_files:
        graph.parse(mm_file, format="json-ld")
    return graph


def query_graph(graph: rdflib.Graph, query_str: str) -> dict:
    res = graph.query(query_str)
    res_json = json.loads(res.serialize(format="json-ld"))
    transformed_model = {"@graph": res_json}
    return transformed_model


def query_graph_with_file(graph: rdflib.Graph, query_file: str):
    with open(query_file) as infile:
        query_str = infile.read()
    return query_graph(graph, query_str)


def frame_model_with_file(model: dict, frame_file: str):
    with open(frame_file) as infile:
        frame_str = infile.read()
    frame_dict = json.loads(frame_str)
    return jsonld.frame(model, frame_dict)


def create_event_loop_from_data(el_data: dict) -> EventLoop:
    """
    create an EventLoop object from framed, dictionary-like data
    """
    event_names = [event[FR_NAME] for event in el_data[FR_EVENTS]]
    return EventLoop(el_data[FR_NAME], event_names)


def create_event_loop_from_graph(graph: rdflib.Graph) -> list:
    model = query_graph(graph, EVENT_LOOP_QUERY)
    framed_model = jsonld.frame(model, EVENT_LOOP_FRAME)

    if FR_DATA in framed_model:
        # multiple matches
        event_loops = []
        for event_loop_data in framed_model[FR_DATA]:
            event_loops.append(create_event_loop_from_data(event_loop_data))
        return event_loops

    # single match
    return [create_event_loop_from_data(framed_model)]


def load_python_event_action(node_data: dict, event_loop: EventLoop):
    if FR_NAME not in node_data:
        raise ValueError(f"'{FR_NAME}' not found in node data")
    node_name = node_data[FR_NAME]

    for k in [FR_START_E, FR_END_E, FR_IMPL_MODULE, FR_IMPL_CLASS]:
        if k in node_data:
            continue
        raise ValueError(f"required key '{k}' not found in data for action '{node_name}'")

    action_cls = getattr(import_module(node_data[FR_IMPL_MODULE]), node_data[FR_IMPL_CLASS])
    if not issubclass(action_cls, ActionWithEvents):
        raise ValueError(
            f"'{action_cls.__name__}' is not a subclass of '{ActionWithEvents.__name__}'"
        )

    kwarg_dict = {}
    if FR_IMPL_ARG_NAMES in node_data and FR_IMPL_ARG_VALS in node_data:
        kwarg_names = node_data[FR_IMPL_ARG_NAMES]
        kwarg_vals = node_data[FR_IMPL_ARG_VALS]
        if not isinstance(kwarg_names, List):
            kwarg_names = [kwarg_names]
        if not isinstance(kwarg_vals, List):
            kwarg_vals = [kwarg_vals]

        if len(kwarg_names) != len(kwarg_vals):
            raise ValueError(f"argument count mismatch for action '{node_name}")
        for i in range(len(kwarg_names)):
            kwarg_dict[kwarg_names[i]] = kwarg_vals[i]
    return action_cls(
        node_name,
        event_loop,
        node_data[FR_START_E][FR_NAME],
        node_data[FR_END_E][FR_NAME],
        **kwarg_dict,
    )


def create_subtree_behaviours(subtree_data: dict, event_loop: EventLoop) -> pt.composites.Composite:
    subtree_name = subtree_data[FR_NAME]
    composite_type = subtree_data[FR_TYPE]
    subtree_root = None
    if composite_type == Q_BT_SEQUENCE:
        subtree_root = pt.composites.Sequence(name=subtree_name, memory=True)
    elif composite_type == Q_BT_PARALLEL:
        # TODO: annotate policy on graph
        policy = pt.common.ParallelPolicy.SuccessOnAll(synchronise=True)
        subtree_root = pt.composites.Parallel(name=subtree_name, policy=policy)
    else:
        raise ValueError(f"composite type '{composite_type}' is not handled")

    for child_data in subtree_data[FR_CHILDREN]:
        if FR_CHILDREN in child_data:
            # recursive call TODO: confirm/check no cycle
            subtree_root.add_child(create_subtree_behaviours(child_data, event_loop))
            continue

        action = load_python_event_action(child_data, event_loop)
        subtree_root.add_child(action)

    return subtree_root


def create_bt_el_from_data(bt_root_data: dict) -> Tuple[EventLoop, pt.composites.Composite]:
    bt_root_name = bt_root_data[FR_NAME]
    if FR_EL not in bt_root_data:
        raise ValueError(f"key '{FR_EL}' not in data of behaviour tree '{bt_root_name}'")
    event_loop = create_event_loop_from_data(bt_root_data[FR_EL])

    # recursively create behaviour tree
    bt_root_node = create_subtree_behaviours(bt_root_data[FR_SUBTREE], event_loop)

    return event_loop, bt_root_node


def create_bt_from_graph(graph: rdflib.Graph, bt_name: str = None) -> List[Tuple]:
    bt_model = query_graph(graph, BEHAVIOUR_TREE_QUERY)
    bt_model_framed = jsonld.frame(bt_model, BEHAVIOUR_TREE_FRAME)

    if FR_DATA not in bt_model_framed:
        # single BT root
        return [create_bt_el_from_data(bt_model_framed)]

    # multiple BT roots
    els_and_bts = []
    for root_data in bt_model_framed[FR_DATA]:
        root_name = root_data[FR_NAME]
        if bt_name is not None and root_name != bt_name:
            # not the requested tree
            continue

        els_and_bts.append(create_bt_el_from_data(root_data))

    return els_and_bts
