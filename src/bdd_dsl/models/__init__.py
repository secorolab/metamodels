from os.path import dirname, join


MODELs_PATH = dirname(__file__)
EVENT_LOOP_QUERY = join(MODELs_PATH, "queries", "get-event-loop.rq")
EVENT_LOOP_FRAME = join(MODELs_PATH, "frames", "event-loop-frame.json")
