"""
ContentAgent: Looks at common failure patterns (from past Oracle runs or stored errors), asks Gemini to propose new micro-lesson or SUBJECT tweak.
Decision executed: "generate 2 new drills for softmax".
"""
from ..deps import call_gemini
from .base import log_decision

def run_content_agent(dry_run: bool = False):
    # In real: aggregate recent FAIL outputs from DB or logs
    failures = "Many students fail the exact output format for softmax on token 1; common mistake: off-by-one in sum(exp)."
    prompt = f"Common failure pattern observed: {failures}. Propose ONE new micro-exercise (title + 3-sentence spec + exact expected output string) that can be added to Phase 01 SUBJECT.md for the JAX pillar. Keep it in the Trial of Fangorn style."
    proposal = call_gemini(prompt, system="You are the Entmoot Curriculum Agent. Output clean, copy-pasteable content only.")
    
    decision = "Generated 1 new micro-exercise for softmax precision based on 35% fail rate."
    log_decision("ContentAgent", decision, prompt, proposal, "proposed_to_human_or_auto_added")
    
    print("[CONTENT] Proposal:\n", proposal)
    if dry_run:
        print("(dry run - not published)")

if __name__ == "__main__":
    run_content_agent(dry_run=True)
