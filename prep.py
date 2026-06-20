#!/usr/bin/env python3
"""
prep.py — a local coding-interview practice harness.

Workflow:
    python prep.py list                  # browse problems (filter with --pattern / --difficulty)
    python prep.py new two-sum           # scaffold solutions/two-sum.py with a stub + examples
    # ...edit solutions/two-sum.py and implement the function...
    python prep.py test two-sum          # run your solution against the test cases
    python prep.py hint two-sum          # one-line nudge (the pattern)
    python prep.py reveal two-sum        # print a model solution (asks first)
    python prep.py random --pattern dp   # scaffold a random (optionally filtered) problem
    python prep.py stats                 # what you've solved, by pattern

Stdlib only. Solutions live in ./solutions/. Progress is saved to ~/.prep/progress.json.
"""
import argparse
import copy
import importlib.util
import inspect
import json
import os
import random
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

SOL_DIR = Path("solutions")
PROGRESS = Path.home() / ".prep" / "progress.json"

# ----------------------------------------------------------------------------- colors
def _supports_color():
    return sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

_C = _supports_color()
def c(text, code):
    return f"\033[{code}m{text}\033[0m" if _C else text
def green(t):  return c(t, "32")
def red(t):    return c(t, "31")
def yellow(t): return c(t, "33")
def blue(t):   return c(t, "36")
def grey(t):   return c(t, "90")
def bold(t):   return c(t, "1")

# ----------------------------------------------------------------------------- model solutions
def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], i]
        seen[x] = i
    return []

def is_anagram(s, t):
    from collections import Counter
    return Counter(s) == Counter(t)

def group_anagrams(strs):
    from collections import defaultdict
    groups = defaultdict(list)
    for w in strs:
        groups[tuple(sorted(w))].append(w)
    return list(groups.values())

def top_k_frequent(nums, k):
    from collections import Counter
    return [v for v, _ in Counter(nums).most_common(k)]

def is_palindrome(s):
    t = [ch.lower() for ch in s if ch.isalnum()]
    return t == t[::-1]

def three_sum(nums):
    nums = sorted(nums)
    res, n = [], len(nums)
    for i in range(n):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        l, r = i + 1, n - 1
        while l < r:
            s = nums[i] + nums[l] + nums[r]
            if s < 0:
                l += 1
            elif s > 0:
                r -= 1
            else:
                res.append([nums[i], nums[l], nums[r]])
                l += 1
                r -= 1
                while l < r and nums[l] == nums[l - 1]:
                    l += 1
                while l < r and nums[r] == nums[r + 1]:
                    r -= 1
    return res

def max_area(height):
    l, r, best = 0, len(height) - 1, 0
    while l < r:
        best = max(best, (r - l) * min(height[l], height[r]))
        if height[l] < height[r]:
            l += 1
        else:
            r -= 1
    return best

def length_of_longest_substring(s):
    seen, l, best = {}, 0, 0
    for r, ch in enumerate(s):
        if ch in seen and seen[ch] >= l:
            l = seen[ch] + 1
        seen[ch] = r
        best = max(best, r - l + 1)
    return best

def is_valid(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
        else:
            stack.append(ch)
    return not stack

def daily_temperatures(temps):
    res, stack = [0] * len(temps), []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            res[j] = i - j
        stack.append(i)
    return res

def search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

def min_eating_speed(piles, h):
    import math
    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi) // 2
        if sum(math.ceil(p / mid) for p in piles) <= h:
            hi = mid
        else:
            lo = mid + 1
    return lo

def num_islands(grid):
    if not grid:
        return 0
    rows, cols, count = len(grid), len(grid[0]), 0
    def dfs(r, col):
        if r < 0 or col < 0 or r >= rows or col >= cols or grid[r][col] != "1":
            return
        grid[r][col] = "0"
        dfs(r + 1, col); dfs(r - 1, col); dfs(r, col + 1); dfs(r, col - 1)
    for r in range(rows):
        for col in range(cols):
            if grid[r][col] == "1":
                count += 1
                dfs(r, col)
    return count

def can_finish(num_courses, prerequisites):
    from collections import defaultdict, deque
    adj, indeg = defaultdict(list), [0] * num_courses
    for a, b in prerequisites:
        adj[b].append(a)
        indeg[a] += 1
    q = deque(i for i in range(num_courses) if indeg[i] == 0)
    seen = 0
    while q:
        u = q.popleft()
        seen += 1
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return seen == num_courses

