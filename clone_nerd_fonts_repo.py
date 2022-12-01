"""Clone ryanoasis/nerd-fonts repo from GitHub"""

import os
import shutil
import subprocess
import sys

HOME_DIR = os.getenv("HOME")
URL_REPO = "https://github.com/ryanoasis/nerd-fonts.git"
DEST_DIR = f"{HOME_DIR}/nerd-fonts"


def check_requirements():
    """Check if Git is installed"""
    if shutil.which("git") is None:
        print("Git is required.")
        sys.exit(0)


def clone_nerd_fonts_repo():
    """Clone ryanoasis/nerd-fonts repo from GitHub"""
    if os.path.exists(DEST_DIR):
        shutil.rmtree(DEST_DIR)

    print(f"Cloning {URL_REPO}")
    with subprocess.Popen(
        ["git", "clone", "--filter=blob:none", "--sparse", URL_REPO, DEST_DIR],
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
        cwd=DEST_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        process.communicate()
        print("Directories bin, css, src/glyphs and src/svgs added.\n")

    os.makedirs(f"{DEST_DIR}/patched-fonts")
    os.makedirs(f"{DEST_DIR}/src/unpatched-fonts")


check_requirements()
clone_nerd_fonts_repo()
