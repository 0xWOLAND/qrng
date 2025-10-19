import math
from itertools import product
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import RYGate
from qiskit_aer import AerSimulator

def random_sample(N: int) -> QuantumCircuit:
    k = math.ceil(math.log2(N))
    qc = QuantumCircuit(k)

    def count(N, k, p):
        t = len(p); v = 0
        for b in p: v = (v << 1) | b
        span = 1 << (k - t)
        lo = v << (k - t); hi = lo + span - 1
        if lo >= N: return 0
        return max(0, min(N, hi + 1) - lo)

    for t in range(k):
        for p in product([0, 1], repeat=t):
            c = count(N, k, p)
            if c == 0: continue
            c0 = count(N, k, p + (0,))
            c1 = c - c0
            if c0 == 0 or c1 == 0: continue

            theta = 2 * math.acos((c0 / c) ** 0.5)

            if t == 0:
                qc.ry(theta, 0)
            else:
                # Control directly on the prefix pattern p via ctrl_state
                ctrl_qubits = list(range(t))
                target = t
                ctrl_state = ''.join(str(bit) for bit in p)  # e.g. p=(0,1) -> "01"
                qc.append(RYGate(theta).control(t, ctrl_state=ctrl_state),
                          ctrl_qubits + [target])

    return qc

if __name__ == "__main__":
    N = 7
    qc = random_sample(N)
    qc.measure_all()
    try:
        qc.draw('mpl').savefig("circuit.png", dpi=300)
    except Exception:
        pass

    sim = AerSimulator()
    job = sim.run(transpile(qc, sim, optimization_level=3), shots=5000)
    counts = job.result().get_counts()

    print("Measurement counts:")
    for state, c in sorted(counts.items(), key=lambda x: int(x[0][::-1], 2)):
        print(f"{int(state[::-1], 2):2d}: {c}")
