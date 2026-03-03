import os
import subprocess
import threading
import time
from pathlib import Path
from analysis.results import main as analysis_main


REPO_ROOT = Path(__file__).resolve().parent
RESULTS_DIR = REPO_ROOT / "results"
SERVICE_NAME = "stress-service"
K8S_PORT = "8080"
POLL_INTERVAL_S = 10
POST_K6_DELAY_S = 5  # wait after k6 so final poll sees newly Ready pods


def capture_replicas_at_start() -> None:
    """Write current replica count to results/replicas_at_start.txt so we can tell if HPA scaled during the test."""
    if os.environ.get("K8S") != "1":
        return
    try:
        from analysis.collect import get_replica_count
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        (RESULTS_DIR / "replicas_at_start.txt").write_text(str(get_replica_count(SERVICE_NAME)))
    except Exception:
        pass


def _k8s_poller_loop(stop_event: threading.Event, samples: list, start_time: float) -> None:
    """Background: poll replicas + kubectl top every POLL_INTERVAL_S, write k8s-timeseries.json."""
    from analysis.collect import poll_k8s_sample
    time.sleep(5)  # first poll at t=5
    while not stop_event.is_set():
        t = int(time.monotonic() - start_time)
        sample = poll_k8s_sample(SERVICE_NAME)
        samples.append({"t": t, "replicas": sample["replicas"], "cpu_m": sample["cpu_m"], "mem_mib": sample["mem_mib"]})
        ts_path = RESULTS_DIR / "k8s-timeseries.json"
        try:
            import json
            RESULTS_DIR.mkdir(parents=True, exist_ok=True)
            ts_path.write_text(json.dumps(samples, indent=2))
        except OSError:
            pass
        stop_event.wait(POLL_INTERVAL_S)


def run_k6_basic() -> int:
    """Run k6; return exit code. When K8S=1, start port-forward and live-poll K8s metrics."""
    use_k8s = os.environ.get("K8S") == "1"
    pf_proc = None
    poller_stop = threading.Event()
    samples = []
    poller_thread = None

    if use_k8s:
        pf_proc = subprocess.Popen(
            ["kubectl", "port-forward", f"svc/{SERVICE_NAME}", f"{K8S_PORT}:80"],
            cwd=REPO_ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(1.5)
        print(f"Port-forward svc/{SERVICE_NAME} -> localhost:{K8S_PORT} (k6 will hit pods)")
        poller_thread = threading.Thread(
            target=_k8s_poller_loop,
            args=(poller_stop, samples, time.monotonic()),
            daemon=True,
        )
        poller_thread.start()

    env = os.environ.copy()
    if use_k8s:
        env["BASE_URL"] = f"http://localhost:{K8S_PORT}"
    cmd = [
        "k6",
        "run",
        "--summary-export=./results/k6-summary.json",
        "load-tests/k6/basic.js",
    ]
    out = subprocess.run(cmd, cwd=REPO_ROOT, env=env, check=False)

    if poller_thread is not None:
        poller_stop.set()
        poller_thread.join(timeout=15)
        time.sleep(POST_K6_DELAY_S)
        from analysis.collect import poll_k8s_sample
        import json
        sample = poll_k8s_sample(SERVICE_NAME)
        last_t = samples[-1]["t"] + POST_K6_DELAY_S if samples else 0
        samples.append({"t": last_t, "replicas": sample["replicas"], "cpu_m": sample["cpu_m"], "mem_mib": sample["mem_mib"]})
        try:
            (RESULTS_DIR / "k8s-timeseries.json").write_text(json.dumps(samples, indent=2))
        except OSError:
            pass

    if pf_proc is not None:
        pf_proc.terminate()
        pf_proc.wait(timeout=5)
    if out.returncode != 0:
        print(f"k6 exited with {out.returncode} (thresholds or errors). Analysis will still run.")
    return out.returncode


def run_analysis() -> None:
    """Start LLM based analysis."""
    analysis_main()


if __name__ == "__main__":
    capture_replicas_at_start()
    run_k6_basic()
    run_analysis()