def climb_stairs(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def coin_change(coins, amount):
    INF = float("inf")
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for coin in coins:
            if coin <= a:
                dp[a] = min(dp[a], dp[a - coin] + 1)
    return dp[amount] if dp[amount] != INF else -1

def longest_common_subsequence(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]

def merge(intervals):
    intervals = sorted(intervals)
    res = []
    for s, e in intervals:
        if res and s <= res[-1][1]:
            res[-1][1] = max(res[-1][1], e)
        else:
            res.append([s, e])
    return res

# ----------------------------------------------------------------------------- problem set
# compare modes: eq | sorted | set_groups | set_triples
PROBLEMS = [
    dict(id="two-sum", title="Two Sum", pattern="arrays-hashing", diff="easy",
         fn="two_sum", ref=two_sum, compare="sorted",
         sig="def two_sum(nums: List[int], target: int) -> List[int]:",
         stmt="Return indices of the two numbers that add up to target (exactly one solution).",
         inputs=[([2, 7, 11, 15], 9), ([3, 2, 4], 6), ([3, 3], 6)]),
    dict(id="valid-anagram", title="Valid Anagram", pattern="arrays-hashing", diff="easy",
         fn="is_anagram", ref=is_anagram, compare="eq",
         sig="def is_anagram(s: str, t: str) -> bool:",
         stmt="Return True if t is an anagram of s.",
         inputs=[("anagram", "nagaram"), ("rat", "car"), ("", "")]),
    dict(id="group-anagrams", title="Group Anagrams", pattern="arrays-hashing", diff="medium",
         fn="group_anagrams", ref=group_anagrams, compare="set_groups",
         sig="def group_anagrams(strs: List[str]) -> List[List[str]]:",
         stmt="Group strings that are anagrams of each other. Any group/order is fine.",
         inputs=[(["eat", "tea", "tan", "ate", "nat", "bat"],), ([""],), (["a"],)]),
    dict(id="top-k-frequent", title="Top K Frequent Elements", pattern="arrays-hashing", diff="medium",
         fn="top_k_frequent", ref=top_k_frequent, compare="sorted",
         sig="def top_k_frequent(nums: List[int], k: int) -> List[int]:",
         stmt="Return the k most frequent elements (any order).",
         inputs=[([1, 1, 1, 2, 2, 3], 2), ([1], 1), ([4, 4, 4, 5, 5, 6], 2)]),
    dict(id="valid-palindrome", title="Valid Palindrome", pattern="two-pointers", diff="easy",
         fn="is_palindrome", ref=is_palindrome, compare="eq",
         sig="def is_palindrome(s: str) -> bool:",
         stmt="Return True if s is a palindrome considering only alphanumerics, ignoring case.",
         inputs=[("A man, a plan, a canal: Panama",), ("race a car",), (" ",)]),
    dict(id="3sum", title="3Sum", pattern="two-pointers", diff="medium",
         fn="three_sum", ref=three_sum, compare="set_triples",
         sig="def three_sum(nums: List[int]) -> List[List[int]]:",
         stmt="Return all unique triplets that sum to zero (any order).",
         inputs=[([-1, 0, 1, 2, -1, -4],), ([0, 1, 1],), ([0, 0, 0],)]),
    dict(id="container", title="Container With Most Water", pattern="two-pointers", diff="medium",
         fn="max_area", ref=max_area, compare="eq",
         sig="def max_area(height: List[int]) -> int:",
         stmt="Return the max water area between two lines.",
         inputs=[([1, 8, 6, 2, 5, 4, 8, 3, 7],), ([1, 1],), ([4, 3, 2, 1, 4],)]),
    dict(id="longest-substring", title="Longest Substring Without Repeating", pattern="sliding-window", diff="medium",
         fn="length_of_longest_substring", ref=length_of_longest_substring, compare="eq",
         sig="def length_of_longest_substring(s: str) -> int:",
         stmt="Return the length of the longest substring without repeating characters.",
         inputs=[("abcabcbb",), ("bbbbb",), ("pwwkew",), ("",)]),
    dict(id="valid-parentheses", title="Valid Parentheses", pattern="stack", diff="easy",
         fn="is_valid", ref=is_valid, compare="eq",
         sig="def is_valid(s: str) -> bool:",
         stmt="Return True if the bracket string is valid.",
         inputs=[("()[]{}",), ("(]",), ("([{}])",), ("(",)]),
    dict(id="daily-temperatures", title="Daily Temperatures", pattern="monotonic-stack", diff="medium",
         fn="daily_temperatures", ref=daily_temperatures, compare="eq",
         sig="def daily_temperatures(temps: List[int]) -> List[int]:",
         stmt="For each day, how many days until a warmer temperature (0 if none).",
         inputs=[([73, 74, 75, 71, 69, 72, 76, 73],), ([30, 40, 50, 60],), ([30, 60, 90],)]),
    dict(id="binary-search", title="Binary Search", pattern="binary-search", diff="easy",
         fn="search", ref=search, compare="eq",
         sig="def search(nums: List[int], target: int) -> int:",
         stmt="Return the index of target in sorted nums, or -1.",
         inputs=[([-1, 0, 3, 5, 9, 12], 9), ([-1, 0, 3, 5, 9, 12], 2), ([5], 5)]),
    dict(id="koko", title="Koko Eating Bananas", pattern="binary-search", diff="medium",
         fn="min_eating_speed", ref=min_eating_speed, compare="eq",
         sig="def min_eating_speed(piles: List[int], h: int) -> int:",
         stmt="Min integer eating speed to finish all piles within h hours.",
         inputs=[([3, 6, 7, 11], 8), ([30, 11, 23, 4, 20], 5), ([30, 11, 23, 4, 20], 6)]),
    dict(id="num-islands", title="Number of Islands", pattern="graphs", diff="medium",
         fn="num_islands", ref=num_islands, compare="eq",
         sig="def num_islands(grid: List[List[str]]) -> int:",
         stmt="Count islands ('1' = land, '0' = water) with 4-directional connectivity.",
         inputs=[([["1", "1", "0"], ["1", "0", "0"], ["0", "0", "1"]],),
                 ([["1", "1", "1"], ["0", "1", "0"], ["1", "1", "1"]],)]),
    dict(id="course-schedule", title="Course Schedule", pattern="graphs", diff="medium",
         fn="can_finish", ref=can_finish, compare="eq",
         sig="def can_finish(num_courses: int, prerequisites: List[List[int]]) -> bool:",
         stmt="Return True if all courses can be finished (no prerequisite cycle).",
         inputs=[(2, [[1, 0]]), (2, [[1, 0], [0, 1]]), (4, [[1, 0], [2, 1], [3, 2]])]),
    dict(id="climbing-stairs", title="Climbing Stairs", pattern="dp", diff="easy",
         fn="climb_stairs", ref=climb_stairs, compare="eq",
         sig="def climb_stairs(n: int) -> int:",
         stmt="Number of distinct ways to climb n stairs taking 1 or 2 steps.",
         inputs=[(2,), (3,), (5,), (1,)]),
    dict(id="coin-change", title="Coin Change", pattern="dp", diff="medium",
         fn="coin_change", ref=coin_change, compare="eq",
         sig="def coin_change(coins: List[int], amount: int) -> int:",
         stmt="Fewest coins to make amount, or -1 if impossible.",
         inputs=[([1, 2, 5], 11), ([2], 3), ([1], 0)]),
    dict(id="lcs", title="Longest Common Subsequence", pattern="dp", diff="medium",
         fn="longest_common_subsequence", ref=longest_common_subsequence, compare="eq",
         sig="def longest_common_subsequence(text1: str, text2: str) -> int:",
         stmt="Length of the longest common subsequence of two strings.",
         inputs=[("abcde", "ace"), ("abc", "abc"), ("abc", "def")]),
    dict(id="merge-intervals", title="Merge Intervals", pattern="intervals", diff="medium",
         fn="merge", ref=merge, compare="sorted",
         sig="def merge(intervals: List[List[int]]) -> List[List[int]]:",
         stmt="Merge all overlapping intervals.",
         inputs=[([[1, 3], [2, 6], [8, 10], [15, 18]],), ([[1, 4], [4, 5]],), ([[1, 4], [2, 3]],)]),
]
BY_ID = {p["id"]: p for p in PROBLEMS}

# ----------------------------------------------------------------------------- comparison
def _norm(mode, val):
    if mode == "set_groups":
        return frozenset(tuple(sorted(g)) for g in val)
    if mode == "set_triples":
        return frozenset(tuple(sorted(t)) for t in val)
    if mode == "sorted":
        return sorted(val)
    return val

def _equal(mode, expected, got):
    try:
        return _norm(mode, expected) == _norm(mode, got)
    except Exception:
        return False

# ----------------------------------------------------------------------------- timeout
class _Timeout(Exception):
    pass

def _run_with_timeout(func, args, seconds=5):
    if hasattr(signal, "SIGALRM"):
        def handler(signum, frame):
            raise _Timeout()
        old = signal.signal(signal.SIGALRM, handler)
        signal.alarm(seconds)
        try:
            return func(*args)
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old)
    return func(*args)

