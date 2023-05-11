import glob
import json
from os.path import join
from pyld import jsonld
import rdflib
from bdd_dsl.coordination import EventLoop
from bdd_dsl.metamodels import META_MODELs_PATH
from bdd_dsl.models import EVENT_LOOP_QUERY, EVENT_LOOP_FRAME


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


def frame_graph_with_file(model: dict, frame_file: str):
    with open(frame_file) as infile:
        frame_str = infile.read()
    frame_dict = json.loads(frame_str)
    return frame_model(model, frame_dict)


def create_event_loop_from_graph(graph: rdflib.Graph) -> list:
    model = query_graph_with_file(graph, EVENT_LOOP_QUERY)
    framed_model = frame_graph_with_file(model, EVENT_LOOP_FRAME)

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
