EVENT_LOOP_QUERY = """
PREFIX crdn: <https://my.url/metamodels/coordination#>
PREFIX trans: <https://my.url/transformations/>

CONSTRUCT {
    ?eventLoop trans:has-events ?event .
}
WHERE {
    ?eventLoop a crdn:EventLoop ;
        ^crdn:event-loop / crdn:events ?event .
}
"""

BEHAVIOUR_TREE_QUERY = """
PREFIX bt: <https://my.url/metamodels/behaviour-tree#>
PREFIX trans: <https://my.url/transformations/>

CONSTRUCT {
    ?root trans:has-subtree ?childRoot .
    ?root trans:has-parent ?hasParent .
    ?childRoot trans:has-children ?child ;
               trans:has-type ?childRootType .
    ?child trans:has-type ?childType ;
           trans:has-start-event ?startEvent ;
           trans:has-end-event ?endEvent .
}
WHERE {
    ?subtree a bt:ActionSubtree ;
        bt:parent ?root ;
        bt:subroot ?childRoot .
    OPTIONAL {
        ?root ^bt:children ?composite .
        ?composite ^bt:subroot / bt:parent ?rootParent .
    }
    bind ( bound(?rootParent) as ?hasParent )

    ?childRoot bt:children ?child ;
               a ?childRootType .
    ?child a ?childType .
    OPTIONAL {
        ?child a bt:Action ;
            ^bt:of-action / bt:start-event ?startEvent ;
            ^bt:of-action / bt:end-event ?endEvent .
    }
}
"""
