import { execFileSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
execFileSync("python3", [join(here, "draw.py")], { cwd: here, stdio: "inherit" });
const png = join(here, "entry.png");
if (!existsSync(png)) throw new Error("entry.png missing after draw.py");
copyFileSync(png, join(outDir, "entry.png"));
