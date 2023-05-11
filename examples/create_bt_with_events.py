from os.path import join, dirname
import time
import py_trees
from pprint import pprint
from bdd_dsl.util import create_event_loop_from_graph, load_metamodels, query_graph, frame_model
from bdd_dsl.behaviours.mockup import Heartbeat


PKG_ROOT = join(dirname(__file__), "..")
META_MODELs_PATH = join(PKG_ROOT, "metamodels")
MODELS_PATH = join(PKG_ROOT, "models")
BT_QUERY = """
PREFIX bt: <https://my.url/metamodels/behaviour-tree#>
PREFIX trans: <https://my.url/transformations/>

CONSTRUCT {
    ?root trans:has-subtree ?childRoot .
    ?childRoot trans:has-children ?child .
    ?child trans:has-start-event ?startEvent .
    ?child trans:has-end-event ?endEvent .
}
WHERE {
    ?subtree a bt:ActionSubtree ;
        bt:parent ?root ;
        bt:subroot ?childRoot .
    ?childRoot bt:children ?child .
    ?child a bt:Action ;
        ^bt:of-action / bt:start-event ?startEvent ;
        ^bt:of-action / bt:end-event ?endEvent .
}
"""
BT_FRAME = {
    "@context": {
        "@base": "https://my.url/models/coordination/",
        "bt": "https://my.url/metamodels/behaviour-tree#",
        "trans": "https://my.url/transformations/",
        "data": "@graph",
        "name": "@id",
        "subtree": "trans:has-subtree",
        "children": "trans:has-children",
        "start_event": "trans:has-start-event",
        "end_event": "trans:has-end-event"
    },
    "data": {
        "subtree": {}
    }
}


def main():
    g = load_metamodels()
    g.parse(join(MODELS_PATH, "pickup-events.json"), format="json-ld")
    g.parse(join(MODELS_PATH, "pickup-behaviours.json"), format="json-ld")
    # pprint(list(g))

    event_loops = create_event_loop_from_graph(g)
    for el in event_loops:
        pprint(el.event_data)

    bt_model = query_graph(g, BT_QUERY)
    # pprint(bt_model)
    bt_model_framed = frame_model(bt_model, BT_FRAME)
    pprint(bt_model_framed)

    root_name = bt_model_framed["subtree"]["name"]
    root = py_trees.composites.Sequence(name=root_name, memory=True)
    for child_data in bt_model_framed["subtree"]["children"]:
        action = Heartbeat(child_data["name"], event_loops[0],
                           child_data["start_event"]["name"],
                           child_data["end_event"]["name"])
        root.add_child(action)

    # py_trees.display.render_dot_tree(root)
    behaviour_tree = py_trees.trees.BehaviourTree(root)
    while True:
        try:
            behaviour_tree.tick()
            event_loops[0].reconfigure()
            time.sleep(0.05)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()
