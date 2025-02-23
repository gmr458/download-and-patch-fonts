"""Download and path fonts"""

import argparse
import os
import shutil
import sys

from fonts import fonts
from lib import (
    TEMP_DIR_FONTS,
    LogLevel,
    apply_stylistic_sets,
    check_requirements,
    clone_nerd_fonts_repo,
    copy_and_paste_fonts,
    download_and_extract_fonts,
    get_latest_version_nf,
    log,
    path_fonts,
)
from ttf_otf_files import ttf_otf_files

HOME_DIR = os.getenv("HOME")


def main():
    check_requirements()

    parser = argparse.ArgumentParser(
        description="This script clone the latest release of github.com/ryanoasis/nerd-fonts"
    )
    parser.add_argument(
        "dest",
        nargs="?",
        help="Destination directory to clone the repository",
    )
    parser.add_argument(
        "token",
        nargs="?",
        help="GitHub API token",
    )

    args = parser.parse_args()
    if args.dest is None or args.dest == "":
        log(
            LogLevel.FATAL,
            "Pass the destination directory to clone the repository as the first argument",
        )
        sys.exit(1)
    if args.token is None or args.token == "":
        log(LogLevel.FATAL, "Pass the GitHub API token as the second argument")
        sys.exit(1)

    latest_tag_nf = get_latest_version_nf(args.token)
    if latest_tag_nf == "" or latest_tag_nf is None:
        log(LogLevel.FATAL, "Could not get nerd-fonts latest tag")
        sys.exit(1)

    clone_nerd_fonts_repo(args.dest, latest_tag_nf)

    download_and_extract_fonts(fonts, args.token)

    apply_stylistic_sets(ttf_otf_files)

    copy_and_paste_fonts(args.dest, ttf_otf_files)

    shutil.rmtree(TEMP_DIR_FONTS)

    path_fonts(args.dest)


if __name__ == "__main__":
    main()
