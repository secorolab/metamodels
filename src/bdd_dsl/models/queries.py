Q_URI_TRANS = "https://my.url/transformations/"
Q_URI_MM_CRDN = "https://my.url/metamodels/coordination#"
Q_URI_MM_BT = "https://my.url/metamodels/coordination/behaviour-tree#"
Q_URI_MM_PY = "https://my.url/metamodels/languages/python#"
Q_URI_M_CRDN = "https://my.url/models/coordination/"

# transformation concepts and relations
Q_PREFIX_TRANS = "trans"
Q_HAS_EVENT = f"{Q_PREFIX_TRANS}:has-event"
Q_HAS_EL_CONN = f"{Q_PREFIX_TRANS}:has-el-conn"
Q_HAS_ROOT = f"{Q_PREFIX_TRANS}:has-root"
Q_HAS_SUBTREE = f"{Q_PREFIX_TRANS}:has-subtree"
Q_HAS_PARENT = f"{Q_PREFIX_TRANS}:has-parent"
Q_HAS_CHILD = f"{Q_PREFIX_TRANS}:has-child"
Q_HAS_TYPE = f"{Q_PREFIX_TRANS}:has-type"
Q_HAS_START_E = f"{Q_PREFIX_TRANS}:has-start-event"
Q_HAS_END_E = f"{Q_PREFIX_TRANS}:has-end-event"
Q_IMPL_MODULE = f"{Q_PREFIX_TRANS}:impl-module"
Q_IMPL_CLASS = f"{Q_PREFIX_TRANS}:impl-class"
Q_IMPL_ARG_NAME = f"{Q_PREFIX_TRANS}:impl-arg-name"
Q_IMPL_ARG_VALUE = f"{Q_PREFIX_TRANS}:impl-arg-value"

# coordination concepts & relations
Q_PREFIX_CRDN = "crdn"
Q_CRDN_EVENT_LOOP = f"{Q_PREFIX_CRDN}:EventLoop"
Q_CRDN_EVENT_LOOP_CONN = f"{Q_PREFIX_CRDN}:EventLoopConn"
Q_CRDN_HAS_EL_CONN = f"{Q_PREFIX_CRDN}:event-loop-connection"
Q_CRDN_OF_EL = f"{Q_PREFIX_CRDN}:event-loop"
Q_CRDN_HAS_EVENT = f"{Q_PREFIX_CRDN}:has-event"

# behaviour tree concepts & relations
Q_PREFIX_BT = "bt"
Q_BT_WITH_EVENTS = f"{Q_PREFIX_BT}:BehaviourTreeWithEvents"
Q_BT_USES_IMPL = f"{Q_PREFIX_BT}:uses-implementation"
Q_BT_SEQUENCE = f"{Q_PREFIX_BT}:Sequence"
Q_BT_PARALLEL = f"{Q_PREFIX_BT}:Parallel"
Q_BT_ACTION = f"{Q_PREFIX_BT}:Action"
Q_BT_ACTION_IMPL = f"{Q_PREFIX_BT}:PythonActionImpl"
Q_BT_ACTION_SUBTREE = f"{Q_PREFIX_BT}:ActionSubtree"
Q_BT_SUBTREE_IMPL = f"{Q_PREFIX_BT}:SubtreeImpl"
Q_BT_OF_SUBTREE = f"{Q_PREFIX_BT}:of-subtree"
Q_BT_SUBROOT = f"{Q_PREFIX_BT}:subroot"
Q_BT_PARENT = f"{Q_PREFIX_BT}:parent"
Q_BT_CHILDREN = f"{Q_PREFIX_BT}:has-child"
Q_BT_OF_ACTION = f"{Q_PREFIX_BT}:of-action"
Q_BT_START_E = f"{Q_PREFIX_BT}:start-event"
Q_BT_END_E = f"{Q_PREFIX_BT}:end-event"

# Python concepts & relations
Q_PREFIX_PY = "py"
Q_PY_MODULE = f"{Q_PREFIX_PY}:module"
Q_PY_CLASS = f"{Q_PREFIX_PY}:class-name"
Q_PY_ARG_NAME = f"{Q_PREFIX_PY}:ArgName"
Q_PY_ARG_VAL = f"{Q_PREFIX_PY}:ArgValue"

