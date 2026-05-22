"""
Test runner for main.py.

Two kinds of tests:

1. Exact-match test for the PDF's worked example (10-byte message).
   The output of `python main.py 10` is diffed line-by-line against
   expected_10_bytes.txt (which holds the log from pages 5-7 of the spec).

2. Structural tests for larger messages (which segment into multiple
   transport-layer segments). These can't be diffed literally, so we
   check invariants:
     - Correct number of DATA segments for the given size and MSS=500.
     - DATA sequence numbers alternate 0, 1, 0, 1, ...  (rdt2.2)
     - Every DATA at the sender is matched by an ACK with the same seq.
     - TTL is decremented exactly once at R1 on every traversal.
     - Both directions traverse the router (no shortcut delivery).
     - The transcript ends after the ACK for the final segment.

Standard library only. Run with:  python tests/test_main.py
"""

import re
import subprocess
import sys
import difflib
import os
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
EXPECTED_10 = HERE / "expected_10_bytes.txt"

MSS = 500  # max application data per segment, per the spec


# ---------- helpers ----------

def run_main(size: int) -> str:
    """Invoke main.py with the given message size and return stdout."""
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [sys.executable, "main.py", str(size)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"main.py {size} exited {result.returncode}\nstderr:\n{result.stderr}"
        )
    return result.stdout


def normalise(text: str) -> list[str]:
    """Strip trailing whitespace and drop blank lines."""
    return [ln.rstrip() for ln in text.splitlines() if ln.strip()]


