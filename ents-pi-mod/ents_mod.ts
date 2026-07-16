import { ExtensionAPI } from '@earendil-works/pi-coding-agent';

export default async function activate(pi: ExtensionAPI) {
    pi.registerCommand('ents-grade', async (args) => {
        const level = args[0] || "00";
        const levelDirs: Record<string, string> = {
            "00": "ents/max_env/phases/00_The_Seed",
            "01": "ents/max_env/phases/01_The_Enting",
            "02": "ents/max_env/phases/02_The_Lexicon"
        };
        
        const targetDir = levelDirs[level];
        if (!targetDir) {
            pi.ui.notify(`Invalid level: ${level}`, { type: 'error' });
            return;
        }

        pi.ui.notify(`Oracle is grading level ${level}...`, { type: 'info' });
        try {
            const { spawn } = await import('child_process');
            
            const p = spawn('./grademe.sh', [], { cwd: targetDir, shell: true });
            let output = "";
            
            p.stdout.on('data', (data) => {
                output += data.toString();
            });
            p.stderr.on('data', (data) => {
                output += data.toString();
            });

            p.on('close', (code) => {
                // Show custom UI with the output
                pi.ui.custom({
                    type: 'box',
                    title: `🔮 Oracle of Fangorn - Level ${level}`,
                    content: output,
                    style: { border: 'double', borderColor: output.includes('✅ PASS') && !output.includes('❌ FAIL') ? 'green' : 'red' }
                });
            });

        } catch (e: any) {
            pi.ui.notify(`Failed to invoke Oracle: ${e.message}`, { type: 'error' });
        }
    }, {
        description: 'Invoke the Oracle of Fangorn to grade an Ents level (e.g. /ents-grade 00)'
    });

    // File protection
    pi.on('preToolCall', async (event) => {
        if (event.tool.name === 'edit' || event.tool.name === 'write') {
            const path = event.tool.parameters.path;
            if (path.endsWith('grademe.sh') || path.endsWith('SUBJECT.md')) {
                throw new Error("The Oracle forbids tampering with the trial parameters.");
            }
        }
    });
}
