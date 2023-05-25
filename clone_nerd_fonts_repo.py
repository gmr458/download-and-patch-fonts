"""Clone ryanoasis/nerd-fonts repo from GitHub"""

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
NF_LATEST_VERSION = ""

req = urllib.request.Request(URL_API)

try:
    with urllib.request.urlopen(req) as response:
        data = json.load(response)
        NF_LATEST_VERSION = data["tag_name"]
except urllib.error.HTTPError as err:
    if str(err) == "HTTP Error 401: Unauthorized":
        print("Invalid token")
        sys.exit()

if NF_LATEST_VERSION == "":
    print("Could not get nerd-fonts latest tag")
    sys.exit()


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

    with subprocess.Popen(
        [
            "git",
            "checkout",
            NF_LATEST_VERSION,
        ],
        cwd=DEST_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        process.communicate()
        print(f"git checkout {NF_LATEST_VERSION} done.")

    os.makedirs(f"{DEST_DIR}/patched-fonts")
    os.makedirs(f"{DEST_DIR}/src/unpatched-fonts")


check_requirements()
clone_nerd_fonts_repo()
