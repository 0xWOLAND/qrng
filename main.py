import math
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import HGate, RYGate
from qiskit_aer import AerSimulator

def _append_ctrl(qc, gate, ctrls, target, state):
    if ctrls:
        qc.append(gate.control(len(ctrls), ctrl_state=int(state[::-1], 2)), ctrls + [target])
    else:
        qc.append(gate, [target])

def _prep(qc, qs, N, ctrls=None, state=""):
    ctrls = ctrls or []
    if N <= 1 or not qs: return
    full = 1 << len(qs)
    if N == full:
        for q in qs: _append_ctrl(qc, HGate(), ctrls, q, state)
        return

    msb, rest = qs[0], qs[1:]
    half = 1 << (len(qs) - 1)
    left, right = min(N, half), N - min(N, half)
    theta = 2 * math.acos((left / N) ** 0.5)
    _append_ctrl(qc, RYGate(theta), ctrls, msb, state)

    if left:  _prep(qc, rest, left,  ctrls + [msb], state + "0")
    if right: _prep(qc, rest, right, ctrls + [msb], state + "1")

def uniform_first_N(N):
    k = math.ceil(math.log2(N))
    qc = QuantumCircuit(k)
    _prep(qc, list(range(k)), N)
    return qc

if __name__ == "__main__":
    N = 7
    qc = uniform_first_N(N)
    qc.measure_all()
    qc.draw('mpl').savefig("circuit.png", dpi=300)

    sim = AerSimulator()
    res = sim.run(transpile(qc, sim, optimization_level=3), shots=8000).result()
    counts = res.get_counts()

    print(f"Uniform over 0..{N-1}:")
    for s, c in sorted(counts.items(), key=lambda x: int(x[0][::-1], 2)):
        print(f"{int(s[::-1], 2):2d}: {c}")
