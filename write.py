from PIL import Image
import datetime
import argparse
import os
import subprocess
import random
import math
import tempfile
import shutil


def create_commit(cwd: str, date: datetime.date) -> None:
    filepath = os.path.join(cwd, "file")
    with open(filepath, "w") as file:
        file.write(str(random.random()))
    call_git(cwd, "add", filepath)
    dateStr = date.strftime("%a %b %d %I:%M %Y +0100")
    call_git(cwd, "commit", "-m", "automated commit", "--date", dateStr)


def call_git(cwd: str, *cmds: str) -> str:
    return call_proc(cwd, "git", *cmds)


def call_proc(cwd: str, *cmds: str) -> str:
    proc = subprocess.run(list(cmds), cwd=cwd, stdout=subprocess.PIPE)
    return proc.stdout.decode()


def file_path(path):
    """From https://stackoverflow.com/a/54547257"""
    if os.path.isfile(path):
        return path
    else:
        raise argparse.ArgumentTypeError(
            f"readable_dir:{path} is not a valid file path"
        )


def get_lum(col: tuple[int, int, int]) -> float:
    R, G, B = col
    return math.sqrt(0.299 * (R**2) + 0.587 * (G**2) + 0.114 * (B**2))


def dir_path(path):
    """From https://stackoverflow.com/a/54547257"""
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(
            f"readable_dir:{path} is not a valid directory path"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "repo_name",
        type=str,
        help="Name of dummy repository (history in this repo WILL BE OVERWRITTEN)",
    )
    parser.add_argument(
        "image_path",
        type=file_path,
        help="Path to image to use as the commit pattern. Will be cropped to 52x7",
    )
    parser.add_argument(
        "year",
        type=int,
        help="Year to write message to",
    )
    args = parser.parse_args()
    img = Image.open(args.image_path)
    img = img.convert("RGB")

    # Turns out calendar operations are kinda complicated :(
    start_date = datetime.date(args.year, 1, 1)
    x_offset = 0
    # Makes x start at 0 even if Jan 1 is a Sunday
    if int(start_date.strftime("%U")) == 1:
        x_offset = -1
    y_offset = (start_date.weekday()) % 7
    y = (start_date.weekday() + 1 + y_offset) % 7
    x = int(start_date.strftime("%U")) + x_offset
    offset = datetime.timedelta(days=0)
    curr_date = start_date + offset
    vals = []
    max_val = 0
    while x < 52:
        val = get_lum(img.getpixel((x, y)))  # type: ignore
        vals.append(val)
        if val > max_val:
            max_val = val

        offset = datetime.timedelta(days=offset.days + 1)
        curr_date = start_date + offset
        x = int(curr_date.strftime("%U")) + x_offset
        # 0 is Monday, we want 0 to be Sunday
        y = (curr_date.weekday() + 1 + y_offset) % 7

    # Add commits using the normalised pixel value
    tmp = tempfile.mkdtemp()
    print(tmp)
    call_proc(tmp, "gh", "repo", "delete", args.repo_name, "--yes")
    call_git(tmp, "init")
    call_proc(
        tmp,
        "gh",
        "repo",
        "create",
        args.repo_name,
        "--public",
        "-r",
        "origin",
        "--source",
        ".",
    )
    offset = datetime.timedelta(days=0)
    curr_date = start_date + offset
    for i, val in enumerate(vals):
        print(f"\r{i+1}/{len(vals)} ", end="")
        for _ in range(int(10 * val / max_val)):
            create_commit(tmp, curr_date)
        offset = datetime.timedelta(days=offset.days + 1)
        curr_date = start_date + offset
    print()

    call_git(tmp, "push")
    os.system(f'rmdir /S /Q "{tmp}"')

