const { execFileSync } = require("node:child_process");
const { readFileSync, readdirSync, mkdirSync, writeFileSync } = require("node:fs");
const { join } = require("node:path");
const { createHash } = require("node:crypto");

const [output, corepack] = process.argv.slice(2);
const packages = Object.values(JSON.parse(execFileSync(process.execPath,
  [corepack, "pnpm@11.22.0", "licenses", "list", "--prod", "--json"], { encoding: "utf8" }))).flat();
const sections = ["LLM Nest Android — JavaScript and WebAssembly runtime"];
const licenseDir = "gradle/licenses";
for (const pkg of packages.sort((a, b) => a.name.localeCompare(b.name, "en"))) {
  for (const [i, directory] of pkg.paths.entries()) {
    const version = pkg.versions[i];
    const files = readdirSync(directory, { withFileTypes: true })
      .filter(f => f.isFile() && /^(licen[cs]e|copying|notice)(?:[._-].*)?$/i.test(f.name))
      .map(f => f.name).sort();
    if (!files.length) throw Error("No license for " + pkg.name + "@" + version);
    sections.push([pkg.name + "@" + version + " · " + pkg.license, pkg.homepage || "",
      ...files.map(f => f + "\n" + readFileSync(join(directory, f), "utf8"))].join("\n"));
    if (pkg.name === "@matrix-org/matrix-sdk-crypto-wasm") {
      const stem = join(licenseDir, "matrix-sdk-crypto-wasm-" + version);
      const provenance = JSON.parse(readFileSync(stem + "-provenance.json", "utf8"));
      const extra = readFileSync(stem + ".txt");
      if (createHash("sha256").update(extra).digest("hex") !== provenance.noticesSha256)
        throw Error("Matrix WASM attribution mismatch");
      sections.push(extra.toString("utf8"));
    }
  }
}
const dest = join(output, "crypto");
mkdirSync(dest, { recursive: true });
writeFileSync(join(dest, "THIRD_PARTY_NOTICES.txt"), sections.join("\n\n" + "=".repeat(72) + "\n\n") + "\n");
for (const name of ["LICENSE", "NOTICE"]) writeFileSync(join(dest, name + ".txt"), readFileSync(name));
