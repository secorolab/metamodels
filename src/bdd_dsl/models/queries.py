Q_URI_TRANS = "https://my.url/transformations/"
Q_URI_MM_CRDN = "https://my.url/metamodels/coordination#"
Q_URI_MM_BT = "https://my.url/metamodels/coordination/behaviour-tree#"
Q_URI_MM_PY = "https://my.url/metamodels/languages/python#"
Q_URI_M_CRDN = "https://my.url/models/coordination/"

# transformation concepts and relations
Q_PREFIX_TRANS = "trans"
Q_HAS_EVENTS = f"{Q_PREFIX_TRANS}:has-events"
Q_HAS_SUBTREE = f"{Q_PREFIX_TRANS}:has-subtree"
Q_HAS_PARENT = f"{Q_PREFIX_TRANS}:has-parent"
Q_HAS_CHILDREN = f"{Q_PREFIX_TRANS}:has-children"
Q_HAS_TYPE = f"{Q_PREFIX_TRANS}:has-type"
Q_HAS_START_E = f"{Q_PREFIX_TRANS}:has-start-event"
Q_HAS_END_E = f"{Q_PREFIX_TRANS}:has-end-event"
Q_IMPL_MODULE = f"{Q_PREFIX_TRANS}:impl-module"
Q_IMPL_CLASS = f"{Q_PREFIX_TRANS}:impl-class"
Q_IMPL_ARG_NAMES = f"{Q_PREFIX_TRANS}:impl-arg-names"
Q_IMPL_ARG_VALUES = f"{Q_PREFIX_TRANS}:impl-arg-values"

# coordination concepts & relations
Q_PREFIX_CRDN = "crdn"
Q_CRDN_EVENT_LOOP = f"{Q_PREFIX_CRDN}:EventLoop"
Q_CRDN_HAS_EL = f"{Q_PREFIX_CRDN}:event-loop"
Q_CRDN_EVENTS = f"{Q_PREFIX_CRDN}:events"

# behaviour tree concepts & relations
Q_PREFIX_BT = "bt"
Q_BT_SEQUENCE = f"{Q_PREFIX_BT}:Sequence"
Q_BT_PARALLEL = f"{Q_PREFIX_BT}:Parallel"
Q_BT_ACTION = f"{Q_PREFIX_BT}:Action"
Q_BT_ACTION_SUBTREE = f"{Q_PREFIX_BT}:ActionSubtree"
Q_BT_SUBROOT = f"{Q_PREFIX_BT}:subroot"
Q_BT_PARENT = f"{Q_PREFIX_BT}:parent"
Q_BT_CHILDREN = f"{Q_PREFIX_BT}:children"
Q_BT_OF_ACTION = f"{Q_PREFIX_BT}:of-action"
Q_BT_START_E = f"{Q_PREFIX_BT}:start-event"
Q_BT_END_E = f"{Q_PREFIX_BT}:end-event"

# Python concepts & relations
Q_PREFIX_PY = "py"
Q_PY_MODULE = f"{Q_PREFIX_PY}:module"
Q_PY_CLASS = f"{Q_PREFIX_PY}:class"
Q_PY_ARG_NAME = f"{Q_PREFIX_PY}:ArgName"
Q_PY_ARG_VAL = f"{Q_PREFIX_PY}:ArgValue"

# Query for event loops from graph
EVENT_LOOP_QUERY = f"""
PREFIX {Q_PREFIX_CRDN}: <{Q_URI_MM_CRDN}>
PREFIX {Q_PREFIX_TRANS}: <{Q_URI_TRANS}>

CONSTRUCT {{
    ?eventLoop {Q_HAS_EVENTS} ?event .
}}
WHERE {{
    ?eventLoop a {Q_CRDN_EVENT_LOOP} ;
        ^{Q_CRDN_HAS_EL} / {Q_CRDN_EVENTS} ?event .
}}
"""

# Query for behaviour trees from graph
BEHAVIOUR_TREE_QUERY = f"""
PREFIX {Q_PREFIX_BT}: <{Q_URI_MM_BT}>
PREFIX {Q_PREFIX_PY}: <{Q_URI_MM_PY}>
PREFIX {Q_PREFIX_TRANS}: <{Q_URI_TRANS}>

CONSTRUCT {{
    ?root {Q_HAS_SUBTREE} ?childRoot .
    ?root {Q_HAS_PARENT} ?hasParent .
    ?childRoot {Q_HAS_CHILDREN} ?child ;
               {Q_HAS_TYPE} ?childRootType .
    ?child {Q_HAS_TYPE} ?childType ;
           {Q_HAS_START_E} ?startEvent ;
           {Q_HAS_END_E} ?endEvent ;
           {Q_IMPL_MODULE} ?implModule ;
           {Q_IMPL_CLASS} ?implClass ;
           {Q_IMPL_ARG_NAMES} ?implArgNames ;
           {Q_IMPL_ARG_VALUES} ?implArgValues .
}}
WHERE {{
    ?subtree a {Q_BT_ACTION_SUBTREE} ;
        {Q_BT_PARENT} ?root ;
        {Q_BT_SUBROOT} ?childRoot .
    OPTIONAL {{
        ?root ^{Q_BT_CHILDREN} ?composite .
        ?composite ^{Q_BT_SUBROOT} / {Q_BT_PARENT} ?rootParent .
    }}
    bind ( bound(?rootParent) as ?hasParent )

    ?childRoot {Q_BT_CHILDREN} ?child ;
               a ?childRootType .
    ?child a ?childType .
    OPTIONAL {{
        ?child a {Q_BT_ACTION} ;
            ^{Q_BT_OF_ACTION} / {Q_BT_START_E} ?startEvent ;
            ^{Q_BT_OF_ACTION} / {Q_BT_END_E} ?endEvent ;
            ^{Q_BT_OF_ACTION} / {Q_PY_MODULE} ?implModule ;
            ^{Q_BT_OF_ACTION} / {Q_PY_CLASS} ?implClass .
        OPTIONAL {{
            ?child ^{Q_BT_OF_ACTION} / {Q_PY_ARG_NAME} ?implArgNames ;
                   ^{Q_BT_OF_ACTION} / {Q_PY_ARG_VAL} ?implArgValues .
        }}
    }}
}}
"""
