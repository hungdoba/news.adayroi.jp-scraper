from typing import Any, Callable
import subprocess
import logging
logger = logging.getLogger(__name__)


def execute_sequential(exe: str, callback: Callable[[], Any]) -> None:
    logger.info(f"Launching application: {exe}")

    # Use subprocess to run the program and wait for it to complete
    process = subprocess.Popen(exe)
    return_code = process.wait()

    logger.info(f"Application closed with status: {return_code}")

    # Check if the program closed successfully
    if return_code == 0:
        logger.info("Executing callback function")
        try:
            callback()
            logger.info("Callback function completed!")
        except Exception as e:
            raise RuntimeError(f"Callback failed: {str(e)}")
    else:
        logger.error("Application closed with an error. Aborting sequence.")
        raise subprocess.SubprocessError(
            f"Application failed with return code {return_code}")
