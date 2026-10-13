"""60-question quiz: 20 math word problems, 20 multiple-choice knowledge/reasoning, 20 Python coding tasks.

Math and multiple-choice answers are graded by exact match on a final "ANSWER:" line.
Coding answers are graded by running the unit tests below against the model's function.
Each coding task carries a reference solution; `python3 bench/quiz_questions.py` verifies keys and references.
"""

MATH = [
    ("A bakery sells muffins for $3 each and cookies for $1.25 each. Maria buys 4 muffins and 6 cookies and pays with a $50 bill. How much change does she get, in dollars?", 30.5),
    ("A train travels 180 km in 2.5 hours. At the same speed, how many km does it travel in 4 hours?", 288),
    ("A rectangle has a perimeter of 54 cm and its length is twice its width. What is its area in square cm?", 162),
    ("Tom has 3 times as many marbles as Jerry. Together they have 96 marbles. How many marbles does Tom have?", 72),
    ("A shirt costs $40. It is discounted by 25%, then 8% sales tax is added to the discounted price. What is the final price in dollars?", 32.4),
    ("An empty 1,200-liter tank is filled at 45 liters per minute while it leaks 15 liters per minute. How many minutes until it is full?", 40),
    ("What is the sum of all integers from 1 to 200 (inclusive) that are divisible by 3 or by 5?", sum(i for i in range(1, 201) if i % 3 == 0 or i % 5 == 0)),
    ("A recipe needs 2.5 cups of flour for 12 cookies. How many cups of flour are needed for 66 cookies?", 13.75),
    ("Sam reads 24 pages on Monday, and each day after that he reads 6 more pages than the day before. How many pages does he read in total from Monday through Sunday?", sum(24 + 6 * d for d in range(7))),
    ("A car gets 32 miles per gallon and gas costs $3.60 per gallon. How much does the fuel cost for a 400-mile trip, in dollars?", 400 / 32 * 3.60),
    ("What is the remainder when 7 to the power of 100 is divided by 13?", pow(7, 100, 13)),
    ("Three friends split a restaurant bill of $84 plus an 18% tip equally. How much does each person pay, in dollars?", round(84 * 1.18 / 3, 2)),
    ("A store has 250 notebooks. On Monday it sells 18% of them. On Tuesday it sells 40% of the notebooks that remain. How many notebooks are left?", 250 * 0.82 * 0.6),
    ("How many positive whole-number divisors does 360 have?", sum(1 for d in range(1, 361) if 360 % d == 0)),
    ("One pipe fills a pool in 6 hours. A second pipe fills it in 3 hours. How many hours does it take with both pipes running?", 1 / (1 / 6 + 1 / 3)),
    ("$5,000 is invested at 4% interest compounded once per year. What is it worth after 3 years, in dollars, rounded to the nearest cent?", round(5000 * 1.04 ** 3, 2)),
    ("The average of five numbers is 18. Four of them are 12, 20, 15 and 25. What is the fifth number?", 5 * 18 - (12 + 20 + 15 + 25)),
    ("An analog clock shows 3:40. What is the smaller angle between the hour hand and the minute hand, in degrees?", abs((3 * 30 + 40 * 0.5) - 40 * 6)),
    ("A school has 480 students and the ratio of boys to girls is 7 to 5. How many more boys than girls are there?", 480 * 7 // 12 - 480 * 5 // 12),
    ("How many distinct arrangements are there of the letters in the word BANANA?", 720 // (6 * 2)),
]

MULTIPLE_CHOICE = [
    ("In which year did the Berlin Wall fall?", ["1987", "1989", "1991", "1985"], "B"),
    ("Which element has the chemical symbol W?", ["Tungsten", "Titanium", "Vanadium", "Xenon"], "A"),
    ("The speed of sound in dry air at 20 degrees C is closest to:", ["99 m/s", "1,235 m/s", "3,000 m/s", "343 m/s"], "D"),
    ("Who wrote 'One Hundred Years of Solitude'?", ["Jorge Luis Borges", "Mario Vargas Llosa", "Gabriel Garcia Marquez", "Isabel Allende"], "C"),
    ("On a local network, which protocol finds the hardware (MAC) address for a given IP address?", ["DNS", "ARP", "DHCP", "ICMP"], "B"),
    ("Which of these numbers is NOT prime?", ["97", "89", "83", "91"], "D"),
    ("All bloops are razzies. Some razzies are lazzies. Which statement must be true?", ["All bloops are lazzies", "Some bloops are lazzies", "No bloops are lazzies", "None of these must be true"], "D"),
    ("If today is Wednesday, what day of the week will it be 100 days from now?", ["Thursday", "Friday", "Saturday", "Sunday"], "B"),
    ("Which organ produces insulin?", ["Liver", "Kidney", "Pancreas", "Spleen"], "C"),
    ("What is the time complexity of binary search on a sorted array of n items?", ["O(log n)", "O(n)", "O(n log n)", "O(1)"], "A"),
    ("According to United Nations estimates, which country has had the largest population since 2023?", ["China", "United States", "Indonesia", "India"], "D"),
    ("What is the main job of red blood cells?", ["Fighting infection", "Carrying oxygen", "Clotting blood", "Producing hormones"], "B"),
    ("A bat and a ball cost $1.10 together. The bat costs $1.00 more than the ball. How much does the ball cost?", ["$0.10", "$0.05", "$0.01", "$0.15"], "B"),
    ("Which layer of Earth's atmosphere contains most of the ozone layer?", ["Troposphere", "Mesosphere", "Stratosphere", "Thermosphere"], "C"),
    ("When people's incomes rise, what usually happens to demand for a 'normal good'?", ["It rises", "It falls", "It stays the same", "It drops to zero"], "A"),
    ("What does the S in HTTPS stand for?", ["Server", "Secure", "Standard", "Session"], "B"),
    ("Five runners finish a race. Eli finishes first. Ana finishes before Ben. Cara finishes after Ben but before Dev. Who finishes third?", ["Ana", "Cara", "Ben", "Dev"], "C"),
    ("Which data structure works on a last-in, first-out (LIFO) basis?", ["Queue", "Stack", "Heap", "Linked hash map"], "B"),
    ("The Peace of Westphalia (1648) ended which conflict?", ["The Hundred Years' War", "The Thirty Years' War", "The War of the Roses", "The Seven Years' War"], "B"),
    ("Light from the Sun takes about how long to reach Earth?", ["8 seconds", "8 hours", "8 minutes", "8 days"], "C"),
]

CODING = [
    {
        "name": "is_palindrome",
        "spec": "is_palindrome(s: str) -> bool. Return True if s reads the same forwards and backwards, ignoring case and any character that is not a letter or digit.",
        "tests": "assert is_palindrome('A man, a plan, a canal: Panama')\nassert not is_palindrome('race a car')\nassert is_palindrome('')\nassert is_palindrome('No lemon, no melon')\nassert not is_palindrome('ab')",
        "ref": "def is_palindrome(s):\n    t = [c.lower() for c in s if c.isalnum()]\n    return t == t[::-1]",
    },
    {
        "name": "levenshtein",
        "spec": "levenshtein(a: str, b: str) -> int. Return the minimum number of single-character insertions, deletions or substitutions needed to turn a into b.",
        "tests": "assert levenshtein('kitten', 'sitting') == 3\nassert levenshtein('', 'abc') == 3\nassert levenshtein('flaw', 'lawn') == 2\nassert levenshtein('same', 'same') == 0",
        "ref": "def levenshtein(a, b):\n    prev = list(range(len(b) + 1))\n    for i, ca in enumerate(a, 1):\n        cur = [i]\n        for j, cb in enumerate(b, 1):\n            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))\n        prev = cur\n    return prev[-1]",
    },
    {
        "name": "flatten",
        "spec": "flatten(lst: list) -> list. Flatten a list that may contain nested lists to any depth into a single flat list, keeping order.",
        "tests": "assert flatten([1, [2, [3, [4]], 5]]) == [1, 2, 3, 4, 5]\nassert flatten([]) == []\nassert flatten([[[]]]) == []\nassert flatten(['a', ['b', ['c']]]) == ['a', 'b', 'c']",
        "ref": "def flatten(lst):\n    out = []\n    for x in lst:\n        out.extend(flatten(x) if isinstance(x, list) else [x])\n    return out",
    },
    {
        "name": "word_count",
        "spec": "word_count(text: str) -> dict. Count words case-insensitively. A word is a maximal run of the letters a-z (after lowercasing); everything else separates words. Return a dict mapping each lowercase word to its count.",
        "tests": "assert word_count('Hello, hello world!') == {'hello': 2, 'world': 1}\nassert word_count('') == {}\nassert word_count(\"it's 2 o'clock\") == {'it': 1, 's': 1, 'o': 1, 'clock': 1}",
        "ref": "import re\nfrom collections import Counter\ndef word_count(text):\n    return dict(Counter(re.findall('[a-z]+', text.lower())))",
    },
    {
        "name": "roman_to_int",
        "spec": "roman_to_int(s: str) -> int. Convert a valid Roman numeral (I, V, X, L, C, D, M, with subtractive forms like IV and CM) to an integer.",
        "tests": "assert roman_to_int('III') == 3\nassert roman_to_int('LVIII') == 58\nassert roman_to_int('MCMXCIV') == 1994\nassert roman_to_int('MMXXVI') == 2026",
        "ref": "def roman_to_int(s):\n    v = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}\n    total = 0\n    for i, c in enumerate(s):\n        total += -v[c] if i + 1 < len(s) and v[c] < v[s[i + 1]] else v[c]\n    return total",
    },
    {
        "name": "int_to_roman",
        "spec": "int_to_roman(n: int) -> str. Convert an integer from 1 to 3999 to a standard Roman numeral using subtractive forms (IV, IX, XL, XC, CD, CM).",
        "tests": "assert int_to_roman(3) == 'III'\nassert int_to_roman(1994) == 'MCMXCIV'\nassert int_to_roman(3999) == 'MMMCMXCIX'\nassert int_to_roman(44) == 'XLIV'",
        "ref": "def int_to_roman(n):\n    pairs = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]\n    out = ''\n    for v, r in pairs:\n        while n >= v:\n            out += r\n            n -= v\n    return out",
    },
    {
        "name": "merge_intervals",
        "spec": "merge_intervals(intervals: list[list[int]]) -> list[list[int]]. Merge all overlapping or touching intervals (e.g. [1,3] and [3,5] merge) and return them sorted by start. Input may be unsorted.",
        "tests": "assert merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]\nassert merge_intervals([[1, 4], [4, 5]]) == [[1, 5]]\nassert merge_intervals([]) == []\nassert merge_intervals([[5, 7], [1, 2]]) == [[1, 2], [5, 7]]",
        "ref": "def merge_intervals(intervals):\n    out = []\n    for s, e in sorted(intervals):\n        if out and s <= out[-1][1]:\n            out[-1][1] = max(out[-1][1], e)\n        else:\n            out.append([s, e])\n    return out",
    },
    {
        "name": "two_sum",
        "spec": "two_sum(nums: list[int], target: int) -> tuple[int, int]. Return a tuple (i, j) with i < j such that nums[i] + nums[j] == target. Exactly one such pair exists.",
        "tests": "assert two_sum([2, 7, 11, 15], 9) == (0, 1)\nassert two_sum([3, 2, 4], 6) == (1, 2)\nassert two_sum([3, 3], 6) == (0, 1)\nassert two_sum([-1, 8, 4, 5], 3) == (0, 2)",
        "ref": "def two_sum(nums, target):\n    seen = {}\n    for j, x in enumerate(nums):\n        if target - x in seen:\n            return (seen[target - x], j)\n        seen[x] = j",
    },
    {
        "name": "is_valid_brackets",
        "spec": "is_valid_brackets(s: str) -> bool. Return True if every bracket in s ((), [], {}) is closed by the same type in the correct order. Ignore all other characters.",
        "tests": "assert is_valid_brackets('()[]{}')\nassert not is_valid_brackets('(]')\nassert is_valid_brackets('{[a+b]*(c)}')\nassert not is_valid_brackets('([)]')\nassert not is_valid_brackets('((')\nassert is_valid_brackets('')",
        "ref": "def is_valid_brackets(s):\n    pairs = {')': '(', ']': '[', '}': '{'}\n    st = []\n    for c in s:\n        if c in '([{':\n            st.append(c)\n        elif c in pairs:\n            if not st or st.pop() != pairs[c]:\n                return False\n    return not st",
    },
    {
        "name": "rotate_matrix",
        "spec": "rotate_matrix(m: list[list[int]]) -> list[list[int]]. Return a new matrix that is m rotated 90 degrees clockwise. m may be rectangular.",
        "tests": "assert rotate_matrix([[1, 2], [3, 4]]) == [[3, 1], [4, 2]]\nassert rotate_matrix([[1, 2, 3]]) == [[1], [2], [3]]\nassert rotate_matrix([[1, 2, 3], [4, 5, 6]]) == [[4, 1], [5, 2], [6, 3]]",
        "ref": "def rotate_matrix(m):\n    return [list(r) for r in zip(*m[::-1])]",
    },
    {
        "name": "longest_common_prefix",
        "spec": "longest_common_prefix(strs: list[str]) -> str. Return the longest string that is a prefix of every string in strs. Return '' for an empty list.",
        "tests": "assert longest_common_prefix(['flower', 'flow', 'flight']) == 'fl'\nassert longest_common_prefix(['dog', 'racecar', 'car']) == ''\nassert longest_common_prefix([]) == ''\nassert longest_common_prefix(['same']) == 'same'",
        "ref": "import os\ndef longest_common_prefix(strs):\n    return os.path.commonprefix(strs) if strs else ''",
    },
    {
        "name": "caesar",
        "spec": "caesar(s: str, k: int) -> str. Shift each letter by k positions in the alphabet, wrapping around and preserving case. k may be negative or larger than 26. Leave non-letters unchanged.",
        "tests": "assert caesar('abc', 1) == 'bcd'\nassert caesar('Hello, World!', 3) == 'Khoor, Zruog!'\nassert caesar('xyz', 29) == 'abc'\nassert caesar('Abc', -1) == 'Zab'",
        "ref": "def caesar(s, k):\n    out = []\n    for c in s:\n        if c.isalpha() and c.isascii():\n            base = ord('A') if c.isupper() else ord('a')\n            out.append(chr((ord(c) - base + k) % 26 + base))\n        else:\n            out.append(c)\n    return ''.join(out)",
    },
    {
        "name": "run_length_encode",
        "spec": "run_length_encode(s: str) -> str. Encode runs of the same character as the character followed by the run length, e.g. 'aaabcc' -> 'a3b1c2'.",
        "tests": "assert run_length_encode('aaabcc') == 'a3b1c2'\nassert run_length_encode('') == ''\nassert run_length_encode('a') == 'a1'\nassert run_length_encode('aaaaaaaaaaab') == 'a11b1'",
        "ref": "from itertools import groupby\ndef run_length_encode(s):\n    return ''.join(f'{c}{len(list(g))}' for c, g in groupby(s))",
    },
    {
        "name": "primes_up_to",
        "spec": "primes_up_to(n: int) -> list[int]. Return all prime numbers less than or equal to n, in increasing order.",
        "tests": "assert primes_up_to(10) == [2, 3, 5, 7]\nassert primes_up_to(1) == []\nassert primes_up_to(2) == [2]\nassert len(primes_up_to(10000)) == 1229",
        "ref": "def primes_up_to(n):\n    if n < 2:\n        return []\n    sieve = [True] * (n + 1)\n    sieve[0] = sieve[1] = False\n    for i in range(2, int(n ** 0.5) + 1):\n        if sieve[i]:\n            sieve[i * i::i] = [False] * len(sieve[i * i::i])\n    return [i for i, p in enumerate(sieve) if p]",
    },
    {
        "name": "binary_search",
        "spec": "binary_search(arr: list[int], x: int) -> int. arr is sorted ascending with no duplicates. Return the index of x, or -1 if x is not present.",
        "tests": "assert binary_search([1, 3, 5, 7, 9], 7) == 3\nassert binary_search([1, 3, 5, 7, 9], 4) == -1\nassert binary_search([], 1) == -1\nassert binary_search([5], 5) == 0\nassert binary_search(list(range(0, 1000, 2)), 998) == 499",
        "ref": "import bisect\ndef binary_search(arr, x):\n    i = bisect.bisect_left(arr, x)\n    return i if i < len(arr) and arr[i] == x else -1",
    },
    {
        "name": "group_anagrams",
        "spec": "group_anagrams(words: list[str]) -> list[list[str]]. Group words that are anagrams of each other. Any order of groups and of words within a group is fine.",
        "tests": "norm = lambda g: sorted(sorted(x) for x in g)\nassert norm(group_anagrams(['eat', 'tea', 'tan', 'ate', 'nat', 'bat'])) == norm([['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']])\nassert group_anagrams([]) == []\nassert norm(group_anagrams(['a'])) == [['a']]",
        "ref": "def group_anagrams(words):\n    g = {}\n    for w in words:\n        g.setdefault(''.join(sorted(w)), []).append(w)\n    return list(g.values())",
    },
    {
        "name": "max_subarray",
        "spec": "max_subarray(nums: list[int]) -> int. Return the largest sum of any non-empty contiguous subarray.",
        "tests": "assert max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6\nassert max_subarray([1]) == 1\nassert max_subarray([-3, -1, -2]) == -1\nassert max_subarray([5, 4, -1, 7, 8]) == 23",
        "ref": "def max_subarray(nums):\n    best = cur = nums[0]\n    for x in nums[1:]:\n        cur = max(x, cur + x)\n        best = max(best, cur)\n    return best",
    },
    {
        "name": "lcs_length",
        "spec": "lcs_length(a: str, b: str) -> int. Return the length of the longest common subsequence of a and b (characters in order, not necessarily adjacent).",
        "tests": "assert lcs_length('abcde', 'ace') == 3\nassert lcs_length('abc', 'def') == 0\nassert lcs_length('AGGTAB', 'GXTXAYB') == 4\nassert lcs_length('', 'abc') == 0",
        "ref": "def lcs_length(a, b):\n    prev = [0] * (len(b) + 1)\n    for ca in a:\n        cur = [0]\n        for j, cb in enumerate(b, 1):\n            cur.append(prev[j - 1] + 1 if ca == cb else max(prev[j], cur[j - 1]))\n        prev = cur\n    return prev[-1]",
    },
    {
        "name": "parse_duration",
        "spec": "parse_duration(s: str) -> int. Parse a duration like '1h30m15s', '45m', '2h' or '90s' into total seconds. Parts appear in the order h, m, s and any part may be missing.",
        "tests": "assert parse_duration('1h30m15s') == 5415\nassert parse_duration('45m') == 2700\nassert parse_duration('2h') == 7200\nassert parse_duration('90s') == 90\nassert parse_duration('1h5s') == 3605",
        "ref": "import re\ndef parse_duration(s):\n    m = re.fullmatch(r'(?:(\\d+)h)?(?:(\\d+)m)?(?:(\\d+)s)?', s)\n    h, mi, se = (int(x) if x else 0 for x in m.groups())\n    return h * 3600 + mi * 60 + se",
    },
    {
        "name": "spiral_order",
        "spec": "spiral_order(m: list[list[int]]) -> list[int]. Return the elements of matrix m in clockwise spiral order starting from the top-left. m may be rectangular or empty.",
        "tests": "assert spiral_order([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [1, 2, 3, 6, 9, 8, 7, 4, 5]\nassert spiral_order([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]) == [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]\nassert spiral_order([]) == []\nassert spiral_order([[1], [2], [3]]) == [1, 2, 3]",
        "ref": "def spiral_order(m):\n    out = []\n    m = [list(r) for r in m]\n    while m:\n        out += m.pop(0)\n        m = [list(r) for r in zip(*m)][::-1]\n    return out",
    },
]


# Harder questions that separate strong models. Same grading rules.
HARD_MATH = [
    ("How many positive integers less than 1000 are divisible by neither 7 nor 11?", sum(1 for i in range(1, 1000) if i % 7 and i % 11)),
    ("How many zeros are at the end of 125! (125 factorial)?", 125 // 5 + 125 // 25 + 125 // 125),
    ("What is the sum of the digits of 2 to the power of 100?", sum(int(d) for d in str(2 ** 100))),
    ("In how many different ways can you climb a staircase of 20 steps if each move climbs 1, 2 or 3 steps?", (lambda: (lambda f: f(f, 20))(lambda f, n: 1 if n == 0 else sum(f(f, n - k) for k in (1, 2, 3) if n - k >= 0)))()),
    ("How many 5-card hands from a standard 52-card deck contain exactly two aces?", 6 * (48 * 47 * 46 // 6)),
    ("What is the smallest positive integer n such that n! is divisible by 10 to the power of 10?", next(n for n in range(1, 100) if sum(n // 5 ** k for k in range(1, 4)) >= 10)),
    ("How many integers from 1 to 10,000 inclusive are perfect squares or perfect cubes (or both)?", len({i * i for i in range(1, 101)} | {i ** 3 for i in range(1, 22)})),
    ("What are the last three digits of 3 to the power of 2026? Give them as a number.", pow(3, 2026, 1000)),
    ("What is the smallest positive integer that leaves remainder 2 when divided by 3, remainder 3 when divided by 5, and remainder 2 when divided by 7?", next(n for n in range(1, 200) if n % 3 == 2 and n % 5 == 3 and n % 7 == 2)),
    ("A grid has 6 rows and 6 columns of squares. Moving only right or down along the grid lines, how many different shortest paths go from the top-left corner to the bottom-right corner?", 924),
]

HARD_MULTIPLE_CHOICE = [
    ("A game show has 3 doors: one car, two goats. You pick door 1. The host, who does NOT know where the car is, opens door 3 at random and it happens to show a goat. If you switch to door 2, what is your chance of winning the car?", ["1/3", "1/2", "2/3", "3/4"], "B"),
    ("A family has two children. At least one of them is a boy who was born on a Tuesday. What is the probability that both children are boys? (Assume boys and girls and all days of the week are equally likely.)", ["1/2", "1/3", "13/27", "1/4"], "C"),
    ("On an island, knights always tell the truth and knaves always lie. A says: 'We are both knaves.' What are A and B?", ["Both knights", "Both knaves", "A is a knight, B is a knave", "A is a knave, B is a knight"], "D"),
    ("If the day before yesterday was Thursday, what day will it be the day after tomorrow?", ["Sunday", "Monday", "Tuesday", "Saturday"], "B"),
    ("How many times do the hour hand and minute hand of a clock point in exactly the same direction during a full 24-hour day?", ["24", "23", "22", "12"], "C"),
]

HARD_CODING = [
    {
        "name": "evaluate",
        "spec": "evaluate(expr: str) -> int. Evaluate an arithmetic expression containing non-negative integers, +, -, *, / and parentheses, with normal operator precedence. Spaces may appear anywhere. Division is integer division that truncates toward zero.",
        "tests": "assert evaluate('3+2*2') == 7\nassert evaluate(' 3/2 ') == 1\nassert evaluate('(1+(4+5+2)-3)+(6+8)') == 23\nassert evaluate('14-3/2') == 13\nassert evaluate('2*(3+4)*5') == 70\nassert evaluate('(2-9)/2') == -3\nassert evaluate('100') == 100",
        "ref": "def evaluate(expr):\n    s = expr.replace(' ', '')\n    pos = 0\n    def num():\n        nonlocal pos\n        if s[pos] == '(':\n            pos += 1\n            v = add()\n            pos += 1\n            return v\n        start = pos\n        while pos < len(s) and s[pos].isdigit():\n            pos += 1\n        return int(s[start:pos])\n    def mul():\n        nonlocal pos\n        v = num()\n        while pos < len(s) and s[pos] in '*/':\n            op = s[pos]\n            pos += 1\n            r = num()\n            v = v * r if op == '*' else int(v / r)\n        return v\n    def add():\n        nonlocal pos\n        v = mul()\n        while pos < len(s) and s[pos] in '+-':\n            op = s[pos]\n            pos += 1\n            r = mul()\n            v = v + r if op == '+' else v - r\n        return v\n    return add()",
    },
    {
        "name": "LRUCache",
        "spec": "class LRUCache with __init__(self, capacity: int), get(self, key) -> int and put(self, key, value) -> None. get returns the value or -1 if missing. put inserts or updates a key. Both get and put mark the key as most recently used. When an insert exceeds capacity, evict the least recently used key.",
        "tests": "c = LRUCache(2)\nc.put(1, 1)\nc.put(2, 2)\nassert c.get(1) == 1\nc.put(3, 3)\nassert c.get(2) == -1\nc.put(4, 4)\nassert c.get(1) == -1\nassert c.get(3) == 3\nassert c.get(4) == 4\nd = LRUCache(2)\nd.put(1, 1)\nd.put(2, 2)\nd.put(1, 10)\nd.put(3, 3)\nassert d.get(1) == 10\nassert d.get(2) == -1",
        "ref": "from collections import OrderedDict\nclass LRUCache:\n    def __init__(self, capacity):\n        self.cap = capacity\n        self.d = OrderedDict()\n    def get(self, key):\n        if key not in self.d:\n            return -1\n        self.d.move_to_end(key)\n        return self.d[key]\n    def put(self, key, value):\n        self.d[key] = value\n        self.d.move_to_end(key)\n        if len(self.d) > self.cap:\n            self.d.popitem(last=False)",
    },
    {
        "name": "next_permutation",
        "spec": "next_permutation(nums: list[int]) -> list[int]. Return a new list with the next lexicographically greater permutation of nums. If nums is the largest permutation, return the smallest one (sorted ascending). nums may contain duplicates.",
        "tests": "assert next_permutation([1, 2, 3]) == [1, 3, 2]\nassert next_permutation([3, 2, 1]) == [1, 2, 3]\nassert next_permutation([1, 1, 5]) == [1, 5, 1]\nassert next_permutation([1, 3, 2]) == [2, 1, 3]\nassert next_permutation([2, 2, 1, 1]) == [1, 1, 2, 2]\nassert next_permutation([5]) == [5]",
        "ref": "def next_permutation(nums):\n    a = list(nums)\n    i = len(a) - 2\n    while i >= 0 and a[i] >= a[i + 1]:\n        i -= 1\n    if i >= 0:\n        j = len(a) - 1\n        while a[j] <= a[i]:\n            j -= 1\n        a[i], a[j] = a[j], a[i]\n    a[i + 1:] = reversed(a[i + 1:])\n    return a",
    },
    {
        "name": "count_islands",
        "spec": "count_islands(grid: list[str]) -> int. grid is a list of equal-length strings of '1' (land) and '0' (water). Count islands: groups of land cells connected up, down, left or right (not diagonally).",
        "tests": "assert count_islands(['11000', '11000', '00100', '00011']) == 3\nassert count_islands(['111', '010', '111']) == 1\nassert count_islands(['101', '010', '101']) == 5\nassert count_islands([]) == 0\nassert count_islands(['0000']) == 0",
        "ref": "def count_islands(grid):\n    seen = set()\n    def fill(r, c):\n        stack = [(r, c)]\n        while stack:\n            r, c = stack.pop()\n            if (r, c) in seen or not (0 <= r < len(grid) and 0 <= c < len(grid[0])) or grid[r][c] != '1':\n                continue\n            seen.add((r, c))\n            stack += [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]\n    n = 0\n    for r in range(len(grid)):\n        for c in range(len(grid[0])):\n            if grid[r][c] == '1' and (r, c) not in seen:\n                n += 1\n                fill(r, c)\n    return n",
    },
    {
        "name": "decode_ways",
        "spec": "decode_ways(s: str) -> int. Letters are encoded as numbers: A=1, B=2, ..., Z=26. Given a string of digits, return how many different ways it can be decoded back into letters. A code cannot start with 0 (so '06' is not valid for F).",
        "tests": "assert decode_ways('12') == 2\nassert decode_ways('226') == 3\nassert decode_ways('06') == 0\nassert decode_ways('11106') == 2\nassert decode_ways('10') == 1\nassert decode_ways('2611055971756562') == 4\nassert decode_ways('0') == 0",
        "ref": "def decode_ways(s):\n    prev, cur = 1, (1 if s and s[0] != '0' else 0)\n    for i in range(1, len(s)):\n        nxt = 0\n        if s[i] != '0':\n            nxt += cur\n        if s[i - 1] == '1' or (s[i - 1] == '2' and s[i] <= '6'):\n            nxt += prev\n        prev, cur = cur, nxt\n    return cur if s else 0",
    },
]


# Challenge set: only questions that separate models. 50 of the 80 questions above were answered correctly in all
# 19 quiz runs measured up to 2026-10-21, so they are not asked again. CHALLENGE_KEEP lists the questions above
# (numbered 1-80 in quiz order) that a strong model or at least two runs got wrong. The rest are new: 25 were
# written, and the 11 that both calibration models (gemma4-fable-text and granite4.2:8b, neither in the deck)
# answered correctly were dropped. bench/results/challenge-calibration.json holds that run, numbered for all 40.
CHALLENGE_KEEP = [59, 60, 63, 64, 65, 67, 68, 70, 71, 74, 76, 77, 78, 79, 80]

CHALLENGE_MATH = [
    ("What are the last two nonzero digits of 30! (30 factorial)? Give them as a two-digit number.", 48),
    ("How many integers from 1 to 10,000 inclusive have digits that add up to exactly 20?", 633),
    ("In how many ways can 10 identical balls be placed into 4 different boxes if no box may hold more than 4 balls?", 68),
    ("How many months in the years 2026 and 2027 combined have a Friday the 13th?", 4),
    ("What is the smallest positive integer that has exactly 30 positive divisors?", 720),
    ("How many integers n from 1 to 2026 inclusive make n squared plus n plus 1 divisible by 7?", 579),
    ("Two fair six-sided dice are rolled. Given that at least one die shows a 6, the probability that the total is at least 10 is m/n in lowest terms. What is m + n?", 16),
    ("A phone number has 7 digits, each 0 to 9, and leading zeros are allowed. How many phone numbers contain the digit 7 at least once and never have the same digit twice in a row?", 2955114),
]

CHALLENGE_MULTIPLE_CHOICE = [
    ("Five people P, Q, R, S and T sit in seats 1 to 5 in a row, numbered left to right. Q sits immediately to the right of P. R is not in seat 1 or seat 5. S sits somewhere to the left of T. T does not sit next to R. P is not in seat 1. Who sits in seat 3?", ["R", "Q", "P", "S"], "C"),
]

CHALLENGE_CODING = [
    {
        "name": "calc",
        "spec": "calc(expr: str) -> int. Evaluate an integer expression with +, -, *, /, ^, unary minus and parentheses. Spaces may appear anywhere. Precedence from highest to lowest: ^ (exponent, right-associative), unary minus, then * and / (left-associative), then + and - (left-associative). So -2^2 is -4 and 2^3^2 is 512. / is integer division that truncates toward zero. Exponents are never negative.",
        "tests": "assert calc('2^3^2') == 512\nassert calc('-2^2') == -4\nassert calc('(-2)^2') == 4\nassert calc('2*-3') == -6\nassert calc('- -3') == 3\nassert calc('10/-3') == -3\nassert calc('-7/2') == -3\nassert calc('1 + 2 * 3 ^ 2') == 19\nassert calc('(1+2)*(3-5)^3') == -24\nassert calc('100 - 2 - 3') == 95\nassert calc('-(2+3)^2') == -25",
        "ref": "def calc(expr):\n    s = expr.replace(' ', '')\n    pos = 0\n    def peek():\n        return s[pos] if pos < len(s) else ''\n    def atom():\n        nonlocal pos\n        if peek() == '(':\n            pos += 1\n            v = add()\n            pos += 1\n            return v\n        start = pos\n        while peek().isdigit():\n            pos += 1\n        return int(s[start:pos])\n    def power():\n        nonlocal pos\n        base = atom()\n        if peek() == '^':\n            pos += 1\n            return base ** unary()\n        return base\n    def unary():\n        nonlocal pos\n        if peek() == '-':\n            pos += 1\n            return -unary()\n        return power()\n    def mul():\n        nonlocal pos\n        v = unary()\n        while peek() in ('*', '/'):\n            op = s[pos]\n            pos += 1\n            r = unary()\n            v = v * r if op == '*' else int(v / r)\n        return v\n    def add():\n        nonlocal pos\n        v = mul()\n        while peek() in ('+', '-'):\n            op = s[pos]\n            pos += 1\n            r = mul()\n            v = v + r if op == '+' else v - r\n        return v\n    return add()",
    },
    {
        "name": "int_to_words",
        "spec": "int_to_words(n: int) -> str. Write 0 <= n < 1,000,000,000 in English words, all lowercase, words separated by single spaces. Use 'zero' for 0. Numbers 21 to 99 that are not multiples of ten use a hyphen ('forty-two'). Do not use 'and' or commas. Use 'hundred', 'thousand' and 'million' (e.g. 'one million two hundred thirty-four thousand five hundred sixty-seven'). Skip groups that are zero (1000005 is 'one million five').",
        "tests": "assert int_to_words(0) == 'zero'\nassert int_to_words(7) == 'seven'\nassert int_to_words(13) == 'thirteen'\nassert int_to_words(40) == 'forty'\nassert int_to_words(42) == 'forty-two'\nassert int_to_words(105) == 'one hundred five'\nassert int_to_words(1000) == 'one thousand'\nassert int_to_words(1000005) == 'one million five'\nassert int_to_words(1234567) == 'one million two hundred thirty-four thousand five hundred sixty-seven'\nassert int_to_words(999999999) == 'nine hundred ninety-nine million nine hundred ninety-nine thousand nine hundred ninety-nine'\nassert int_to_words(20019) == 'twenty thousand nineteen'\nassert int_to_words(300000000) == 'three hundred million'",
        "ref": "def int_to_words(n):\n    ones = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()\n    tens = 'x x twenty thirty forty fifty sixty seventy eighty ninety'.split()\n    def under_1000(k):\n        out = []\n        if k >= 100:\n            out += [ones[k // 100], 'hundred']\n            k %= 100\n        if k >= 20:\n            out.append(tens[k // 10] + ('-' + ones[k % 10] if k % 10 else ''))\n        elif k:\n            out.append(ones[k])\n        return out\n    if n == 0:\n        return 'zero'\n    words = []\n    for size, name in ((10 ** 6, 'million'), (10 ** 3, 'thousand'), (1, '')):\n        k, n = divmod(n, size)\n        if k:\n            words += under_1000(k) + ([name] if name else [])\n    return ' '.join(words)",
    },
    {
        "name": "flatten_json",
        "spec": "flatten_json(obj: dict) -> dict. Flatten nested dicts and lists into one dict whose keys are paths joined with '.'. List items use their index as the path part. A nested empty dict or empty list is kept as the value at its path. Other values (numbers, strings, booleans, None) are leaves. Example: {'a': {'b': [1, {'c': 2}]}, 'd': []} becomes {'a.b.0': 1, 'a.b.1.c': 2, 'd': []}.",
        "tests": "assert flatten_json({'a': {'b': [1, {'c': 2}]}, 'd': []}) == {'a.b.0': 1, 'a.b.1.c': 2, 'd': []}\nassert flatten_json({}) == {}\nassert flatten_json({'x': {}}) == {'x': {}}\nassert flatten_json({'x': [[1, 2], []]}) == {'x.0.0': 1, 'x.0.1': 2, 'x.1': []}\nassert flatten_json({'a': None, 'b': {'c': False}}) == {'a': None, 'b.c': False}\nassert flatten_json({'k': [{'a': [{}]}]}) == {'k.0.a.0': {}}",
        "ref": "def flatten_json(obj):\n    out = {}\n    def walk(v, path):\n        if isinstance(v, dict) and v:\n            for k, x in v.items():\n                walk(x, f'{path}.{k}' if path else str(k))\n        elif isinstance(v, list) and v:\n            for i, x in enumerate(v):\n                walk(x, f'{path}.{i}' if path else str(i))\n        else:\n            out[path] = v\n    for k, v in obj.items():\n        walk(v, str(k))\n    return out",
    },
    {
        "name": "glob_match",
        "spec": "glob_match(name: str, pattern: str) -> bool. Match the whole name against a shell-style pattern, case-sensitively. '*' matches any sequence of characters (including none), '?' matches exactly one character, '[abc]' matches one character from the set, ranges like '[a-z]' are allowed inside brackets, and '[!abc]' matches one character NOT in the set. All other characters match themselves.",
        "tests": "assert glob_match('report.txt', '*.txt')\nassert not glob_match('report.txt', '*.TXT')\nassert glob_match('a1', '[a-c][0-9]')\nassert not glob_match('d1', '[a-c][0-9]')\nassert glob_match('x', '[!abc]')\nassert not glob_match('b', '[!abc]')\nassert glob_match('', '*')\nassert not glob_match('', '?')\nassert glob_match('abcde', 'a*c?e')\nassert not glob_match('abcd', 'a*c?e')\nassert glob_match('aaa', 'a*a*a')\nassert glob_match('file-2.log', 'file-[!0-1].*')\nassert not glob_match('file-1.log', 'file-[!0-1].*')",
        "ref": "import fnmatch\ndef glob_match(name, pattern):\n    return fnmatch.fnmatchcase(name, pattern)",
    },
    {
        "name": "parse_csv_line",
        "spec": "parse_csv_line(line: str) -> list[str]. Split one line of CSV into fields. Fields are separated by commas. A field may be wrapped in double quotes; inside a quoted field, commas are literal and two double quotes \"\" stand for one double quote. Unquoted fields are taken as-is (no trimming). An empty line is one empty field, and a trailing comma means a final empty field.",
        "tests": "assert parse_csv_line('a,b,c') == ['a', 'b', 'c']\nassert parse_csv_line('\"x, y\",z') == ['x, y', 'z']\nassert parse_csv_line('\"he said \"\"hi\"\"\",2') == ['he said \"hi\"', '2']\nassert parse_csv_line('a,') == ['a', '']\nassert parse_csv_line('') == ['']\nassert parse_csv_line(',,') == ['', '', '']\nassert parse_csv_line(' a , b ') == [' a ', ' b ']\nassert parse_csv_line('\"\"') == ['']",
        "ref": "def parse_csv_line(line):\n    fields, cur, i, quoted = [], '', 0, False\n    while i < len(line):\n        ch = line[i]\n        if quoted:\n            if ch == '\"':\n                if i + 1 < len(line) and line[i + 1] == '\"':\n                    cur += '\"'\n                    i += 1\n                else:\n                    quoted = False\n            else:\n                cur += ch\n        elif ch == '\"':\n            quoted = True\n        elif ch == ',':\n            fields.append(cur)\n            cur = ''\n        else:\n            cur += ch\n        i += 1\n    fields.append(cur)\n    return fields",
    },
]


if __name__ == "__main__":
    assert len(MATH) == len(MULTIPLE_CHOICE) == len(CODING) == 20
    for q, a in MATH:
        print(f"{a!r:>10}  {q[:70]}")
    assert len(HARD_MATH) == 10 and len(HARD_MULTIPLE_CHOICE) == len(HARD_CODING) == 5
    for q, a in HARD_MATH:
        print(f"{a!r:>10}  HARD {q[:65]}")
    for c in CODING + HARD_CODING:
        exec(c["ref"] + "\n" + c["tests"], {})
    assert len(set(CHALLENGE_KEEP)) == len(CHALLENGE_KEEP) and all(1 <= n <= 80 for n in CHALLENGE_KEEP)
    for c in CHALLENGE_CODING:
        exec(c["ref"] + "\n" + c["tests"], {})
    print(f"All {len(CODING) + len(HARD_CODING) + len(CHALLENGE_CODING)} reference solutions pass their tests.")
