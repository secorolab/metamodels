from os.path import join, dirname
from bdd_dsl.utils.json import load_metamodels, process_bdd_us_from_graph
from pprint import pprint


PKG_ROOT = join(dirname(__file__), "..")
MODELS_PATH = join(PKG_ROOT, "models")


def main():
    g = load_metamodels()
    g.parse(join(MODELS_PATH, "acceptance-criteria", "bdd-templates-pick.json"), format="json-ld")
    g.parse(join(MODELS_PATH, "acceptance-criteria", "bdd-pick.json"), format="json-ld")
    g.parse(join(MODELS_PATH, "coordination", "pickup-events.json"), format="json-ld")
    g.parse(join(MODELS_PATH, "brsu-robots.json"), format="json-ld")
    g.parse(join(MODELS_PATH, "brsu-env.json"), format="json-ld")

    processed_bdd_data = process_bdd_us_from_graph(g)
    pprint(processed_bdd_data)


if __name__ == "__main__":
    main()
