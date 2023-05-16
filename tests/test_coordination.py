from os.path import join, dirname
import unittest
from bdd_dsl.json_utils import load_metamodels, create_event_loop_from_graph, create_bt_from_graph


PKG_ROOT = join(dirname(__file__), "..")
META_MODELs_PATH = join(PKG_ROOT, "metamodels")
MODELS_PATH = join(PKG_ROOT, "models")


class NominalCoordination(unittest.TestCase):

    def setUp(self):
        self.graph = load_metamodels()
        self.event_loop_model_file = join(MODELS_PATH, "pickup-events.json")
        self.graph.parse(self.event_loop_model_file, format="json-ld")
        self.graph.parse(join(MODELS_PATH, "pickup-dual-arm-behaviours.json"), format="json-ld")
        self.event_loops = create_event_loop_from_graph(self.graph)

    def test_event_loop(self):
        self.assertTrue(len(self.event_loops) > 0, f"no event loop created from '{self.event_loop_model_file}'")

        for el in self.event_loops:
            self.assertTrue(len(el.event_data) > 0, f"no event created for '{el.id}'")

            for e_name in el.event_data:
                self.assertFalse(el.consume(e_name), f"event not initialized to 'False': {e_name}")
                el.produce(e_name)

            # trigger event value update
            el.reconfigure()

            for e_name in el.event_data:
                self.assertTrue(el.consume(e_name), f"event not set to 'True' after reconfigure: {e_name}")

    def test_behaviour_tree(self):
        _ = create_bt_from_graph(self.graph, self.event_loops[0])


if __name__ == '__main__':
    unittest.main()
