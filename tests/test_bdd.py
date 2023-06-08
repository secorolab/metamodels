from os.path import join, dirname
import unittest
from bdd_dsl.json_utils import load_metamodels, query_graph
from bdd_dsl.models.queries import BDD_QUERY
from bdd_dsl.models.frames import BDD_FRAME, FR_DATA, FR_CRITERIA
from pyld import jsonld


PKG_ROOT = join(dirname(__file__), "..")
META_MODELs_PATH = join(PKG_ROOT, "metamodels")
MODELS_PATH = join(PKG_ROOT, "models")


class BDD(unittest.TestCase):
    def setUp(self):
        self.graph = load_metamodels()
        self.graph.parse(
            join(MODELS_PATH, "acceptance-criteria", "bdd-templates-pick.json"), format="json-ld"
        )
        self.graph.parse(
            join(MODELS_PATH, "acceptance-criteria", "bdd-pick.json"), format="json-ld"
        )
        self.graph.parse(join(MODELS_PATH, "brsu-robots.json"), format="json-ld")
        self.graph.parse(join(MODELS_PATH, "brsu-env.json"), format="json-ld")

    def test_bdd(self):
        bdd_result = query_graph(self.graph, BDD_QUERY)
        model_framed = jsonld.frame(bdd_result, BDD_FRAME)
        self.assertTrue(FR_DATA in model_framed or FR_CRITERIA in model_framed)


if __name__ == "__main__":
    unittest.main()
