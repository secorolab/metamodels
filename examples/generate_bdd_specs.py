from os.path import join, dirname
from bdd_dsl.json_utils import load_metamodels, query_graph
from pyld import jsonld
from bdd_dsl.models.queries import BDD_QUERY
from bdd_dsl.models.frames import BDD_FRAME
from pprint import pprint


PKG_ROOT = join(dirname(__file__), "..")
MODELS_PATH = join(PKG_ROOT, "models")


def main():
    g = load_metamodels()
    g.parse(join(MODELS_PATH, "bdd-templates-pick.json"), format="json-ld")
    g.parse(join(MODELS_PATH, "bdd-pick.json"), format="json-ld")
    g.parse(join(MODELS_PATH, "brsu-robots.json"), format="json-ld")
    g.parse(join(MODELS_PATH, "brsu-env.json"), format="json-ld")

    bdd_result = query_graph(g, BDD_QUERY)
    pprint(bdd_result)
    model_framed = jsonld.frame(bdd_result, BDD_FRAME)
    pprint(model_framed)


if __name__ == "__main__":
    main()
