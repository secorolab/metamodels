import glob
import json
from os.path import join
from pyld import jsonld
import py_trees
import rdflib
from bdd_dsl.behaviours.mockup import Heartbeat
from bdd_dsl.coordination import EventLoop
from bdd_dsl.metamodels import META_MODELs_PATH
from bdd_dsl.models.queries import EVENT_LOOP_QUERY
from bdd_dsl.models.frames import EVENT_LOOP_FRAME


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
        for event_loop_data in framed_model["data"]:
            event_names = [event["name"] for event in event_loop_data["events"]]
            el = EventLoop(event_loop_data["name"], event_names)
            event_loops.append(el)
        return event_loops

    # single match
    event_names = [event["name"] for event in framed_model["events"]]
    el = EventLoop(framed_model["name"], event_names)
    return [el]


def create_subtree_behaviours(subtree_data: dict, event_loop: EventLoop) -> py_trees.composites.Composite:
    subtree_name = subtree_data["name"]
    composite_type = subtree_data["subtree"]["type"]["name"]
    subtree_root = None
    if composite_type == "bt:Sequence":
        subtree_root = py_trees.composites.Sequence(name=subtree_name, memory=True)
    elif composite_type == "bt:Parallel":
        # TODO: annotate policy on graph
        policy = py_trees.common.ParallelPolicy.SuccessOnAll(synchronise=True)
        subtree_root = py_trees.composites.Parallel(name=subtree_name, policy=policy)
    else:
        raise ValueError(f"composite type '{composite_type}' is not handled")

    for child_data in subtree_data["subtree"]["children"]:
        if "subtree" in child_data:
            # recursive call TODO: confirm/check no cycle
            subtree_root.add_child(create_subtree_behaviours(child_data, event_loop))
            continue

        child_type = child_data["type"]["name"]
        if child_type != "bt:Action":
            raise ValueError(f"child node of type '{child_type}' is not handled")

        # TODO: load actual behaviour
        child_name = child_data["name"]
        if "start_event" not in child_data or "end_event" not in child_data:
            raise ValueError(f"start or end events not found for action '{child_name}'")
        action = Heartbeat(child_name, event_loop,
                           child_data["start_event"]["name"],
                           child_data["end_event"]["name"])
        subtree_root.add_child(action)

    return subtree_root
