from bisect import bisect_left, bisect_right


class BPlusNode:
    def __init__(self, leaf=False):
        self.keys = []
        self.children = []
        self.leaf = leaf
        self.next = None


class BPlusTree:
    """Simple integer-only B+ tree used as a toy database index."""

    def __init__(self, order=16):
        if order < 3:
            raise ValueError("order must be at least 3")
        self.root = BPlusNode(leaf=True)
        self.order = order

    def insert(self, key):
        root = self.root
        if len(root.keys) == self.order - 1:
            new_root = BPlusNode()
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root
        self._insert_non_full(self.root, key)

    def _insert_non_full(self, node, key):
        if node.leaf:
            i = bisect_left(node.keys, key)
            if i < len(node.keys) and node.keys[i] == key:
                return
            node.keys.insert(i, key)
        else:
            i = bisect_right(node.keys, key)
            if len(node.children[i].keys) == self.order - 1:
                self._split_child(node, i)
                if key >= node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key)

    def _split_child(self, parent, index):
        node = parent.children[index]
        mid = len(node.keys) // 2

        if node.leaf:
            new_node = BPlusNode(leaf=True)
            new_node.keys = node.keys[mid:]
            node.keys = node.keys[:mid]
            new_node.next = node.next
            node.next = new_node
            parent.keys.insert(index, new_node.keys[0])
            parent.children.insert(index + 1, new_node)
        else:
            new_node = BPlusNode()
            push_up_key = node.keys[mid]
            new_node.keys = node.keys[mid + 1 :]
            new_node.children = node.children[mid + 1 :]
            node.keys = node.keys[:mid]
            node.children = node.children[: mid + 1]
            parent.keys.insert(index, push_up_key)
            parent.children.insert(index + 1, new_node)

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, node, key):
        if node.leaf:
            i = bisect_left(node.keys, key)
            return i < len(node.keys) and node.keys[i] == key
        i = bisect_right(node.keys, key)
        return self._search(node.children[i], key)

    def range_query(self, start, end):
        """Return every key in the inclusive range [start, end]."""
        if start > end:
            start, end = end, start

        node = self.root
        while not node.leaf:
            node = node.children[bisect_right(node.keys, start)]

        values = []
        while node:
            idx = bisect_left(node.keys, start)
            while idx < len(node.keys) and node.keys[idx] <= end:
                values.append(node.keys[idx])
                idx += 1
            if not node.keys or node.keys[-1] > end:
                break
            node = node.next
        return values

    def to_sorted_list(self):
        node = self.root
        while not node.leaf:
            node = node.children[0]

        out = []
        while node:
            out.extend(node.keys)
            node = node.next
        return out

    def bulk_load(self, values):
        """Fast-ish insertion path for demos: sort/dedupe first then insert."""
        for value in sorted(set(values)):
            self.insert(value)

    def delete(self, key):
        self._delete(self.root, key)
        if not self.root.leaf and len(self.root.keys) == 0 and self.root.children:
            self.root = self.root.children[0]

    def _delete(self, node, key):
        if node.leaf:
            i = bisect_left(node.keys, key)
            if i < len(node.keys) and node.keys[i] == key:
                node.keys.pop(i)
            return

        i = bisect_right(node.keys, key)
        self._delete(node.children[i], key)

        if len(node.children[i].keys) < (self.order - 1) // 2:
            self._fix_child(node, i)

        self._update_keys(node)

    def _fix_child(self, parent, index):
        if index > 0 and len(parent.children[index - 1].keys) > (self.order - 1) // 2:
            self._borrow_from_left(parent, index)
        elif (
            index < len(parent.children) - 1
            and len(parent.children[index + 1].keys) > (self.order - 1) // 2
        ):
            self._borrow_from_right(parent, index)
        else:
            if index > 0:
                self._merge(parent, index - 1)
            elif index < len(parent.children) - 1:
                self._merge(parent, index)

    def _borrow_from_left(self, parent, index):
        child = parent.children[index]
        left = parent.children[index - 1]
        if child.leaf:
            child.keys.insert(0, left.keys.pop())
            parent.keys[index - 1] = child.keys[0]
        else:
            child.keys.insert(0, parent.keys[index - 1])
            parent.keys[index - 1] = left.keys.pop()
            if left.children:
                child.children.insert(0, left.children.pop())

    def _borrow_from_right(self, parent, index):
        child = parent.children[index]
        right = parent.children[index + 1]
        if child.leaf:
            child.keys.append(right.keys.pop(0))
            parent.keys[index] = right.keys[0]
        else:
            child.keys.append(parent.keys[index])
            parent.keys[index] = right.keys.pop(0)
            if right.children:
                child.children.append(right.children.pop(0))

    def _merge(self, parent, index):
        left = parent.children[index]
        right = parent.children[index + 1]
        if left.leaf:
            left.keys.extend(right.keys)
            left.next = right.next
        else:
            left.keys.append(parent.keys[index])
            left.keys.extend(right.keys)
            left.children.extend(right.children)
        parent.keys.pop(index)
        parent.children.pop(index + 1)

    def _update_keys(self, node):
        for i in range(len(node.children) - 1):
            if node.children[i + 1].leaf:
                if node.children[i + 1].keys:
                    node.keys[i] = node.children[i + 1].keys[0]
            else:
                leftmost = node.children[i + 1]
                while not leftmost.leaf:
                    leftmost = leftmost.children[0]
                if leftmost.keys:
                    node.keys[i] = leftmost.keys[0]


def get_levels(root):
    if root is None or len(root.keys) == 0:
        return []
    levels = []
    current_level = [root]
    while current_level:
        levels.append(current_level)
        next_level = []
        for node in current_level:
            if not node.leaf:
                next_level.extend(node.children)
        current_level = next_level
    return levels
