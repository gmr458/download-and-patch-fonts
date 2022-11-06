"""Download and path fonts"""

import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

TOKEN = ""

while True:
    TOKEN = input("Enter GitHub API token: ")

    if TOKEN == "":
        continue

    break

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
}


class Font:
    """Class Font"""

    def __init__(
        self,
        owner,
        repo,
        tag="",
        file_name="",
        download_url="",
        file_name_start_with="",
    ):
        self.owner = owner
        self.repo = repo
        self.tag = tag or self.get_tag()
        self.file_name = file_name or self.get_file_name(file_name_start_with)
        self.download_url = (
            download_url
            or f"https://github.com/{self.owner}/{self.repo}/releases/download/{self.tag}/{self.file_name}"
        )

    def get_tag(self) -> str:
        """Get tag from GitHub API"""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases/latest"

        req = urllib.request.Request(url=url, headers=headers)

        try:
            with urllib.request.urlopen(req) as response:
                data = json.load(response)
                return data["tag_name"]
        except urllib.error.HTTPError as err:
            if str(err) == "HTTP Error 401: Unauthorized":
                print("Invalid token")
                sys.exit()

        return "none"

    def get_file_name(self, file_name_start_with="") -> str:
        """Get file name from GitHub API"""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases/latest"

        req = urllib.request.Request(url=url, headers=headers)

        try:
            with urllib.request.urlopen(req) as response:
                data = json.load(response)

                if len(data["assets"]) == 1:
                    return data["assets"][0]["name"]

                for asset in data["assets"]:
                    if asset["name"].find(file_name_start_with) != -1:
                        return asset["name"]
        except urllib.error.HTTPError as err:
            if str(err) == "HTTP Error 401: Unauthorized":
                print("Invalid token")
                sys.exit()

        return "none"


HOME_DIR = os.getenv("HOME")

# 1. Clone nerd-fonts repo.
def clone_nerd_fonts_repo():
    """Clone nerd-fonts repo from GitHub"""
    if not os.path.exists(f"{HOME_DIR}/Programs"):
        os.makedirs(f"{HOME_DIR}/Programs")

    if os.path.exists(f"{HOME_DIR}/Programs/nerd-fonts"):
        shutil.rmtree(f"{HOME_DIR}/Programs/nerd-fonts")

    print("\nCloning https://github.com/ryanoasis/nerd-fonts.git")
    with subprocess.Popen(
        [
            "git",
            "clone",
            "--filter=blob:none",
            "--sparse",
            "https://github.com/ryanoasis/nerd-fonts.git",
            f"{HOME_DIR}/Programs/nerd-fonts",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        process.communicate()
        print("https://github.com/ryanoasis/nerd-fonts.git cloned.\n")

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
        cwd=f"{HOME_DIR}/Programs/nerd-fonts",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        process.communicate()
        print("Directories bin, css, src/glyphs and src/svgs added.\n")

    os.makedirs(f"{HOME_DIR}/Programs/nerd-fonts/patched-fonts")
    os.makedirs(f"{HOME_DIR}/Programs/nerd-fonts/src/unpatched-fonts")


clone_nerd_fonts_repo()

# 2. Download and extracts fonts.
fonts = (
    {
        "owner": "tonsky",
        "repo": "FiraCode",
        "tag": "",
        "file_name": "",
        "download_url": "",
        "file_name_start_with": "",
    },
    {
        "owner": "microsoft",
        "repo": "cascadia-code",
        "tag": "",
        "file_name": "",
        "download_url": "",
        "file_name_start_with": "",
    },
    {
        "owner": "be5invis",
        "repo": "Iosevka",
        "tag": "",
        "file_name": "",
        "download_url": "",
        "file_name_start_with": "ttf-iosevka-fixed-",
    },
    {
        "owner": "dtinth",
        "repo": "comic-mono-font",
        "tag": "",
        "file_name": "ComicMono.ttf",
        "download_url": "https://dtinth.github.io/comic-mono-font/ComicMono.ttf",
        "file_name_start_with": "",
    },
)

TEMP_DIR = "/tmp/fonts"


def is_ttf(filename: str) -> bool:
    """The font to download is .ttf, there are link that download .zip files"""
    return filename.find(".ttf") != -1


def download_and_extract_fonts(list_fonts):
    """Download and extract fonts in temp directory /tmp/fonts"""
    if os.path.exists(TEMP_DIR) and os.path.isdir(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

    os.makedirs(TEMP_DIR)

    for item in list_fonts:
        font = Font(
            item["owner"],
            item["repo"],
            item["tag"],
            item["file_name"],
            item["download_url"],
            item["file_name_start_with"],
        )

        dest = f"{TEMP_DIR}/{font.file_name}"

        if is_ttf(font.file_name):
            dest = (
                f"{HOME_DIR}/Programs/nerd-fonts/src/unpatched-fonts/{font.file_name}"
            )

        print(f"Downloading {font.download_url}")
        urllib.request.urlretrieve(font.download_url, dest)
        print(f"{font.file_name} downloaded.\n")

        if is_ttf(font.file_name):
            continue

        print(f"Extracting {font.file_name}")
        with subprocess.Popen(
            [
                "unzip",
                "-q",
                f"{TEMP_DIR}/{font.file_name}",
                "-d",
                f"{TEMP_DIR}/{font.repo}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as process:
            process.communicate()
            print(f"{font.file_name} extracted.\n")


download_and_extract_fonts(fonts)

# 3. Copy ttf files downloaded to ~/Programs/nerd-fonts/src/unpatched-fonts
ttf_files = (
    f"{TEMP_DIR}/FiraCode/ttf/FiraCode-Regular.ttf",
    f"{TEMP_DIR}/cascadia-code/ttf/static/CascadiaCode-Light.ttf",
    f"{TEMP_DIR}/cascadia-code/ttf/static/CascadiaCode-LightItalic.ttf",
    f"{TEMP_DIR}/cascadia-code/ttf/static/CascadiaCode-SemiLight.ttf",
    f"{TEMP_DIR}/cascadia-code/ttf/static/CascadiaCode-SemiLightItalic.ttf",
    f"{TEMP_DIR}/Iosevka/iosevka-fixed-regular.ttf",
    f"{TEMP_DIR}/Iosevka/iosevka-fixed-italic.ttf",
)


def copy_and_paste_fonts():
    """Copy downloaded fonts and paste in src/unpatched-fonts inside nerd-fonts repo"""
    for file in ttf_files:
        shutil.copy(file, f"{HOME_DIR}/Programs/nerd-fonts/src/unpatched-fonts/")


copy_and_paste_fonts()

# Remove temporal dir for downloaded fonts
shutil.rmtree(TEMP_DIR)

# Path fonts
def path_fonts():
    "Path fonts previosly downloaded"
    print("Patching fonts in ~/Programs/nerd-fonts/src/unpatched-fonts\n")

    fonts_to_path = os.listdir(f"{HOME_DIR}/Programs/nerd-fonts/src/unpatched-fonts")

    for font in fonts_to_path:
        print(f"Patching {font}")
        with subprocess.Popen(
            [
                "fontforge",
                "-script",
                "font-patcher",
                f"src/unpatched-fonts/{font}",
                "--complete",
                "--mono",
                "--outputdir",
                "patched-fonts",
            ],
            cwd=f"{HOME_DIR}/Programs/nerd-fonts",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as process:
            process.communicate()
            print(f"{font} patched.\n")

    print("All patched fonts are in ~/Programs/nerd-fonts/patched-fonts\n")


path_fonts()
