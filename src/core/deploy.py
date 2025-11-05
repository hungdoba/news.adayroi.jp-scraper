import glob
import subprocess
import datetime
import os
import logging
from exceptions import ConfigurationError

logger = logging.getLogger(__name__)


def build_next_app():
    """
    Build the Next.js application.

    Returns:
        bool: True if build succeeded, False otherwise

    Raises:
        ConfigurationError: If NEXTJS_DIR is not configured
    """
    try:
        nextjs_dir = os.environ.get('NEXTJS_DIR')
        if not nextjs_dir:
            raise ConfigurationError(
                "NEXTJS_DIR environment variable is not set. "
                "Please configure it in your .env file."
            )

        if not os.path.exists(nextjs_dir):
            raise FileNotFoundError(
                f"NextJS directory does not exist: {nextjs_dir}"
            )

        command = r"C:\Program Files\nodejs\npm.cmd"
        args = ["run", "build"]

        _run_command_and_stream_output(command, args, nextjs_dir)
        return True
    except Exception as e:
        logger.error(f"Error building Next.js app: {e}")
        return False


def git_push_next_app():
    """
    Commit and push changes to the Next.js repository.

    Raises:
        ConfigurationError: If NEXTJS_DIR is not configured
    """
    nextjs_dir = os.environ.get('NEXTJS_DIR')
    if not nextjs_dir:
        raise ConfigurationError(
            "NEXTJS_DIR environment variable is not set. "
            "Please configure it in your .env file."
        )

    if not os.path.exists(nextjs_dir):
        raise FileNotFoundError(
            f"NextJS directory does not exist: {nextjs_dir}")

    # Clean up files with problematic names before git operations
    _cleanup_problematic_files(nextjs_dir)

    datetime_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"Update blog {datetime_str}"

    _run_command_and_stream_output("git", ["add", "."], nextjs_dir)
    _run_command_and_stream_output(
        "git", ["commit", "-m", commit_message], nextjs_dir)
    _run_command_and_stream_output("git", ["push"], nextjs_dir)


def _cleanup_problematic_files(nextjs_dir):
    """Remove files with names that are too long for Git/filesystem."""
    max_path_length = 250  # Conservative limit for Windows

    # Check all files in the directory
    for root, dirs, files in os.walk(nextjs_dir):
        for file in files:
            full_path = os.path.join(root, file)
            # Check if the full path or just filename is too long
            if len(full_path) > max_path_length or len(file) > 200:
                try:
                    os.remove(full_path)
                    logger.info(
                        f"Removed file with problematic name: {file[:50]}...")
                except OSError as e:
                    logger.error(
                        f"Could not remove problematic file {file[:50]}...: {e}")


def _run_command_and_stream_output(command, args, cwd):
    """Run a command and stream its output to the logger."""
    process = subprocess.Popen(
        [command] + args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,  # Capture stderr separately
        text=True,
        bufsize=1,
        encoding="utf-8"
    )

    # Capture both stdout and stderr
    stdout_lines = []
    stderr_lines = []

    if process.stdout:
        for line in process.stdout:
            line = line.rstrip()
            stdout_lines.append(line)
            logger.info(line)

    if process.stderr:
        for line in process.stderr:
            line = line.rstrip()
            stderr_lines.append(line)
            logger.error(line)

    process.wait()

    if process.returncode != 0:
        error_msg = f"Command failed with exit code {process.returncode}"
        if stderr_lines:
            error_msg += f"\nStderr output:\n" + \
                "\n".join(stderr_lines[-10:])  # Last 10 lines
        if stdout_lines:
            error_msg += f"\nStdout output:\n" + \
                "\n".join(stdout_lines[-10:])  # Last 10 lines
        raise subprocess.CalledProcessError(
            process.returncode, command, output=error_msg)
