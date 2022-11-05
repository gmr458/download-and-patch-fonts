import json
import os
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request

token = ""

while True:
    token = input("Enter GitHub API token: ")

    if token == "":
        continue
    else:
        break

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {token}",
}


class Font:
    def __init__(self, owner, repo, file_name_start_with=""):
        self.owner = owner
        self.repo = repo
        self.tag = self.get_tag()
        self.file_name = self.get_file_name(file_name_start_with)
        self.download_url = f"https://github.com/{self.owner}/{self.repo}/releases/download/{self.tag}/{self.file_name}"

    def get_tag(self):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases/latest"

        req = urllib.request.Request(url=url, headers=headers)

        try:
            with urllib.request.urlopen(req) as response:
                data = json.load(response)
                return data["tag_name"]
        except urllib.error.HTTPError as e:
            if str(e) == "HTTP Error 401: Unauthorized":
                print("Invalid token")
                exit()

    def get_file_name(self, file_name_start_with=""):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases/latest"

        req = urllib.request.Request(url=url, headers=headers)

        try:
            with urllib.request.urlopen(req) as response:
                data = json.load(response)

                if len(data["assets"]) == 1:
                    return data["assets"][0]["name"]

                for a in data["assets"]:
                    if a["name"].find(file_name_start_with) != -1:
                        return a["name"]
        except urllib.error.HTTPError as e:
            if str(e) == "HTTP Error 401: Unauthorized":
                print("Invalid token")
                exit()


home_dir = os.getenv("HOME")

# 1. Clone nerd-fonts repo.
def clone_nerd_fonts_repo():
    if not os.path.exists(f"{home_dir}/Programs"):
        os.makedirs(f"{home_dir}/Programs")

    if os.path.exists(f"{home_dir}/Programs/nerd-fonts"):
        shutil.rmtree(f"{home_dir}/Programs/nerd-fonts")

    print("Cloning https://github.com/ryanoasis/nerd-fonts.git")
    process = subprocess.Popen(
        [
            "git",
            "clone",
            "--filter=blob:none",
            "--sparse",
            "https://github.com/ryanoasis/nerd-fonts.git",
            f"{home_dir}/Programs/nerd-fonts",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    process.communicate()
    print("https://github.com/ryanoasis/nerd-fonts.git cloned.\n")

    process = subprocess.Popen(
        [
            "git",
            "sparse-checkout",
            "add",
            "bin",
            "css",
            "src/glyphs",
            "src/svgs",
        ],
        cwd=f"{home_dir}/Programs/nerd-fonts",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    process.communicate()
    print("Directories bin, css, src/glyphs and src/svgs added.\n")

    os.makedirs(f"{home_dir}/Programs/nerd-fonts/patched-fonts")
    os.makedirs(f"{home_dir}/Programs/nerd-fonts/src/unpatched-fonts")


clone_nerd_fonts_repo()

# 2. Download and extracts fonts.
fonts = (
    {
        "owner": "tonsky",
        "repo": "FiraCode",
        "file_name_start_with": "",
    },
    {
        "owner": "microsoft",
        "repo": "cascadia-code",
        "file_name_start_with": "",
    },
    {
        "owner": "be5invis",
        "repo": "Iosevka",
        "file_name_start_with": "ttf-iosevka-fixed-",
    },
)

temp_dir = "/tmp/fonts"


def download_and_extract_fonts(list_fonts):
    if os.path.exists(temp_dir) and os.path.isdir(temp_dir):
        shutil.rmtree(temp_dir)

    os.makedirs(temp_dir)

    for f in list_fonts:
        font = Font(f["owner"], f["repo"], f["file_name_start_with"])

        print(f"Downloading {font.download_url}")
        urllib.request.urlretrieve(font.download_url, f"{temp_dir}/{font.file_name}")
        print(f"{font.file_name} downloaded.\n")

        print(f"Extracting {font.file_name}")
        process = subprocess.Popen(
            [
                "unzip",
                "-q",
                f"{temp_dir}/{font.file_name}",
                "-d",
                f"{temp_dir}/{font.repo}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        process.communicate()
        print(f"{font.file_name} extracted.\n")


download_and_extract_fonts(fonts)

# 3. Copy ttf files downloaded to ~/Programs/nerd-fonts/src/unpatched-fonts
ttf_files = (
    f"{temp_dir}/FiraCode/ttf/FiraCode-Regular.ttf",
    f"{temp_dir}/cascadia-code/ttf/static/CascadiaCode-Light.ttf",
    f"{temp_dir}/cascadia-code/ttf/static/CascadiaCode-LightItalic.ttf",
    f"{temp_dir}/cascadia-code/ttf/static/CascadiaCode-SemiLight.ttf",
    f"{temp_dir}/cascadia-code/ttf/static/CascadiaCode-SemiLightItalic.ttf",
    f"{temp_dir}/Iosevka/iosevka-fixed-regular.ttf",
    f"{temp_dir}/Iosevka/iosevka-fixed-italic.ttf",
)


def copy_and_paste_fonts():
    for file in ttf_files:
        shutil.copy(file, f"{home_dir}/Programs/nerd-fonts/src/unpatched-fonts/")


copy_and_paste_fonts()

# Remove temporal dir for downloaded fonts
shutil.rmtree(temp_dir)
