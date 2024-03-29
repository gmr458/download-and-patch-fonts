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
    FontMetadata("microsoft", "cascadia-code", "", "", "", ""),
    FontMetadata(
        "dtinth",
        "comic-mono-font",
        "",
        "ComicMono.ttf",
        "",
        "https://dtinth.github.io/comic-mono-font/ComicMono.ttf",
    ),
    FontMetadata("tonsky", "FiraCode", "", "", "", ""),
    FontMetadata("vercel", "geist-font", "", "", "Geist.Mono", ""),
    FontMetadata("IBM", "plex", "", "", "True", ""),
    FontMetadata("source-foundry", "Hack", "", "Hack-v3.003-ttf.zip", "", ""),
    # FontMetadata("be5invis", "Iosevka", "", "", "ttf-iosevka-fixed-", ""),
    FontMetadata("JetBrains", "JetBrainsMono", "", "", "", ""),
    FontMetadata(
        "googlefonts",
        "RobotoMono",
        "",
        "RobotoMono-Regular.ttf",
        "",
        "https://github.com/googlefonts/RobotoMono/raw/main/fonts/ttf/RobotoMono-Regular.ttf",
    ),
]

ttf_files = [
    TtfOtf(
        os.path.join(
            TEMP_DIR_FONTS,
            "cascadia-code",
            "ttf",
            "static",
            "CascadiaCode-Light.ttf",
        ),
        True,
        "ss19",
    ),
    TtfOtf(
        os.path.join(
            TEMP_DIR_FONTS,
            "cascadia-code",
            "ttf",
            "static",
            "CascadiaCode-LightItalic.ttf",
        ),
        True,
        "ss01,ss19",
    ),
    TtfOtf(
        os.path.join(
            TEMP_DIR_FONTS,
            "cascadia-code",
            "ttf",
            "static",
            "CascadiaCode-SemiLight.ttf",
        ),
        True,
        "ss19",
    ),
    TtfOtf(
        os.path.join(
            TEMP_DIR_FONTS,
            "cascadia-code",
            "ttf",
            "static",
            "CascadiaCode-SemiLightItalic.ttf",
        ),
        True,
        "ss01,ss19",
    ),
    TtfOtf(
        os.path.join(
            TEMP_DIR_FONTS,
            "cascadia-code",
            "ttf",
            "static",
            "CascadiaCode-Regular.ttf",
        ),
        True,
        "ss19",
    ),
    TtfOtf(
        os.path.join(
            TEMP_DIR_FONTS,
            "cascadia-code",
            "ttf",
            "static",
            "CascadiaCode-Italic.ttf",
        ),
        True,
        "ss01,ss19",
    ),
    TtfOtf(
        os.path.join(TEMP_DIR_FONTS, "FiraCode", "ttf", "FiraCode-Regular.ttf"),
        True,
        "cv01,cv02,cv10,ss01,ss05,cv16,cv29",
    ),
    TtfOtf(
        os.path.join(TEMP_DIR_FONTS, "geist-font", "Geist.Mono", "GeistMono-Regular.otf"),
        True,
        "ss08",
    ),
    TtfOtf(
        os.path.join(TEMP_DIR_FONTS, "Hack", "ttf", "Hack-Regular.ttf"),
        False,
        "",
    ),
    TtfOtf(
        os.path.join(TEMP_DIR_FONTS, "Hack", "ttf", "Hack-Italic.ttf"),
        False,
        "",
    ),
    TtfOtf(
        os.path.join(TEMP_DIR_FONTS, "plex", "TrueType", "IBM-Plex-Mono", "IBMPlexMono-Regular.ttf"),
        True,
        "zero,salt",
    ),
    TtfOtf(
        os.path.join(TEMP_DIR_FONTS, "plex", "TrueType", "IBM-Plex-Mono", "IBMPlexMono-Italic.ttf"),
        True,
        "zero",
    ),
    # Ttf(
    #     os.path.join(TEMP_DIR_FONTS, "Iosevka", "iosevka-fixed-regular.ttf"),
    #     False,
    #     "",
    # ),
    # Ttf(
    #     os.path.join(TEMP_DIR_FONTS, "Iosevka", "iosevka-fixed-italic.ttf"),
    #     False,
    #     "",
    # ),
    TtfOtf(
        os.path.join(
            TEMP_DIR_FONTS,
            "JetBrainsMono",
            "fonts",
            "ttf",
            "JetBrainsMono-Regular.ttf",
        ),
        True,
        "cv01,cv02,cv15,cv20,zero",
    ),
    TtfOtf(
        os.path.join(
            TEMP_DIR_FONTS,
            "JetBrainsMono",
            "fonts",
            "ttf",
            "JetBrainsMono-Italic.ttf",
        ),
        True,
        "cv01,cv02,cv15,cv20,zero",
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
