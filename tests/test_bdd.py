from os.path import join, dirname
import unittest
from bdd_dsl.json_utils import load_metamodels, process_bdd_us_from_graph
from bdd_dsl.models.frames import FR_CONN_DATA, FR_VAR_CONN_DICT


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
        bdd_result = process_bdd_us_from_graph(self.graph)
        self.assertIsInstance(bdd_result, list)
        for us_data in bdd_result:
            for var_name in us_data[FR_VAR_CONN_DICT]:
                self.assertIn(us_data[FR_VAR_CONN_DICT][var_name], us_data[FR_CONN_DATA])


if __name__ == "__main__":
    unittest.main()
