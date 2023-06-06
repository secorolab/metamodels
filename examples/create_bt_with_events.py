from os.path import join, dirname
import time
import py_trees as pt
from pprint import pprint
from bdd_dsl.json_utils import (
    load_metamodels,
    create_bt_from_graph,
)


PKG_ROOT = join(dirname(__file__), "..")
META_MODELs_PATH = join(PKG_ROOT, "metamodels")
MODELS_PATH = join(PKG_ROOT, "models")


def main():
    g = load_metamodels()
    g.parse(join(MODELS_PATH, "pickup-events.json"), format="json-ld")
    g.parse(join(MODELS_PATH, "pickup-behaviours.json"), format="json-ld")
    g.parse(join(MODELS_PATH, "pickup-dual-arm-behaviours.json"), format="json-ld")

    els_and_bts = create_bt_from_graph(g)
    for el, bt in els_and_bts:
        print(f"found behaviour tree '{bt.name}' associated with event loop '{el.id}'")
        pprint(el.event_data)

    selected_el, selected_bt_root = els_and_bts[0]
    pt.display.render_dot_tree(selected_bt_root)
    selected_bt = pt.trees.BehaviourTree(selected_bt_root)

    while True:
        try:
            selected_bt.tick()
            selected_el.reconfigure()
            time.sleep(0.01)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
