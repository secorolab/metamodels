EVENT_LOOP_FRAME = {
    "@context": {
        "@base": "https://my.url/models/coordination/",
        "crdn": "https://my.url/metamodels/coordination#",
        "trans": "https://my.url/transformations/",
        "data": "@graph",
        "name": "@id",
        "events": "trans:has-events"
    },
    "data": {
        "@explicit": True,
        "events": {}
    }
}

BEHAVIOUR_TREE_FRAME = {
    "@context": {
        "@base": "https://my.url/models/coordination/",
        "bt": "https://my.url/metamodels/behaviour-tree#",
        "trans": "https://my.url/transformations/",
        "data": "@graph",
        "name": "@id",
        "subtree": "trans:has-subtree",
        "type": "trans:has-type",
        "children": "trans:has-children",
        "start_event": "trans:has-start-event",
        "end_event": "trans:has-end-event"
    },
    "data": {
        "subtree": {}
    }
}
