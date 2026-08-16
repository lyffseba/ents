import { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = join(HERE, "..");
const CURRICULUM = JSON.parse(
  readFileSync(join(REPO, "max_env/phases/curriculum.json"), "utf8"),
);

export default async function activate(pi: ExtensionAPI) {
  pi.registerCommand(
    "ents-grade",
    async (args) => {
      const level = args[0] || "00";
      const spec = CURRICULUM.phases[level];
      if (!spec) {
        pi.ui.notify(`Invalid level: ${level}`, { type: "error" });
        return;
      }
      const targetDir = join(REPO, "max_env/phases", spec.dir);
      pi.ui.notify(`Oracle is grading ${spec.name}...`, { type: "info" });
      try {
        const { spawn } = await import("child_process");
        const p = spawn("./grademe.sh", [], { cwd: targetDir, shell: true });
        let output = "";
        p.stdout.on("data", (data) => {
          output += data.toString();
        });
        p.stderr.on("data", (data) => {
          output += data.toString();
        });
        p.on("close", () => {
          pi.ui.custom({
            type: "box",
            title: `🔮 Oracle of Fangorn - ${spec.name}`,
            content: output,
            style: {
              border: "double",
              borderColor:
                output.includes("✅ PASS") && !output.includes("❌ FAIL")
                  ? "green"
                  : "red",
            },
          });
        });
      } catch (e: any) {
        pi.ui.notify(`Failed to invoke Oracle: ${e.message}`, { type: "error" });
      }
    },
    {
      description:
        "Invoke the Oracle of Fangorn to grade an Ents level (e.g. /ents-grade 00)",
    },
  );

  pi.on("preToolCall", async (event) => {
    if (event.tool.name === "edit" || event.tool.name === "write") {
      const path = event.tool.parameters.path;
      if (
        path.endsWith("grademe.sh") ||
        path.endsWith("SUBJECT.md") ||
        path.endsWith("curriculum.json")
      ) {
        throw new Error("The Oracle forbids tampering with the trial parameters.");
      }
    }
  });
}
