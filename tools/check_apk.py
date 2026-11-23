"""Inspect packaged Android and Matrix attributions and verify release metadata."""
import argparse
import json
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]

def require(condition, message):
    if not condition:
        raise SystemExit(message)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path)
    parser.add_argument("--tag", help="release tag for the checked artifact")
    args = parser.parse_args()
    metadata = json.loads((args.apk.parent / "output-metadata.json").read_text(encoding="utf-8"))
    entry = next(x for x in metadata["elements"] if x["outputFile"] == args.apk.name)
    version = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["version"]
    require(metadata["applicationId"] == "com.llmnest.android", "wrong application ID")
    require(entry["versionName"] == version, "inconsistent release version")
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
    print(f"{args.apk.name}: {version} ({entry['versionCode']}), local SDK and runtime licenses verified")

if __name__ == "__main__":
    main()
