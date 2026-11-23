"""Inspect packaged Android and Matrix attributions and verify release metadata."""
import argparse
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]

def require(condition, message):
    if not condition:
        raise SystemExit(message)

def sdk_root():
    for name in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
        if os.environ.get(name):
            return Path(os.environ[name])
    adb = shutil.which("adb")
    if adb and Path(adb).parent.name == "platform-tools":
        return Path(adb).resolve().parents[1]
    return None

def apk_identity(apk, sdk):
    require(sdk is not None, "set ANDROID_HOME or pass --sdk-root for Android Build Tools 36.0.0")
    aapt = sdk / "build-tools" / "36.0.0" / ("aapt2.exe" if os.name == "nt" else "aapt2")
    require(aapt.is_file(), f"Android Build Tools 36.0.0 not found at {aapt}")
    result = subprocess.run([str(aapt), "dump", "badging", str(apk.resolve())],
                            capture_output=True, encoding="utf-8", errors="replace")
    require(result.returncode == 0, f"aapt2 failed: {result.stderr.strip()}")
    package = next((line for line in result.stdout.splitlines() if line.startswith("package: ")), "")
    fields = dict(re.findall(r"([A-Za-z]+)='([^']*)'", package))
    require({"name", "versionName", "versionCode"} <= fields.keys(), "missing APK manifest identity")
    return fields

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path)
    parser.add_argument("--tag", help="release tag for the checked artifact")
    parser.add_argument("--sdk-root", type=Path, help="Android SDK containing Build Tools 36.0.0")
    args = parser.parse_args()
    identity = apk_identity(args.apk, args.sdk_root or sdk_root())
    version = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["version"]
    code = re.search(r"^appVersionCode=(\d+)$", (ROOT / "gradle.properties").read_text(encoding="utf-8"), re.MULTILINE)
    require(code, "missing appVersionCode in gradle.properties")
    require(identity["name"] == "com.llmnest.android", "wrong application ID: " + identity["name"])
    require(identity["versionName"] == version, "unexpected APK versionName: " + identity["versionName"])
    require(identity["versionCode"] == code[1], "unexpected APK versionCode: " + identity["versionCode"])
    require(not args.tag or args.tag == "v" + version, "release tag does not match APK")
    with ZipFile(args.apk) as apk:
        for scope in ("assets/", "assets/crypto/"):
            for name in ("LICENSE", "NOTICE"):
                require(apk.read(scope + name + ".txt") == (ROOT / name).read_bytes(), f"invalid {scope}{name}")
        js = apk.read("assets/crypto/THIRD_PARTY_NOTICES.txt").decode()
        native = apk.read("assets/THIRD_PARTY_NOTICES.txt").decode()
        for name in ("@noble/curves@", "@noble/hashes@", "@matrix-org/matrix-sdk-crypto-wasm@"):
            require(name in js, "missing " + name)
        wasm = [x for x in apk.infolist() if x.filename == "assets/crypto/matrix_sdk_crypto_wasm_bg.wasm"]
        require(len(wasm) == 1 and wasm[0].file_size > 1024 * 1024, "missing local SDK")
        license_dir = ROOT / "gradle/licenses"
        provenance, = license_dir.glob("matrix-sdk-crypto-wasm-*-provenance.json")
        notices = provenance.with_name(provenance.name.replace("-provenance.json", ".txt"))
        require(notices.read_bytes() in apk.read("assets/crypto/THIRD_PARTY_NOTICES.txt"), "incomplete WASM notices")
        for name in ("OkHttp Public Suffix List", "Boost Software License", "Stephen Colebourne", "Copyright 2016-2021 JetBrains"):
            require(name in native, "missing native attribution: " + name)
    with ZipFile(ROOT / "gradle/wrapper/gradle-wrapper.jar") as wrapper:
        require(b"END OF TERMS AND CONDITIONS" in wrapper.read("META-INF/LICENSE"), "incomplete Gradle wrapper license")
    print(f"{args.apk.name}: {identity['name']} {version} ({identity['versionCode']}), local SDK and runtime licenses verified")

if __name__ == "__main__":
    main()
