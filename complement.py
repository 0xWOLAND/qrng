import math
from itertools import product
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import RYGate
from qiskit_aer import AerSimulator

def random_sample(N: int) -> QuantumCircuit:
    k = math.ceil(math.log2(N))
    qc = QuantumCircuit(k)

    # count how many x < N share prefix p (p is a tuple of bits, LSB-first)
    def count(p):
        t = len(p); v = 0
        for b in p: v = (v << 1) | b
        span = 1 << (k - t)
        lo = v << (k - t); hi = lo + span - 1
        if lo >= N: return 0
        return max(0, min(N, hi + 1) - lo)

    for t in range(k):
        # baseline even split on the next bit
        qc.h(t)

        # corrections where split isn't 50-50
        for p in product([0, 1], repeat=t):
            c = count(p)
            if c == 0:
                continue
            c0 = count(p + (0,))
            c1 = c - c0

            if c0 == 0 or c1 == 0:
                theta = 0.0 if c0 == c else math.pi
            else:
                theta = 2 * math.acos((c0 / c) ** 0.5)

            delta = theta - (math.pi / 2)
            if abs(delta) < 1e-12:
                continue

            if t == 0:
                qc.ry(delta, 0)
            else:
                ctrl_qubits = list(range(t))   # [0, 1, ..., t-1]
                target = t
                # IMPORTANT: ctrl_state is MSB->LSB aligned to ctrl_qubits order,
                # while p is LSB-first; so reverse p here.
                ctrl_state = int(''.join(str(bit) for bit in reversed(p)), 2)
                qc.append(
                    RYGate(delta).control(t, ctrl_state=ctrl_state),
                    ctrl_qubits + [target]
                )

    return qc

if __name__ == "__main__":
    N = 9
    qc = random_sample(N)
    qc.measure_all()

    try:
        qc.draw('mpl').savefig("circuit_complement_even_split.png", dpi=300)
    except Exception:
        pass

    sim = AerSimulator()
    qc_opt = transpile(qc, sim, optimization_level=3)
    res = sim.run(qc_opt, shots=5000).result().get_counts()

    print("Measurement counts:")
    for state, c in sorted(res.items(), key=lambda x: int(x[0][::-1], 2)):
        print(f"{int(state[::-1], 2):2d}: {c}")