# Query for event loops from graph
EVENT_LOOP_QUERY = f"""
PREFIX {Q_PREFIX_CRDN}: <{Q_URI_MM_CRDN}>
PREFIX {Q_PREFIX_TRANS}: <{Q_URI_TRANS}>

CONSTRUCT {{
    ?eventLoopConn {Q_HAS_EVENT} ?event .
}}
WHERE {{
    ?eventLoopConn a {Q_CRDN_EVENT_LOOP_CONN} ;
        {Q_CRDN_OF_EL} ?eventLoop ;
        {Q_CRDN_HAS_EVENT} ?event .
    ?eventLoop a {Q_CRDN_EVENT_LOOP} .
}}
"""

BEHAVIOUR_TREE_QUERY = f"""
PREFIX {Q_PREFIX_BT}: <{Q_URI_MM_BT}>
PREFIX {Q_PREFIX_PY}: <{Q_URI_MM_PY}>
PREFIX {Q_PREFIX_TRANS}: <{Q_URI_TRANS}>

CONSTRUCT {{
    ?rootImpl
        {Q_HAS_EL_CONN} ?elConn ;
        {Q_HAS_SUBTREE} ?rootChildImpl .
    ?subtreeImpl
        {Q_HAS_CHILD} ?childImpl ;
        {Q_HAS_TYPE} ?compositeType .
    ?childImpl
        {Q_HAS_START_E} ?startEvent ;
        {Q_HAS_END_E} ?endEvent ;
        {Q_IMPL_MODULE} ?implModule ;
        {Q_IMPL_CLASS} ?implClass ;
        {Q_IMPL_ARG_NAME} ?implArgNames ;
        {Q_IMPL_ARG_VALUE} ?implArgValues .
    ?elConn {Q_HAS_EVENT} ?event .
}}
WHERE {{
    ?subtreeImpl a {Q_BT_SUBTREE_IMPL} ;
        {Q_BT_USES_IMPL} ?childImpl ;
        {Q_BT_OF_SUBTREE} ?subtree .
    ?subtree a {Q_BT_ACTION_SUBTREE} ;
        {Q_BT_PARENT} ?subtreeRootAction ;
        {Q_BT_SUBROOT} ?subtreeComposite .
    ?subtreeComposite a ?compositeType ;
        {Q_BT_CHILDREN} ?childRootAction .

    OPTIONAL {{
        ?subtreeImpl ^{Q_BT_USES_IMPL} ?rootImpl .
        ?subtree {Q_BT_PARENT} ?root ;
            {Q_BT_SUBROOT} ?rootComposite .
        ?rootImpl a {Q_BT_WITH_EVENTS} ;
            {Q_CRDN_HAS_EL_CONN} ?elConn ;
            {Q_BT_USES_IMPL} ?rootChildImpl .
        ?elConn a {Q_CRDN_EVENT_LOOP_CONN} ;
            {Q_CRDN_HAS_EVENT} ?event .
    }}

    OPTIONAL {{
        ?childImpl a {Q_BT_SUBTREE_IMPL} ;
            {Q_BT_OF_SUBTREE} ?childSubtree .
        ?childSubtree a {Q_BT_ACTION_SUBTREE} ;
            {Q_BT_PARENT} ?childRootAction ;
            {Q_BT_SUBROOT} ?childComposite .
    }}

    OPTIONAL {{
        ?childImpl a {Q_BT_ACTION_IMPL} ;
            {Q_BT_OF_ACTION} ?childAction ;
            {Q_PY_MODULE} ?implModule ;
            {Q_PY_CLASS} ?implClass .
        ?childAction a {Q_BT_ACTION} ;
            ^{Q_BT_OF_ACTION} / {Q_BT_START_E} ?startEvent ;
            ^{Q_BT_OF_ACTION} / {Q_BT_END_E} ?endEvent .
        OPTIONAL {{
            ?childImpl {Q_PY_ARG_NAME} ?implArgNames ;
                {Q_PY_ARG_VAL} ?implArgValues .
        }}
    }}

}}
"""
