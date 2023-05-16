Q_URI_TRANS = "https://my.url/transformations/"
Q_URI_MM_COORD = "https://my.url/metamodels/coordination#"
Q_URI_MM_BT = "https://my.url/metamodels/behaviour-tree#"
Q_URI_MM_PY = "https://my.url/metamodels/languages/python#"

# transformation relations
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

# coordination relations
Q_PREFIX_CRDN = "crdn"

# behaviour tree relations
Q_PREFIX_BT = "bt"
Q_BT_SEQUENCE = f"{Q_PREFIX_BT}:Sequence"
Q_BT_PARALLEL = f"{Q_PREFIX_BT}:Parallel"
Q_BT_ACTION = f"{Q_PREFIX_BT}:Action"

# Python relations
Q_PREFIX_PY = "py"

EVENT_LOOP_QUERY = f"""
PREFIX {Q_PREFIX_CRDN}: <{Q_URI_MM_COORD}>
PREFIX {Q_PREFIX_TRANS}: <{Q_URI_TRANS}>

CONSTRUCT {{
    ?eventLoop {Q_HAS_EVENTS} ?event .
}}
WHERE {{
    ?eventLoop a {Q_PREFIX_CRDN}:EventLoop ;
        ^{Q_PREFIX_CRDN}:event-loop / {Q_PREFIX_CRDN}:events ?event .
}}
"""

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
    ?subtree a {Q_PREFIX_BT}:ActionSubtree ;
        {Q_PREFIX_BT}:parent ?root ;
        {Q_PREFIX_BT}:subroot ?childRoot .
    OPTIONAL {{
        ?root ^{Q_PREFIX_BT}:children ?composite .
        ?composite ^{Q_PREFIX_BT}:subroot / {Q_PREFIX_BT}:parent ?rootParent .
    }}
    bind ( bound(?rootParent) as ?hasParent )

    ?childRoot {Q_PREFIX_BT}:children ?child ;
               a ?childRootType .
    ?child a ?childType .
    OPTIONAL {{
        ?child a {Q_PREFIX_BT}:Action ;
            ^{Q_PREFIX_BT}:of-action / {Q_PREFIX_BT}:start-event ?startEvent ;
            ^{Q_PREFIX_BT}:of-action / {Q_PREFIX_BT}:end-event ?endEvent ;
            ^{Q_PREFIX_BT}:of-action / {Q_PREFIX_PY}:module ?implModule ;
            ^{Q_PREFIX_BT}:of-action / {Q_PREFIX_PY}:class ?implClass .
        OPTIONAL {{
            ?child ^{Q_PREFIX_BT}:of-action / {Q_PREFIX_PY}:ArgName ?implArgNames ;
                   ^{Q_PREFIX_BT}:of-action / {Q_PREFIX_PY}:ArgValue ?implArgValues .
        }}
    }}
}}
"""
