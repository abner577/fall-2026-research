"""Execute the notebook and save outputs and three Seaborn/Matplotlib PNGs.

Run with the workspace .venv interpreter. The notebook is the editable source.
No persistent Jupyter kernel is registered.
"""
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager


def main():
    folder = Path(__file__).resolve().parent
    notebook_path = folder / "comparison-matrices.ipynb"
    notebook = nbformat.read(notebook_path, as_version=4)
    with TemporaryDirectory(prefix="comparison-kernel-") as temporary:
        kernel = Path(temporary) / "comparison-example"
        kernel.mkdir()
        (kernel / "kernel.json").write_text(json.dumps({
            "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
            "display_name": "Comparison example", "language": "python",
        }), encoding="utf-8")
        manager = KernelManager(
            kernel_name="comparison-example",
            kernel_spec_manager=KernelSpecManager(kernel_dirs=[temporary]),
        )
        runtime = folder.parent / ".venv" / "comparison-runtime"
        runtime.mkdir(parents=True, exist_ok=True)
        os.environ["JUPYTER_RUNTIME_DIR"] = str(runtime)
        os.environ["MPLCONFIGDIR"] = str(runtime / "matplotlib")
        os.environ["IPYTHONDIR"] = str(runtime / "ipython")
        try:
            NotebookClient(notebook, km=manager, timeout=120,
                           resources={"metadata": {"path": str(folder)}}).execute()
        finally:
            if manager.has_kernel:
                manager.shutdown_kernel(now=True)
    nbformat.validate(notebook)
    nbformat.write(notebook, notebook_path)
    print("Executed notebook; saved outputs and three Seaborn/Matplotlib PNG exports.")


if __name__ == "__main__":
    main()