# ----------------------------------------------------------------------------- helpers
def _args_repr(args):
    return ", ".join(repr(a) for a in args)

def _trunc(text, n=70):
    text = str(text)
    return text if len(text) <= n else text[: n - 1] + "…"

def _load_user_fn(p):
    path = SOL_DIR / f"{p['id']}.py"
    if not path.exists():
        sys.exit(red(f"No solution file at {path}. Run:  python prep.py new {p['id']}"))
    spec = importlib.util.spec_from_file_location("sol_" + p["id"].replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        sys.exit(red(f"Could not import your solution: {e}"))
    if not hasattr(mod, p["fn"]):
        sys.exit(red(f"Your file must define a function named '{p['fn']}'."))
    return getattr(mod, p["fn"])

def _load_progress():
    if PROGRESS.exists():
        try:
            return json.loads(PROGRESS.read_text())
        except Exception:
            return {}
    return {}

def _save_progress(data):
    PROGRESS.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS.write_text(json.dumps(data, indent=2))

# ----------------------------------------------------------------------------- commands
def cmd_list(args):
    rows = [p for p in PROBLEMS
            if (not args.pattern or args.pattern in p["pattern"])
            and (not args.difficulty or args.difficulty == p["diff"])]
    if not rows:
        print("No problems match that filter.")
        return
    done = set(_load_progress().get("solved", {}))
    print(bold(f"\n  {'ID':<20}{'PATTERN':<18}{'DIFF':<8}TITLE"))
    print(grey("  " + "-" * 64))
    for p in rows:
        mark = green("✓ ") if p["id"] in done else "  "
        print(f"{mark}{p['id']:<20}{blue(p['pattern']):<27}{p['diff']:<8}{p['title']}")
    print(grey(f"\n  {len(rows)} problems. Scaffold one with:  python prep.py new <id>\n"))

def cmd_show(args):
    p = BY_ID.get(args.id) or sys.exit(red(f"Unknown problem '{args.id}'."))
    print(f"\n{bold(p['title'])}  [{blue(p['pattern'])} · {p['diff']}]")
    print("\n" + p["stmt"])
    print(grey("\nSignature:"))
    print("  " + p["sig"])
    print(grey("\nExamples:"))
    for inp in p["inputs"][:2]:
        out = p["ref"](*copy.deepcopy(inp))
        print(f"  {p['fn']}({_trunc(_args_repr(inp))}) -> {out!r}")
    print()

def cmd_hint(args):
    p = BY_ID.get(args.id) or sys.exit(red(f"Unknown problem '{args.id}'."))
    print(f"\n{yellow('Hint:')} reach for the {bold(p['pattern'])} pattern.\n"
          f"      See that section in your reference for the template.\n")

def _scaffold(p):
    SOL_DIR.mkdir(exist_ok=True)
    path = SOL_DIR / f"{p['id']}.py"
    if path.exists():
        print(yellow(f"{path} already exists — leaving it untouched."))
        return path
    examples = "\n".join(
        f"    {p['fn']}({_trunc(_args_repr(inp), 60)}) -> {p['ref'](*copy.deepcopy(inp))!r}"
        for inp in p["inputs"][:2])
    body = (
        f'"""\n{p["title"]}   [{p["pattern"]} · {p["diff"]}]\n\n'
        f'{p["stmt"]}\n\nExamples:\n{examples}\n\n'
        f'Run:  python prep.py test {p["id"]}\n"""\n'
        f"from typing import List   # noqa: F401\n\n\n"
        f"{p['sig']}\n"
        f"    # TODO: implement\n"
        f"    pass\n"
    )
    path.write_text(body)
    return path

def cmd_new(args):
    p = BY_ID.get(args.id) or sys.exit(red(f"Unknown problem '{args.id}'."))
    path = _scaffold(p)
    print(green(f"\nScaffolded {path}"))
    print(grey(f"Open it, implement {p['fn']}(), then:  python prep.py test {p['id']}\n"))

def cmd_random(args):
    pool = [p for p in PROBLEMS
            if (not args.pattern or args.pattern in p["pattern"])
            and (not args.difficulty or args.difficulty == p["diff"])]
    if not pool:
        sys.exit(red("No problems match that filter."))
    p = random.choice(pool)
    path = _scaffold(p)
    print(green(f"\nYou drew: {bold(p['title'])}  [{p['pattern']} · {p['diff']}]"))
    print(grey(f"Scaffolded {path} — implement {p['fn']}() then: python prep.py test {p['id']}\n"))

def cmd_test(args):
    p = BY_ID.get(args.id) or sys.exit(red(f"Unknown problem '{args.id}'."))
    fn = _load_user_fn(p)
    print(f"\n{bold('Testing')} {p['title']}  [{blue(p['pattern'])} · {p['diff']}]")
    passed = 0
    total = len(p["inputs"])
    t0 = time.perf_counter()
    for i, inp in enumerate(p["inputs"], 1):
        expected = p["ref"](*copy.deepcopy(inp))
        try:
            got = _run_with_timeout(fn, copy.deepcopy(inp))
        except _Timeout:
            print(f"  {red('TIMEOUT')} case {i}  input={_trunc(_args_repr(inp))}")
            continue
        except Exception as e:
            print(f"  {red('ERROR')}   case {i}  {type(e).__name__}: {e}")
            if args.verbose:
                print(grey(f"          input={_trunc(_args_repr(inp), 90)}"))
            continue
        if _equal(p["compare"], expected, got):
            passed += 1
            if args.verbose:
                print(f"  {green('PASS')}    case {i}")
        else:
            print(f"  {red('FAIL')}    case {i}")
            print(grey(f"          input    = {_trunc(_args_repr(inp), 90)}"))
            print(grey(f"          expected = {_trunc(expected, 90)}"))
            print(grey(f"          got      = {_trunc(got, 90)}"))
    dt = (time.perf_counter() - t0) * 1000
    line = f"\n  {passed}/{total} passed  ({dt:.0f} ms)"
    print(green(line) if passed == total else red(line))
    if passed == total:
        prog = _load_progress()
        solved = prog.setdefault("solved", {})
        solved[p["id"]] = {"at": datetime.now().isoformat(timespec="seconds"),
                           "ms": round(dt, 1)}
        _save_progress(prog)
        print(green("  Solved — recorded.\n"))
    else:
        print(grey(f"  Hint: python prep.py hint {p['id']}   ·   "
                   f"Model: python prep.py reveal {p['id']}\n"))

def cmd_reveal(args):
    p = BY_ID.get(args.id) or sys.exit(red(f"Unknown problem '{args.id}'."))
    if not args.yes:
        ans = input(yellow(f"Show a model solution for '{p['title']}'? [y/N] ")).strip().lower()
        if ans not in ("y", "yes"):
            print("Skipped.")
            return
    print(grey(f"\n# model solution — {p['title']}\n"))
    print(inspect.getsource(p["ref"]))

def cmd_stats(args):
    prog = _load_progress()
    solved = set(prog.get("solved", {}))
    from collections import defaultdict
    tot, done = defaultdict(int), defaultdict(int)
    for p in PROBLEMS:
        tot[p["pattern"]] += 1
        if p["id"] in solved:
            done[p["pattern"]] += 1
    print(bold(f"\n  Solved {len(solved)}/{len(PROBLEMS)} overall\n"))
    for pat in sorted(tot):
        bar_done = done[pat]
        bar = green("█" * bar_done) + grey("░" * (tot[pat] - bar_done))
        print(f"  {pat:<18} {bar_done}/{tot[pat]}  {bar}")
    print()

# ----------------------------------------------------------------------------- argparse
def main():
    ap = argparse.ArgumentParser(prog="prep", description="Interview coding practice harness.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("list", help="list problems")
    s.add_argument("--pattern"); s.add_argument("--difficulty", choices=["easy", "medium", "hard"])
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("show", help="show a problem's statement + examples")
    s.add_argument("id"); s.set_defaults(func=cmd_show)

    s = sub.add_parser("new", help="scaffold a solution file"); s.add_argument("id")
    s.set_defaults(func=cmd_new)

    s = sub.add_parser("random", help="scaffold a random problem")
    s.add_argument("--pattern"); s.add_argument("--difficulty", choices=["easy", "medium", "hard"])
    s.set_defaults(func=cmd_random)

    s = sub.add_parser("test", help="run your solution against the test cases")
    s.add_argument("id"); s.add_argument("-v", "--verbose", action="store_true")
    s.set_defaults(func=cmd_test)

    s = sub.add_parser("hint", help="one-line pattern hint"); s.add_argument("id")
    s.set_defaults(func=cmd_hint)

    s = sub.add_parser("reveal", help="print a model solution")
    s.add_argument("id"); s.add_argument("-y", "--yes", action="store_true")
    s.set_defaults(func=cmd_reveal)

    s = sub.add_parser("stats", help="your progress by pattern"); s.set_defaults(func=cmd_stats)

    args = ap.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
