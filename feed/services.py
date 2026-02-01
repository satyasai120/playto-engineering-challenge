from collections import defaultdict

def build_comment_tree(comments):
    children_map = defaultdict(list)
    roots = []

    for c in comments:
        if c.parent_id:
            children_map[c.parent_id].append(c)
        else:
            roots.append(c)

    def attach(node):
        node.children_cached = children_map.get(node.id, [])
        for child in node.children_cached:
            attach(child)

    for r in roots:
        attach(r)

    return roots