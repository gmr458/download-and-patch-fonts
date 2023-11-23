"""Download and path fonts"""

import argparse
import os
import shutil
import sys

from lib import (
    FontMetadata,
    TEMP_DIR,
    TtfOtf,
    apply_stylistic_sets,
    clone_nerd_fonts_repo,
    copy_and_paste_fonts,
    download_and_extract_fonts,
    get_latest_version_nf,
    path_fonts,
)

HOME_DIR = os.getenv("HOME")
DEST_DIR = f"{HOME_DIR}/nerd-fonts"

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
        f"{TEMP_DIR}/cascadia-code/ttf/static/CascadiaCode-Light.ttf",
        True,
        "ss19",
    ),
    TtfOtf(
        f"{TEMP_DIR}/cascadia-code/ttf/static/CascadiaCode-LightItalic.ttf",
        True,
        "ss01,ss19",
    ),
    TtfOtf(
        f"{TEMP_DIR}/cascadia-code/ttf/static/CascadiaCode-SemiLight.ttf",
        True,
        "ss19",
    ),
    TtfOtf(
        f"{TEMP_DIR}/cascadia-code/ttf/static/CascadiaCode-SemiLightItalic.ttf",
        True,
        "ss01,ss19",
    ),
    TtfOtf(
        f"{TEMP_DIR}/FiraCode/ttf/FiraCode-Regular.ttf",
        True,
        "cv01,cv02,cv10,ss01,ss05,cv16,cv29",
    ),
    TtfOtf(
        f"{TEMP_DIR}/geist-font/GeistMono-Regular.otf",
        True,
        "ss08",
    ),
    TtfOtf(
        f"{TEMP_DIR}/Hack/ttf/Hack-Regular.ttf",
        False,
        "",
    ),
    TtfOtf(
        f"{TEMP_DIR}/Hack/ttf/Hack-Italic.ttf",
        False,
        "",
    ),
    # Ttf(
    #     f"{TEMP_DIR}/Iosevka/iosevka-fixed-regular.ttf",
    #     False,
    #     "",
    # ),
    # Ttf(
    #     f"{TEMP_DIR}/Iosevka/iosevka-fixed-italic.ttf",
    #     False,
    #     "",
    # ),
    TtfOtf(
        f"{TEMP_DIR}/JetBrainsMono/fonts/ttf/JetBrainsMono-Regular.ttf",
        True,
        "cv01,cv02,cv15,cv20,zero",
    ),
    TtfOtf(
        f"{TEMP_DIR}/JetBrainsMono/fonts/ttf/JetBrainsMono-Italic.ttf",
        True,
        "cv01,cv02,cv15,cv20,zero",
    ),
]


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
    if args.dest is None or args.dest == "":
        print("Pass the destination directory to clone the repository")
        sys.exit()

    latest_tag_nf = get_latest_version_nf()
    if latest_tag_nf == "":
        print("Could not get nerd-fonts latest tag")
        sys.exit()

    clone_nerd_fonts_repo(args.dest, latest_tag_nf)

    download_and_extract_fonts(args.dest, fonts)

    apply_stylistic_sets(ttf_files)

    copy_and_paste_fonts(args.dest, ttf_files)

    shutil.rmtree(TEMP_DIR)

    path_fonts(args.dest)


if __name__ == "__main__":
    main()
