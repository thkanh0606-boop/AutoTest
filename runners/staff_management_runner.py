import os
import subprocess
import sys
from pathlib import Path


def run_staff_management_test(worker=None, pytest_args=None):
    """Run the Nhân sự Selenium suite from the PySide worker."""
    root_dir = Path(__file__).resolve().parents[1]
    args = pytest_args or ["tests/test_staff_page.py", "-q"]

    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")

    if worker:
        worker.log_signal.emit("Đang chạy bộ test Nhân sự...")
        worker.progress_signal.emit(20)

    process = subprocess.run(
        [sys.executable, "-m", "pytest", *args],
        cwd=root_dir,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )

    output = "\n".join(
        part.strip()
        for part in (process.stdout, process.stderr)
        if part and part.strip()
    )

    if worker:
        worker.progress_signal.emit(90)
        if output:
            worker.log_signal.emit(output[-4000:])

    status = "PASSED" if process.returncode == 0 else "FAILED"
    return {
        "status": status,
        "message": "Bộ test Nhân sự đã chạy xong.",
        "returncode": process.returncode,
        "output": output,
        "steps": [
            {
                "test_case": "tests/test_staff_page.py",
                "expected": "8 testcase Nhân sự chạy thành công",
                "actual": output[-1200:] if output else "Không có output",
                "result": "PASS" if process.returncode == 0 else "FAIL",
            }
        ],
    }
