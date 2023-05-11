from os.path import join, dirname
import unittest
from bdd_dsl.json_utils import load_metamodels, create_event_loop_from_graph


PKG_ROOT = join(dirname(__file__), "..")
META_MODELs_PATH = join(PKG_ROOT, "metamodels")
MODELS_PATH = join(PKG_ROOT, "models")


class TestEventLoop(unittest.TestCase):

    def test_event_loop_from_json(self):
        g = load_metamodels()
        event_loop_model_file = join(MODELS_PATH, "pickup-events.json")
        g.parse(event_loop_model_file, format="json-ld")

        event_loops = create_event_loop_from_graph(g)
        self.assertTrue(len(event_loops) > 0, f"no event loop created from '{event_loop_model_file}'")

        for el in event_loops:
            self.assertTrue(len(el.event_data) > 0, f"no event created for '{el.id}'")

            for e_name in el.event_data:
                self.assertFalse(el.consume(e_name), f"event not initialized to 'False': {e_name}")
                el.produce(e_name)

            # trigger event value update
            el.reconfigure()

            for e_name in el.event_data:
                self.assertTrue(el.consume(e_name), f"event not set to 'True' after reconfigure: {e_name}")


if __name__ == '__main__':
    unittest.main()
