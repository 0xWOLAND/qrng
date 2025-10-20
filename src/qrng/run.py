import argparse, os
from enum import Enum, auto
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import naiive, anticontrol, complement, main, exhaustive  # import exhaustive


class Version(Enum):
    V0 = auto()  # new version
    V1 = auto()
    V2 = auto()
    V3 = auto()
    V4 = auto()


CIRCUIT_GENERATORS = {
    Version.V0: exhaustive.random_sample,  # use exhaustive version
    Version.V1: naiive.random_sample,
    Version.V2: anticontrol.random_sample,
    Version.V3: complement.random_sample,
    Version.V4: main.uniform_first_N,
}


def run_simulation(N, version, shots):
    os.makedirs("images", exist_ok=True)
    qc = CIRCUIT_GENERATORS[version](N)
    qc.measure_all()

    img_name = f"images/circuit_{version.name.lower()}.png"
    hist_name = f"images/histogram_{version.name.lower()}.png"

    try:
        qc.draw("mpl").savefig(img_name, dpi=300)
    except:
        pass

    sim = AerSimulator()
    qc_opt = transpile(qc, sim, optimization_level=3 if version != Version.V1 else 0)
    counts = sim.run(qc_opt, shots=shots).result().get_counts()

    plt.figure()
    plot_histogram(counts).savefig(hist_name, dpi=300)
    plt.close()

    print(f"--- Version {version.name.lower()}, N={N}, Shots={shots} ---")
    for s, c in sorted(counts.items(), key=lambda x: int(x[0][::-1], 2)):
        print(f"{int(s[::-1], 2):2d}: {c}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("N", type=int, nargs="?", default=9)
    p.add_argument(
        "version", choices=["v0", "v1", "v2", "v3", "v4"], nargs="?", default="v4"
    )  # add v0
    p.add_argument("--shots", type=int, default=5000)
    args = p.parse_args()
    run_simulation(args.N, Version[args.version.upper()], args.shots)
