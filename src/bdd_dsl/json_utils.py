import glob
from importlib import import_module
import json
from os.path import join
from pyld import jsonld
import py_trees
import rdflib
from bdd_dsl.coordination import EventLoop
from bdd_dsl.metamodels import META_MODELs_PATH
from bdd_dsl.models.queries import EVENT_LOOP_QUERY, Q_BT_SEQUENCE, Q_BT_PARALLEL, Q_BT_ACTION
from bdd_dsl.models.frames import EVENT_LOOP_FRAME, \
    FR_NAME, FR_DATA, FR_EVENTS, FR_SUBTREE, FR_TYPE, FR_CHILDREN, FR_START_E, FR_END_E, \
    FR_IMPL_MODULE, FR_IMPL_CLASS, FR_IMPL_ARG_NAMES, FR_IMPL_ARG_VALS


def load_metamodels() -> rdflib.Graph:
    graph = rdflib.Graph()
    mm_files = glob.glob(join(META_MODELs_PATH, '*.json'))
    for mm_file in mm_files:
        graph.parse(mm_file, format="json-ld")
    return graph


def query_graph(graph: rdflib.Graph, query_str: str):
    res = graph.query(query_str)
    res_json = json.loads(res.serialize(format="json-ld"))
    transformed_model = {"@graph": res_json}
    return transformed_model


def query_graph_with_file(graph: rdflib.Graph, query_file: str):
    with open(query_file) as infile:
        query_str = infile.read()
    return query_graph(graph, query_str)


def frame_model(model: dict, frame_dict: dict):
    model_framed = jsonld.frame(model, frame_dict)
    return model_framed


def frame_model_with_file(model: dict, frame_file: str):
    with open(frame_file) as infile:
        frame_str = infile.read()
    frame_dict = json.loads(frame_str)
    return frame_model(model, frame_dict)


def create_event_loop_from_graph(graph: rdflib.Graph) -> list:
    model = query_graph(graph, EVENT_LOOP_QUERY)
    framed_model = frame_model(model, EVENT_LOOP_FRAME)

    if "data" in framed_model:
        # multiple matches
        event_loops = []
        for event_loop_data in framed_model[FR_DATA]:
            event_names = [event[FR_NAME] for event in event_loop_data[FR_EVENTS]]
            el = EventLoop(event_loop_data[FR_NAME], event_names)
            event_loops.append(el)
        return event_loops

    # single match
    event_names = [event[FR_NAME] for event in framed_model[FR_EVENTS]]
    el = EventLoop(framed_model[FR_NAME], event_names)
    return [el]


def load_python_event_action(node_data: dict, event_loop: EventLoop):
    if FR_NAME not in node_data:
        raise ValueError(f"'{FR_NAME}' not found in node data")
    node_name = node_data[FR_NAME]

    for k in [FR_START_E, FR_END_E, FR_IMPL_MODULE, FR_IMPL_CLASS]:
        if k in node_data:
            continue
        raise ValueError(f"required key '{k}' not found in data for action '{node_name}'")

    action_cls = getattr(import_module(node_data[FR_IMPL_MODULE]), node_data[FR_IMPL_CLASS])

    kwarg_dict = {}
    if FR_IMPL_ARG_NAMES in node_data and FR_IMPL_ARG_VALS in node_data:
        kwarg_names = node_data[FR_IMPL_ARG_NAMES]
        kwarg_vals = node_data[FR_IMPL_ARG_VALS]
        if len(kwarg_names) != len(kwarg_vals):
            raise ValueError(f"argument count mismatch for action '{node_name}")
        for i in range(len(kwarg_names)):
            kwarg_dict[kwarg_names[i]] = kwarg_vals[i]
    return action_cls(node_name, event_loop, node_data[FR_START_E][FR_NAME],
                      node_data[FR_END_E][FR_NAME], **kwarg_dict)


def create_subtree_behaviours(subtree_data: dict, event_loop: EventLoop) -> py_trees.composites.Composite:
    subtree_name = subtree_data[FR_NAME]
    composite_type = subtree_data[FR_SUBTREE][FR_TYPE][FR_NAME]
    subtree_root = None
    if composite_type == Q_BT_SEQUENCE:
        subtree_root = py_trees.composites.Sequence(name=subtree_name, memory=True)
    elif composite_type == Q_BT_PARALLEL:
        # TODO: annotate policy on graph
        policy = py_trees.common.ParallelPolicy.SuccessOnAll(synchronise=True)
        subtree_root = py_trees.composites.Parallel(name=subtree_name, policy=policy)
    else:
        raise ValueError(f"composite type '{composite_type}' is not handled")

    for child_data in subtree_data[FR_SUBTREE][FR_CHILDREN]:
        if FR_SUBTREE in child_data:
            # recursive call TODO: confirm/check no cycle
            subtree_root.add_child(create_subtree_behaviours(child_data, event_loop))
            continue

        child_type = child_data[FR_TYPE][FR_NAME]
        if child_type != Q_BT_ACTION:
            raise ValueError(f"child node of type '{child_type}' is not handled")

        action = load_python_event_action(child_data, event_loop)
        subtree_root.add_child(action)

    return subtree_root
