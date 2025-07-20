import subprocess
from typing import Any, Callable


def execute_sequential(exe: str, callback: Callable[[], Any]) -> None:
    print(f"Launching application: {exe}")

    # Use subprocess to run the program and wait for it to complete
    process = subprocess.Popen(exe)
    return_code = process.wait()

    print(f"Application closed with status: {return_code}")

    # Check if the program closed successfully
    if return_code == 0:
        print("Executing callback function")
        try:
            callback()
            print("Callback function completed!")
        except Exception as e:
            raise RuntimeError(f"Callback failed: {str(e)}")
    else:
        print("Application closed with an error. Aborting sequence.")
        raise subprocess.SubprocessError(
            f"Application failed with return code {return_code}")
