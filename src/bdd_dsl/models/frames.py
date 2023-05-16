from bdd_dsl.models.queries import \
    Q_URI_MM_COORD, Q_URI_MM_BT, Q_URI_TRANS, Q_PREFIX_TRANS, Q_HAS_EVENTS, Q_HAS_SUBTREE, \
    Q_HAS_TYPE, Q_HAS_CHILDREN, Q_HAS_PARENT, Q_HAS_START_E, Q_HAS_END_E, Q_IMPL_MODULE, \
    Q_IMPL_CLASS, Q_IMPL_ARG_NAMES, Q_IMPL_ARG_VALUES, Q_PREFIX_CRDN, Q_PREFIX_BT


FR_NAME = "name"
FR_DATA = "data"
FR_EVENTS = "events"
FR_SUBTREE = "subtree"
FR_TYPE = "type"
FR_CHILDREN = "children"
FR_HAS_PARENT = "has_parent"
FR_START_E = "start_event"
FR_END_E = "end_event"
FR_IMPL_MODULE = "impl_module"
FR_IMPL_CLASS = "impl_class"
FR_IMPL_ARG_NAMES = "impl_arg_names"
FR_IMPL_ARG_VALS = "impl_arg_values"

EVENT_LOOP_FRAME = {
    "@context": {
        "@base": "https://my.url/models/coordination/",
        Q_PREFIX_CRDN: Q_URI_MM_COORD,
        Q_PREFIX_TRANS: Q_URI_TRANS,
        FR_DATA: "@graph",
        FR_NAME: "@id",
        FR_EVENTS: Q_HAS_EVENTS
    },
    FR_DATA: {
        "@explicit": True,
        FR_EVENTS: {}
    }
}

BEHAVIOUR_TREE_FRAME = {
    "@context": {
        "@base": "https://my.url/models/coordination/",
        Q_PREFIX_BT: Q_URI_MM_BT,
        Q_PREFIX_TRANS: Q_URI_TRANS,
        FR_DATA: "@graph",
        FR_NAME: "@id",
        FR_SUBTREE: Q_HAS_SUBTREE,
        FR_TYPE: Q_HAS_TYPE,
        FR_CHILDREN: Q_HAS_CHILDREN,
        FR_HAS_PARENT: Q_HAS_PARENT,
        FR_START_E: Q_HAS_START_E,
        FR_END_E: Q_HAS_END_E,
        FR_IMPL_MODULE: Q_IMPL_MODULE,
        FR_IMPL_CLASS: Q_IMPL_CLASS,
        FR_IMPL_ARG_NAMES: Q_IMPL_ARG_NAMES,
        FR_IMPL_ARG_VALS: Q_IMPL_ARG_VALUES
    },
    FR_DATA: {
        FR_SUBTREE: {}
    }
}
