"""Download and path fonts"""

import shutil
import sys

from lib import (
    TEMP_DIR,
    FontMetadata,
    Ttf,
    apply_stylistic_sets,
    clone_nerd_fonts_repo,
    copy_and_paste_fonts,
    download_and_extract_fonts,
    get_latest_version_nf,
    path_fonts,
)

NF_LATEST_VERSION = get_latest_version_nf()
if NF_LATEST_VERSION == "":
    print("Could not get nerd-fonts latest tag")
    sys.exit()

clone_nerd_fonts_repo(NF_LATEST_VERSION)

fonts = [
    FontMetadata("tonsky", "FiraCode", "", "", "", ""),
    FontMetadata("microsoft", "cascadia-code", "", "", "", ""),
    FontMetadata("be5invis", "Iosevka", "", "", "ttf-iosevka-fixed-", ""),
    FontMetadata(
        "dtinth",
        "comic-mono-font",
        "",
        "ComicMono.ttf",
        "",
        "https://dtinth.github.io/comic-mono-font/ComicMono.ttf",
    ),
]
download_and_extract_fonts(fonts)

ttf_files = [
    Ttf(
        f"{TEMP_DIR}/FiraCode/ttf/FiraCode-Regular.ttf",
        True,
        "cv01,cv02,cv10,ss01,ss05",
    ),
    Ttf(
        f"{TEMP_DIR}/cascadia-code/ttf/static/CascadiaCode-Light.ttf",
        True,
        "ss19",
    ),
    Ttf(
        f"{TEMP_DIR}/cascadia-code/ttf/static/CascadiaCode-LightItalic.ttf",
        True,
        "ss01,ss19",
    ),
    Ttf(
        f"{TEMP_DIR}/cascadia-code/ttf/static/CascadiaCode-SemiLight.ttf",
        True,
        "ss19",
    ),
    Ttf(
        f"{TEMP_DIR}/cascadia-code/ttf/static/CascadiaCode-SemiLightItalic.ttf",
        True,
        "ss01,ss19",
    ),
    Ttf(
        f"{TEMP_DIR}/Iosevka/iosevka-fixed-regular.ttf",
        False,
        "",
    ),
    Ttf(
        f"{TEMP_DIR}/Iosevka/iosevka-fixed-italic.ttf",
        False,
        "",
    ),
]
apply_stylistic_sets(ttf_files)

copy_and_paste_fonts(ttf_files)

shutil.rmtree(TEMP_DIR)

path_fonts()
