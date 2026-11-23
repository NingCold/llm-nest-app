import { defineConfig } from "vite";

export default defineConfig({
  root: "crypto",
  base: "./",
  build: {
    target: "es2022",
    outDir: "../app/build/generated/cryptoAssets/crypto",
    emptyOutDir: true,
    assetsInlineLimit: 0,
    rollupOptions: { output: { entryFileNames: "runtime.js", chunkFileNames: "[name].js", assetFileNames: "[name][extname]" } },
  },
});
