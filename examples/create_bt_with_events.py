from os.path import join, dirname
import time
import py_trees
from pprint import pprint
from bdd_dsl.models.queries import BEHAVIOUR_TREE_QUERY
from bdd_dsl.models.frames import BEHAVIOUR_TREE_FRAME
from bdd_dsl.json_utils import \
    create_event_loop_from_graph, load_metamodels, query_graph, frame_model, create_subtree_behaviours


PKG_ROOT = join(dirname(__file__), "..")
META_MODELs_PATH = join(PKG_ROOT, "metamodels")
MODELS_PATH = join(PKG_ROOT, "models")


def main():
    g = load_metamodels()
    g.parse(join(MODELS_PATH, "pickup-events.json"), format="json-ld")
    # g.parse(join(MODELS_PATH, "pickup-behaviours.json"), format="json-ld")
    g.parse(join(MODELS_PATH, "pickup-dual-arm-behaviours.json"), format="json-ld")
    # pprint(list(g))

    event_loops = create_event_loop_from_graph(g)
    for el in event_loops:
        pprint(el.event_data)

    bt_model = query_graph(g, BEHAVIOUR_TREE_QUERY)
    # pprint(bt_model)
    bt_model_framed = frame_model(bt_model, BEHAVIOUR_TREE_FRAME)
    pprint(bt_model_framed)

    if "data" not in bt_model_framed:
        subtree_roots = [bt_model_framed]
    else:
        subtree_roots = bt_model_framed["data"]

    roots = []
    for root in subtree_roots:
        root_name = root["name"]
        if root["has_parent"]:
            print(f"skipping '{ root_name }'")
            continue
        # root tree
        print(f"creating behaviour tree for root '{root_name}'")

        root_node = create_subtree_behaviours(root, event_loops[0])
        roots.append(root_node)

    py_trees.display.render_dot_tree(roots[0])
    behaviour_tree = py_trees.trees.BehaviourTree(roots[0])
    while True:
        try:
            behaviour_tree.tick()
            event_loops[0].reconfigure()
            time.sleep(0.05)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()
