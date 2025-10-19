import math
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import RYGate, HGate
from qiskit_aer import AerSimulator

def block(n, N):
    qc = QuantumCircuit(n)
    def build(qs, N):
        k = len(qs)
        if N == 0 or k == 0: return
        if N == (1 << k):
            for q in qs: qc.h(q); return
        m = 1 << (k-1); msb, low = qs[-1], qs[:-1]
        if N <= m: build(low, N); return
        L, R = m, N - m
        qc.ry(2*math.acos((L/N)**0.5), msb)
        for q in low: qc.append(HGate().control(1, ctrl_state='0'), [msb, q])
        if R: qc.append(block(len(low), R).control(1, ctrl_state='1'), [msb] + low)
    build(list(range(n)), N)
    return qc.to_gate()

def random_sample(N: int) -> QuantumCircuit:
    k = math.ceil(math.log2(N))
    qc = QuantumCircuit(k)
    qc.append(block(k, N), range(k))
    return qc

if __name__ == "__main__":
    N = 9
    qc = random_sample(N)
    qc.measure_all()
    qc.draw('mpl').savefig("circuit.png", dpi=300)
    sim = AerSimulator()
    res = sim.run(transpile(qc, sim, optimization_level=3), shots=5000).result().get_counts()
    for s,c in sorted(res.items(), key=lambda x:int(x[0][::-1],2)):
        print(int(s[::-1],2), c)
