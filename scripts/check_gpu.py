from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import sys
from pathlib import Path

CUDA_ERROR_NAMES = {
    0: "CUDA_SUCCESS",
    35: "CUDA_ERROR_INSUFFICIENT_DRIVER",
    100: "CUDA_ERROR_NO_DEVICE",
    804: "CUDA_ERROR_FORWARD_COMPATIBILITY_NOT_SUPPORTED",
}

TENSORFLOW_CHECK = r"""
import tensorflow as tf
print(f"tensorflow.version\t{tf.__version__}")
print(f"tensorflow.built_with_cuda\t{tf.test.is_built_with_cuda()}")
gpus = tf.config.list_physical_devices("GPU")
print(f"tensorflow.gpus\t{gpus}")
if gpus:
    with tf.device("/GPU:0"):
        result = tf.matmul(tf.ones((64, 64)), tf.ones((64, 64)))
    print(f"tensorflow.matmul_device\t{result.device}")
    print(f"tensorflow.matmul_sum\t{float(tf.reduce_sum(result))}")
"""

TORCH_CHECK = r"""
import torch
print(f"torch.version\t{torch.__version__}")
print(f"torch.cuda_compiled\t{torch.version.cuda}")
print(f"torch.cuda_available\t{torch.cuda.is_available()}")
print(f"torch.cuda_device_count\t{torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"torch.cuda_device_0\t{torch.cuda.get_device_name(0)}")
    result = torch.ones((64, 64), device="cuda") @ torch.ones((64, 64), device="cuda")
    torch.cuda.synchronize()
    print(f"torch.matmul_device\t{result.device}")
    print(f"torch.matmul_sum\t{float(result.sum())}")
"""


def run_command(command: list[str]) -> tuple[int | None, str]:
    if shutil.which(command[0]) is None:
        return None, "missing"
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    output = (result.stdout or result.stderr).strip().replace("\n", " | ")
    return result.returncode, output or "ok"


def libcuda_status(lib_name: str) -> str:
    try:
        cuda = ctypes.CDLL(lib_name)
        cuda.cuInit.argtypes = [ctypes.c_uint]
        cuda.cuInit.restype = ctypes.c_int
        code = cuda.cuInit(0)
        return f"loaded; cuInit={code} ({CUDA_ERROR_NAMES.get(code, 'UNKNOWN')})"
    except Exception as exc:
        return f"error: {type(exc).__name__}: {exc}"


def run_python_check(name: str, code: str) -> list[str]:
    result = subprocess.run(
        [sys.executable, "-c", code],
        check=False,
        capture_output=True,
        text=True,
        timeout=180,
        env={**os.environ, "TF_CPP_MIN_LOG_LEVEL": "2"},
    )
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if result.returncode != 0:
        stderr_tail = " | ".join(result.stderr.strip().splitlines()[-5:])
        lines.append(f"{name}\terror: exit={result.returncode}; {stderr_tail}")
    return lines


def main() -> int:
    print("gpu_device")
    for path in ("/dev/dxg", "/dev/nvidia0", "/dev/nvidiactl"):
        print(f"{path}\t{'present' if Path(path).exists() else 'missing'}")

    print("\ncommands")
    for name, command in {
        "nvidia-smi": ["nvidia-smi"],
        "nvcc": ["nvcc", "--version"],
    }.items():
        code, output = run_command(command)
        status = "missing" if code is None else f"exit={code}"
        print(f"{name}\t{status}\t{output}")

    print("\nlibcuda")
    for library in ("libcuda.so.1", "/usr/lib/wsl/lib/libcuda.so.1"):
        print(f"{library}\t{libcuda_status(library)}")

    print("\nframeworks")
    lines = run_python_check("tensorflow", TENSORFLOW_CHECK)
    lines.extend(run_python_check("torch", TORCH_CHECK))
    print("\n".join(lines))

    healthy = any("tensorflow.matmul_device" in line for line in lines) and any(
        "torch.matmul_device" in line for line in lines
    )
    return 0 if healthy else 1


if __name__ == "__main__":
    raise SystemExit(main())

