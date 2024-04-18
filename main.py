"""Download and path fonts"""

import argparse
import os
import shutil
import sys

from lib import (
    FontMetadata,
    LogLevel,
    TEMP_DIR_FONTS,
    TtfOtf,
    apply_stylistic_sets,
    check_requirements,
    clone_nerd_fonts_repo,
    copy_and_paste_fonts,
    download_and_extract_fonts,
    get_latest_version_nf,
    log,
    path_fonts,
)

HOME_DIR = os.getenv("HOME")

fonts = [
    FontMetadata(
        owner="microsoft",
        repo="cascadia-code",
        tag="",
        filename="",
        filename_start_with="",
        download_url="",
    ),
    FontMetadata(
        owner="dtinth",
        repo="comic-mono-font",
        tag="",
        filename="ComicMono.ttf",
        filename_start_with="",
        download_url="https://dtinth.github.io/comic-mono-font/ComicMono.ttf",
    ),
    FontMetadata(
        owner="tonsky",
        repo="FiraCode",
        tag="",
        filename="",
        filename_start_with="",
        download_url="",
    ),
    FontMetadata(
        owner="vercel",
        repo="geist-font",
        tag="",
        filename="",
        filename_start_with="GeistMono",
        download_url="",
    ),
    FontMetadata(
        owner="IBM",
        repo="plex",
        tag="",
        filename="",
        filename_start_with="IBM-Plex-Mono",
        download_url="",
    ),
    FontMetadata(
        owner="source-foundry",
        repo="Hack",
        tag="",
        filename="Hack-v3.003-ttf.zip",
        filename_start_with="",
        download_url="",
    ),
    FontMetadata(
        owner="be5invis",
        repo="Iosevka",
        tag="",
        filename="",
        filename_start_with="PkgTTF-IosevkaFixed-",
        download_url="",
    ),
    FontMetadata(
        owner="JetBrains",
        repo="JetBrainsMono",
        tag="",
        filename="",
        filename_start_with="",
        download_url="",
    ),
    FontMetadata(
        owner="googlefonts",
        repo="RobotoMono",
        tag="",
        filename="RobotoMono-Regular.ttf",
        filename_start_with="",
        download_url="https://github.com/googlefonts/RobotoMono/raw/main/fonts/ttf/RobotoMono-Regular.ttf",
    ),
]

ttf_files = [
    TtfOtf(
        path=os.path.join(
            TEMP_DIR_FONTS,
            "cascadia-code",
            "ttf",
            "static",
            "CascadiaCode-Light.ttf",
        ),
        enable_stylistic_sets=True,
        stylistic_sets="ss19",
    ),
    TtfOtf(
        path=os.path.join(
            TEMP_DIR_FONTS,
            "cascadia-code",
            "ttf",
            "static",
            "CascadiaCode-LightItalic.ttf",
        ),
        enable_stylistic_sets=True,
        stylistic_sets="ss01,ss19",
    ),
    TtfOtf(
        path=os.path.join(
            TEMP_DIR_FONTS,
            "cascadia-code",
            "ttf",
            "static",
            "CascadiaCode-SemiLight.ttf",
        ),
        enable_stylistic_sets=True,
        stylistic_sets="ss19",
    ),
    TtfOtf(
        path=os.path.join(
            TEMP_DIR_FONTS,
            "cascadia-code",
            "ttf",
            "static",
            "CascadiaCode-SemiLightItalic.ttf",
        ),
        enable_stylistic_sets=True,
        stylistic_sets="ss01,ss19",
    ),
    TtfOtf(
        path=os.path.join(
            TEMP_DIR_FONTS,
            "cascadia-code",
            "ttf",
            "static",
            "CascadiaCode-Regular.ttf",
        ),
        enable_stylistic_sets=True,
        stylistic_sets="ss19",
    ),
    TtfOtf(
        path=os.path.join(
            TEMP_DIR_FONTS,
            "cascadia-code",
            "ttf",
            "static",
            "CascadiaCode-Italic.ttf",
        ),
        enable_stylistic_sets=True,
        stylistic_sets="ss01,ss19",
    ),
    TtfOtf(
        path=os.path.join(
            TEMP_DIR_FONTS,
            "FiraCode",
            "ttf",
            "FiraCode-Regular.ttf",
        ),
        enable_stylistic_sets=True,
        stylistic_sets="cv01,cv02,cv10,ss01,ss05,cv16,cv29",
    ),
    TtfOtf(
        path=os.path.join(
            TEMP_DIR_FONTS,
            "geist-font",
            "GeistMono*",
            "statics-ttf",
            "GeistMono-Regular.ttf",
        ),
        enable_stylistic_sets=True,
        stylistic_sets="ss08",
    ),
    TtfOtf(
        path=os.path.join(
            TEMP_DIR_FONTS,
            "Hack",
            "ttf",
            "Hack-Regular.ttf",
        ),
        enable_stylistic_sets=False,
        stylistic_sets="",
    ),
    TtfOtf(
        path=os.path.join(
            TEMP_DIR_FONTS,
            "Hack",
            "ttf",
            "Hack-Italic.ttf",
        ),
        enable_stylistic_sets=False,
        stylistic_sets="",
    ),
    TtfOtf(
        path=os.path.join(
            TEMP_DIR_FONTS,
            "plex",
            "IBM-Plex-Mono",
            "fonts",
            "complete",
            "ttf",
            "IBMPlexMono-Regular.ttf",
        ),
        enable_stylistic_sets=True,
        stylistic_sets="zero,salt",
    ),
    TtfOtf(
        path=os.path.join(
            TEMP_DIR_FONTS,
            "plex",
            "IBM-Plex-Mono",
            "fonts",
            "complete",
            "ttf",
            "IBMPlexMono-Italic.ttf",
        ),
        enable_stylistic_sets=True,
        stylistic_sets="zero,ss06",
    ),
    TtfOtf(
        path=os.path.join(
            TEMP_DIR_FONTS,
            "Iosevka",
            "IosevkaFixed-Regular.ttf",
        ),
        enable_stylistic_sets=False,
        stylistic_sets="",
    ),
    TtfOtf(
        path=os.path.join(
            TEMP_DIR_FONTS,
            "Iosevka",
            "IosevkaFixed-Italic.ttf",
        ),
        enable_stylistic_sets=False,
        stylistic_sets="",
    ),
    TtfOtf(
        path=os.path.join(
            TEMP_DIR_FONTS,
            "JetBrainsMono",
            "fonts",
            "ttf",
            "JetBrainsMono-Regular.ttf",
        ),
        enable_stylistic_sets=True,
        stylistic_sets="cv01,cv02,cv15,cv20,zero",
    ),
    TtfOtf(
        path=os.path.join(
            TEMP_DIR_FONTS,
            "JetBrainsMono",
            "fonts",
            "ttf",
            "JetBrainsMono-Italic.ttf",
        ),
        enable_stylistic_sets=True,
        stylistic_sets="cv01,cv02,cv15,cv20,zero",
    ),
]


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
    if latest_tag_nf == "":
        log(LogLevel.FATAL, "Could not get nerd-fonts latest tag")
        sys.exit(1)

    clone_nerd_fonts_repo(args.dest, latest_tag_nf)

    download_and_extract_fonts(args.dest, fonts, args.token)

    apply_stylistic_sets(ttf_files)

    copy_and_paste_fonts(args.dest, ttf_files)

    shutil.rmtree(TEMP_DIR_FONTS)

    path_fonts(args.dest)


if __name__ == "__main__":
    main()
