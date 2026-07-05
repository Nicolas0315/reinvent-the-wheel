"""rewheel — 車輪の再発明.

Myers O(ND) diff algorithm, implemented from the 1986 paper
"An O(ND) Difference Algorithm and Its Variations".
No difflib. That would defeat the point.
"""

__version__ = "0.1.0"


def myers_diff(a, b):
    """Return a minimal edit script as a list of (op, line) tuples.

    op is one of ' ' (keep), '-' (delete from a), '+' (insert from b).
    The script is minimal in the number of '-'/'+' operations (LCS-based).
    """
    n, m = len(a), len(b)
    if n + m == 0:
        return []
    # v[k] = furthest x reached on diagonal k after d steps
    v = {1: 0}
    trace = []
    for d in range(n + m + 1):
        v = dict(v)
        trace.append(v)
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v.get(k - 1, -1) < v.get(k + 1, -1)):
                x = v.get(k + 1, 0)  # step down: insertion
            else:
                x = v.get(k - 1, 0) + 1  # step right: deletion
            y = x - k
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1
            v[k] = x
            if x >= n and y >= m:
                return _backtrack(a, b, trace, d)
    raise AssertionError("unreachable: d cannot exceed n+m")


def _backtrack(a, b, trace, d):
    ops = []
    x, y = len(a), len(b)
    for depth in range(d, 0, -1):
        v = trace[depth]
        k = x - y
        if k == -depth or (k != depth and v.get(k - 1, -1) < v.get(k + 1, -1)):
            prev_k = k + 1
        else:
            prev_k = k - 1
        prev_x = v.get(prev_k, 0)
        prev_y = prev_x - prev_k
        while x > prev_x and y > prev_y:
            x -= 1
            y -= 1
            ops.append((" ", a[x]))
        if x == prev_x:
            y -= 1
            ops.append(("+", b[y]))
        else:
            x -= 1
            ops.append(("-", a[x]))
    while x > 0 and y > 0:
        x -= 1
        y -= 1
        ops.append((" ", a[x]))
    ops.reverse()
    return ops


def edit_distance(ops):
    """Number of '-'/'+' operations in an edit script."""
    return sum(1 for op, _ in ops if op != " ")


def unified(a, b, fromfile="a", tofile="b", context=3):
    """Render a unified diff (like `diff -u`) from scratch."""
    ops = myers_diff(a, b)
    changed = [i for i, (op, _) in enumerate(ops) if op != " "]
    if not changed:
        return ""

    # group changed indices whose surrounding context windows touch
    groups = [[changed[0]]]
    for i in changed[1:]:
        if i - groups[-1][-1] <= 2 * context:
            groups[-1].append(i)
        else:
            groups.append([i])

    # a/b line numbers consumed by each op, precomputed as running totals
    ax = bx = 0
    starts = []  # (a_line, b_line) *before* op i is applied, 0-based
    for op, _ in ops:
        starts.append((ax, bx))
        if op in (" ", "-"):
            ax += 1
        if op in (" ", "+"):
            bx += 1

    out = [f"--- {fromfile}", f"+++ {tofile}"]
    for g in groups:
        lo = max(0, g[0] - context)
        hi = min(len(ops), g[-1] + context + 1)
        hunk = ops[lo:hi]
        a_start, b_start = starts[lo]
        a_len = sum(1 for op, _ in hunk if op in (" ", "-"))
        b_len = sum(1 for op, _ in hunk if op in (" ", "+"))
        out.append(f"@@ -{a_start + 1},{a_len} +{b_start + 1},{b_len} @@")
        out.extend(f"{op}{line}" for op, line in hunk)
    return "\n".join(out)