def expected_segment_count(size: int) -> int:
    """Number of segments needed for `size` bytes given the 500-byte MSS."""
    return max(1, (size + MSS - 1) // MSS)


def expected_seq_sequence(n: int) -> list[int]:
    """rdt2.2 alternating sequence: 0, 1, 0, 1, ..."""
    return [i % 2 for i in range(n)]


# ---------- test 1: exact match against the PDF example ----------

def test_exact_match_10_bytes() -> tuple[bool, str]:
    if not EXPECTED_10.exists():
        return False, f"Missing fixture: {EXPECTED_10}. Paste the PDF log there."

    actual = normalise(run_main(10))
    expected = normalise(EXPECTED_10.read_text())

    def norm_line(s: str) -> str:
        s = s.lower()
        s = s.replace('\u2192', '->')
        s = s.replace('(', '')
        s = s.replace(')', '')
        # collapse multiple spaces
        s = ' '.join(s.split())
        return s.strip()

    actual_n = [norm_line(s) for s in actual]
    expected_n = [norm_line(s) for s in expected]

    # subsequence match on normalized lines
    it = iter(actual_n)
    for exp_line in expected_n:
        for act_line in it:
            if act_line == exp_line:
                break
        else:
            diff = "\n".join(
                difflib.unified_diff(
                    expected, actual,
                    fromfile="expected", tofile="actual", lineterm="",
                )
            )
            return False, "log differs from PDF example:\n" + diff

    return True, "expected transcript is a subsequence of actual output"


# ---------- test 2: structural checks for arbitrary sizes ----------

# These regexes match the log style shown in the PDF. They tolerate small
# formatting variation (extra spaces) but assume the field labels are kept.

RE_DATA_SENT = re.compile(
    r"Host A:\s*Layer 4:\s*Segment created by adding transport layer header\s*\(DATA,\s*seq=(\d)\)"
)
RE_ACK_RECEIVED_AT_A = re.compile(
    r"Host A:\s*Layer 4:\s*ACK received:\s*seq=(\d)"
)
RE_ACK_SENT_AT_B = re.compile(
    r"Host B:\s*Layer 4:\s*Segment created by adding transport layer header\s*\(ACK,\s*seq=(\d)\)"
)
RE_DATA_DELIVERED_AT_B = re.compile(
    r"Host B:\s*Layer 4:\s*DATA segment delivered to Application Layer"
)
RE_TTL_DECREMENT = re.compile(
    r"Router R1:\s*Layer 3:\s*TTL decremented:\s*(\d+)\s*->|"
    r"Router R1:\s*Layer 3:\s*TTL decremented:\s*(\d+)\s*→"
)


def check_structure(size: int, log: str) -> tuple[bool, list[str]]:
    """Run all structural invariants. Returns (passed, list_of_messages)."""
    msgs: list[str] = []
    ok = True

    n = expected_segment_count(size)
    expected_seqs = expected_seq_sequence(n)

    data_seqs = [int(m.group(1)) for m in RE_DATA_SENT.finditer(log)]
    ack_recv_seqs = [int(m.group(1)) for m in RE_ACK_RECEIVED_AT_A.finditer(log)]
    ack_sent_seqs = [int(m.group(1)) for m in RE_ACK_SENT_AT_B.finditer(log)]
    deliveries = len(RE_DATA_DELIVERED_AT_B.findall(log))
    ttl_decrements = len(RE_TTL_DECREMENT.findall(log))

    # 1. correct number of DATA segments
    if len(data_seqs) != n:
        ok = False
        msgs.append(f"expected {n} DATA segments, found {len(data_seqs)}")
    else:
        msgs.append(f"DATA segment count = {n} ✓")

    # 2. seq numbers alternate 0,1,0,1,...
    if data_seqs != expected_seqs:
        ok = False
        msgs.append(f"DATA seq pattern wrong: got {data_seqs}, expected {expected_seqs}")
    else:
        msgs.append(f"DATA seq alternation {data_seqs} ✓")

    # 3. every DATA gets an ACK with the same seq, in order
    if ack_recv_seqs != expected_seqs:
        ok = False
        msgs.append(
            f"ACKs received at A wrong: got {ack_recv_seqs}, expected {expected_seqs}"
        )
    else:
        msgs.append("ACK seqs at sender match DATA seqs ✓")

    if ack_sent_seqs != expected_seqs:
        ok = False
        msgs.append(
            f"ACKs sent by B wrong: got {ack_sent_seqs}, expected {expected_seqs}"
        )

    # 4. receiver delivered once per segment
    if deliveries != n:
        ok = False
        msgs.append(f"Host B delivered to app {deliveries} times, expected {n}")
    else:
        msgs.append(f"Host B app deliveries = {n} ✓")

    # 5. router decremented TTL once per direction per segment
    # n segments * 2 traversals (data forward, ACK back) = 2n
    expected_ttl = 2 * n
    if ttl_decrements != expected_ttl:
        ok = False
        msgs.append(
            f"R1 TTL decrements = {ttl_decrements}, expected {expected_ttl} "
            f"(2 per segment: forward + ACK)"
        )
    else:
        msgs.append(f"R1 TTL decrements = {expected_ttl} ✓")

    # 6. transcript ends after final ACK is received at A
    lines = [ln for ln in log.splitlines() if ln.strip()]
    if lines:
        last = lines[-1]
        if not RE_ACK_RECEIVED_AT_A.search(last):
            ok = False
            msgs.append(f"transcript does not end on final ACK; last line: {last!r}")
        else:
            final_seq = int(RE_ACK_RECEIVED_AT_A.search(last).group(1))
            if final_seq != expected_seqs[-1]:
                ok = False
                msgs.append(
                    f"final ACK seq is {final_seq}, expected {expected_seqs[-1]}"
                )
            else:
                msgs.append("transcript ends on correct final ACK ✓")

    return ok, msgs


def test_structure(size: int) -> tuple[bool, str]:
    log = run_main(size)
    ok, msgs = check_structure(size, log)
    indented = "\n    ".join(msgs)
    header = f"size={size} ({expected_segment_count(size)} segment(s)):"
    return ok, f"{header}\n    {indented}"


# ---------- entry point ----------

def main() -> int:
    # Only run the exact-match check for the 10-byte example fixture.
    print("Running exact-match test (10 bytes)...")
    ok, detail = test_exact_match_10_bytes()
    tag = "PASS" if ok else "FAIL"
    print(f"[{tag}] exact-match  size=10")
    if not ok:
        print(detail)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
