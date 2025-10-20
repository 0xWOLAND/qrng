import math
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt

def random_sample(N: int) -> QuantumCircuit:
    k = N - 1  # Number of qubits
    qc = QuantumCircuit(k)
    for i in range(k):
        # Probability of measuring 1 given all previous are 1
        prob = (k - i) / (k - i + 1)
        theta = 2 * math.asin(prob**0.5)

        if i == 0:
            qc.ry(theta, i)
        else:
            # Controlled rotation on previous qubit (nested 2-qubit control)
            qc.cry(theta, i-1, i)
    
    return qc

if __name__ == "__main__":
    N = 9
    qc = random_sample(N)
    qc.measure_all()

    # Draw and save as picture
    fig = qc.draw('mpl', fold=0)
    fig.savefig("circuit.png", dpi=300)
    plt.close(fig)  # Close figure to free memory

    # Simulate
    sim = AerSimulator()
    job = sim.run(qc, shots=5000)
    counts = job.result().get_counts()

    print("Measurement counts:")
    for state, c in sorted(counts.items(), key=lambda x: int(x[0][::-1], 2)):
        print(f"{int(state[::-1], 2):2d}: {c}")
