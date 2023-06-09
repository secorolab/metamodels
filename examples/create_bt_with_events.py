from os.path import join, dirname
import py_trees as pt
from pprint import pprint
from bdd_dsl.utils.json import (
    load_metamodels,
    create_bt_from_graph,
)
from bdd_dsl.behaviours.robosuite import SimulatedScenario


PKG_ROOT = join(dirname(__file__), "..")
MODELS_PATH = join(PKG_ROOT, "models")


def main():
    g = load_metamodels()
    g.parse(join(MODELS_PATH, "coordination", "pickup-events.json"), format="json-ld")
    g.parse(join(MODELS_PATH, "coordination", "pickup-behaviours.json"), format="json-ld")
    g.parse(join(MODELS_PATH, "coordination", "pickup-dual-arm-behaviours.json"), format="json-ld")

    els_and_bts = create_bt_from_graph(g)
    for el, bt in els_and_bts:
        print(f"found behaviour tree '{bt.name}' associated with event loop '{el.id}'")
        pprint(el.event_data)

    selected_el, selected_bt_root = els_and_bts[0]
    pt.display.render_dot_tree(selected_bt_root)

    pickup_scenario = SimulatedScenario(
        g, env_name="PickPlace", robots=["Panda"], bt_root_name="bt/pickup-single-arm-rs"
    )
    pickup_scenario.setup(target_object="Milk", timeout=15)

    while True:
        try:
            pickup_scenario.step()
        except KeyboardInterrupt:
            pickup_scenario.interrupt()
            break


if __name__ == "__main__":
    main()
