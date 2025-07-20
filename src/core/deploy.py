import os
import datetime
import subprocess
import glob


def build_next_app():
    try:
        nextjs_dir = os.environ.get('NEXTJS_DIR')
        if not nextjs_dir:
            # Fallback to default if environment variable not set
            nextjs_dir = "E:/Programming/Nextjs/news.adayroi.jp"
            print(
                f"NEXTJS_DIR environment variable not set, using default: {nextjs_dir}")

        if not os.path.exists(nextjs_dir):
            raise FileNotFoundError(
                f"NextJS directory does not exist: {nextjs_dir}")

        command = r"C:\Program Files\nodejs\npm.cmd"
        args = ["run", "build"]

        _run_command_and_stream_output(command, args, nextjs_dir)
        return True
    except Exception as e:
        print(f"Error building Next.js app: {e}")
        return False


def git_push_next_app():
    nextjs_dir = os.environ.get('NEXTJS_DIR')
    if not nextjs_dir:
        # Fallback to default if environment variable not set
        nextjs_dir = "E:/Programming/Nextjs/news.adayroi.jp"
        print(
            f"NEXTJS_DIR environment variable not set, using default: {nextjs_dir}")

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
                    print(
                        f"Removed file with problematic name: {file[:50]}...")
                except OSError as e:
                    print(
                        f"Could not remove problematic file {file[:50]}...: {e}")


def _run_command_and_stream_output(command, args, cwd):
    process = subprocess.Popen(
        [command] + args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8"  # <-- Add this line
    )

    for line in process.stdout:
        print(line, end='')

    process.wait()
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, command)
