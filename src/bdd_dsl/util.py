import json
import rdflib
from pyld import jsonld


def query_graph(graph: rdflib.Graph, query_str: str):
    res = graph.query(query_str)
    res_json = json.loads(res.serialize(format="json-ld"))
    transformed_model = {"@graph": res_json}
    return transformed_model


def query_graph_with_file(graph: rdflib.Graph, query_file: str):
    with open(query_file) as infile:
        query_str = infile.read()
    return query_graph(graph, query_str)


def frame_model(model: dict, frame_str: str):
    frame = json.loads(frame_str)
    model_framed = jsonld.frame(model, frame)
    return model_framed


def frame_graph_with_file(model: dict, frame_file: str):
    # load query and frame files
    with open(frame_file) as infile:
        frame_str = infile.read()
    return frame_model(model, frame_str)
