import math
from itertools import product
from qiskit import QuantumCircuit
from qiskit.circuit.library import RYGate
from qiskit_aer import AerSimulator
from qiskit import transpile


def random_sample(N: int) -> QuantumCircuit:
    k = math.ceil(math.log2(N))
    qc = QuantumCircuit(k)

    def count(N, k, p):
        t = len(p)
        v = 0
        for b in p:
            v = (v << 1) | b
        span = 1 << (k - t)
        lo = v << (k - t)
        hi = lo + span - 1
        if lo >= N:
            return 0
        return max(0, min(N, hi + 1) - lo)

    for t in range(k):
        for p in product([0, 1], repeat=t):
            c = count(N, k, p)
            if c == 0:
                continue
            c0 = count(N, k, p + (0,))
            c1 = c - c0
            if c0 == 0 or c1 == 0:
                continue
            theta = 2 * math.acos((c0 / c) ** 0.5)
            for qi, bit in zip(range(t), p):
                if bit == 0:
                    qc.x(qi)
            if t == 0:
                qc.ry(theta, 0)
            else:
                qc.append(RYGate(theta).control(t), list(range(t)) + [t])
            for qi, bit in zip(range(t), p):
                if bit == 0:
                    qc.x(qi)

    return qc


# N = 6
# qc = random_sample(N)
# qc.measure_all()
# qc.draw('mpl').savefig("circuit.png", dpi=300)


# sim = AerSimulator()
# job = sim.run(transpile(qc, sim), shots=5000)
# counts = job.result().get_counts()

# print("Measurement counts:")
# for state, c in sorted(
#     counts.items(), key=lambda x: int(x[0][::-1], 2)
# ):  # reverse bitstring
#     print(f"{int(state[::-1], 2):2d}: {c}")
