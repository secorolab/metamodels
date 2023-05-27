from os.path import join, dirname
import time
import py_trees
from pprint import pprint
from bdd_dsl.json_utils import create_event_loop_from_graph, load_metamodels, create_bt_from_graph


PKG_ROOT = join(dirname(__file__), "..")
META_MODELs_PATH = join(PKG_ROOT, "metamodels")
MODELS_PATH = join(PKG_ROOT, "models")


def main():
    g = load_metamodels()
    g.parse(join(MODELS_PATH, "pickup-events.json"), format="json-ld")
    g.parse(join(MODELS_PATH, "pickup-behaviours.json"), format="json-ld")
    g.parse(join(MODELS_PATH, "pickup-dual-arm-behaviours.json"), format="json-ld")

    event_loops = create_event_loop_from_graph(g)
    for el in event_loops:
        pprint(el.event_data)

    roots = create_bt_from_graph(g, event_loops[0])

    py_trees.display.render_dot_tree(roots[0])
    behaviour_tree = py_trees.trees.BehaviourTree(roots[0])
    while True:
        try:
            behaviour_tree.tick()
            event_loops[0].reconfigure()
            time.sleep(0.01)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()
