"""Fuzz tests for the reinvented wheel.

Two independent oracles:
1. Reconstruction: applying the edit script to `a` must yield exactly `b`.
2. Minimality: edit distance must equal n + m - 2*LCS(a, b) computed by
   a brute-force DP that shares no code with the implementation.
"""

import random

from rewheel import edit_distance, myers_diff, unified


def apply_script(a, ops):
    """Replay an edit script against `a` and return the reconstructed `b`."""
    out = []
    i = 0
    for op, line in ops:
        if op == " ":
            assert a[i] == line, f"keep mismatch at {i}: {a[i]!r} != {line!r}"
            out.append(line)
            i += 1
        elif op == "-":
            assert a[i] == line, f"delete mismatch at {i}: {a[i]!r} != {line!r}"
            i += 1
        else:
            out.append(line)
    assert i == len(a), f"script consumed {i} of {len(a)} input lines"
    return out


def lcs_len(a, b):
    """Textbook DP, deliberately independent of the Myers implementation."""
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b):
            cur.append(prev[j] + 1 if x == y else max(prev[j + 1], cur[-1]))
        prev = cur
    return prev[-1]


def check(a, b):
    ops = myers_diff(a, b)
    got = apply_script(a, ops)
    assert got == b, f"reconstruction failed: {got!r} != {b!r}"
    want = len(a) + len(b) - 2 * lcs_len(a, b)
    d = edit_distance(ops)
    assert d == want, f"non-minimal script: d={d}, optimal={want} for {a!r} -> {b!r}"


def main():
    # hand-picked edges
    cases = [
        ([], []),
        ([], ["x"]),
        (["x"], []),
        (["x"], ["x"]),
        (["x"], ["y"]),
        (list("abcabba"), list("cbabac")),  # the example from Myers' paper
        (["same"] * 50, ["same"] * 50),
        (list("aaaa"), list("aaa")),
    ]
    for a, b in cases:
        check(a, b)

    rng = random.Random(20260705)
    alphabet = "abcde"
    for trial in range(2000):
        n = rng.randrange(0, 30)
        m = rng.randrange(0, 30)
        a = [rng.choice(alphabet) for _ in range(n)]
        b = [rng.choice(alphabet) for _ in range(m)]
        check(a, b)
        # also mutate a into b-like sequences to hit high-similarity paths
        b2 = a[:]
        for _ in range(rng.randrange(0, 5)):
            if b2 and rng.random() < 0.5:
                b2.pop(rng.randrange(len(b2)))
            else:
                b2.insert(rng.randrange(len(b2) + 1), rng.choice(alphabet))
        check(a, b2)

    print("myers_diff: 2008/2008 cases passed (reconstruction + minimality)")

    demo = unified(
        ["the wheel", "is round", "and rolls", "since 3500 BC", "unchanged"],
        ["the wheel", "was reinvented", "and rolls", "in 2026 AD", "unchanged"],
        fromfile="wheel_v1.txt",
        tofile="wheel_v2.txt",
        context=1,
    )
    print()
    print(demo)


if __name__ == "__main__":
    main()
