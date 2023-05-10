from os.path import join, dirname
import unittest
import rdflib
from bdd_dsl.coordination import EventLoop
from bdd_dsl.util import query_graph_with_file, frame_graph_with_file


PKG_ROOT = join(dirname(__file__), "..")
META_MODELs_PATH = join(PKG_ROOT, "metamodels")
MODELS_PATH = join(PKG_ROOT, "models")


class TestEventLoop(unittest.TestCase):

    def test_event_loop_from_json(self):
        g = rdflib.Graph()
        g.parse(join(META_MODELs_PATH, "coordination.json"), format="json-ld")
        g.parse(join(MODELS_PATH, "pickup-events.json"), format="json-ld")

        model = query_graph_with_file(g, join(MODELS_PATH, "queries", "get-event-loop.rq"))
        framed_model = frame_graph_with_file(model, join(MODELS_PATH, "frames", "event-loop-frame.json"))

        def test_event_loop(el: EventLoop, event_names: list):
            for e_name in event_names:
                self.assertFalse(el.consume(e_name))
                el.produce(e_name)

            # trigger event value update
            el.reconfigure()

            for e_name in event_names:
                self.assertTrue(el.consume(e_name))

        if "data" in framed_model:
            # multiple matches
            for event_loop_data in framed_model["data"]:
                event_names = [event["name"] for event in event_loop_data["events"]]
                el = EventLoop(event_loop_data["name"], event_names)
                test_event_loop(el, event_names)
        else:
            event_names = [event["name"] for event in framed_model["events"]]
            el = EventLoop(framed_model["name"], event_names)
            test_event_loop(el, event_names)


if __name__ == '__main__':
    unittest.main()
