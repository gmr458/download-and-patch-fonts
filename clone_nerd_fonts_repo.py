"""Clone ryanoasis/nerd-fonts repo from GitHub"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

HOME_DIR = os.getenv("HOME")
URL_REPO = "https://github.com/ryanoasis/nerd-fonts.git"
DEST_DIR = f"{HOME_DIR}/nerd-fonts"
URL_API = "https://api.github.com/repos/ryanoasis/nerd-fonts/releases/latest"


def main():
    parser = argparse.ArgumentParser(
        description="This script clone the latest release of github.com/ryanoasis/nerd-fonts"
    )
    parser.add_argument(
        "dest",
        nargs="?",
        default=DEST_DIR,
        help="Destination directory to clone the repository",
    )

    args = parser.parse_args()

    req = urllib.request.Request(URL_API)

    nf_latest_version = ""

    try:
        with urllib.request.urlopen(req) as response:
            data = json.load(response)
            nf_latest_version = data["tag_name"]
    except Exception as err:
        print(f"Error {err}, Type: {type(err)}")
        sys.exit()

    if nf_latest_version == "":
        print("Could not get nerd-fonts latest tag")
        sys.exit()

    check_requirements()
    clone_nerd_fonts_repo(args.dest, nf_latest_version)


def check_requirements():
    """Check if Git is installed"""
    if shutil.which("git") is None:
        print("Git is required.")
        sys.exit(0)


def clone_nerd_fonts_repo(dest_dir: str, nf_latest_version: str):
    """Clone ryanoasis/nerd-fonts repo from GitHub"""
    if os.path.exists(dest_dir):
        content = os.listdir(dest_dir)
        if len(content) > 0:
            print("The destination directory has other directories or files.")
            sys.exit(0)

    print(f"Cloning {URL_REPO}")
    with subprocess.Popen(
        ["git", "clone", "--filter=blob:none", "--sparse", URL_REPO, dest_dir],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        process.communicate()
        print(f"{URL_REPO} cloned.\n")

    with subprocess.Popen(
        [
            "git",
            "sparse-checkout",
            "add",
            "bin",
            "css",
            "src/glyphs",
            "src/svgs",
        ],
        cwd=dest_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        process.communicate()
        print("Directories bin, css, src/glyphs and src/svgs added.\n")

    with subprocess.Popen(
        [
            "git",
            "checkout",
            nf_latest_version,
        ],
        cwd=dest_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        process.communicate()
        print(f"git checkout {nf_latest_version} done.")

    os.makedirs(f"{dest_dir}/patched-fonts")
    os.makedirs(f"{dest_dir}/src/unpatched-fonts")


if __name__ == "__main__":
    main()
