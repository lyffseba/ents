# Ents Academy — 3-Minute Demo Video Script (for Build with Gemini XPRIZE)

**Target length:** Under 3:00 (judges are not required to watch beyond 3 min).  
**Style:** Screen recording + voiceover (or talking head + screens). Show the *live deployed* product where possible. Emphasize **AI live in production executing key decisions**. Film on desktop/laptop (the intended platform).  
**Music:** Royalty-free, no third-party copyrighted material.  
**Key message:** This is a real business, run by AI agents using Gemini, on Google Cloud Run. The product teaches deep AI skills.

## Timestamped Script Outline

**0:00 - 0:15 — Hook + Context (Title card + quick cuts)**
- Screen: Landing page of deployed Ents Academy (or local at http://localhost:8000).
- Voiceover: "We built Ents Academy to solve a real problem: most people prompt AI, but almost no one understands how the models actually work under the hood. In 90 days we turned our from-scratch LLM curriculum into a real AI-native business for the XPRIZE."
- Show logo + "Education & Human Potential" + "Built with Gemini + Google Cloud Run".
- Quick cut to forest-themed UI.

**0:15 - 0:45 — The Product (Learner experience)**
- Navigate to /dashboard → show progress "grove", phases 00/01/02 with pillars (JAX, MLX, MAX, Mojo).
- Go to /lab/00/jax or /01 (show code editor).
- Submit sample code (use the reference solution or a partial).
- Voiceover: "Students work through strict 'Trials of Fangorn' — exactly like the original local Oracle graders, now in the browser."
- Show the result: auto-grade + **Gemini qualitative feedback** ("As the Oracle of Fangorn...").
- This demonstrates Gemini API call in the deployed application.

**0:45 - 1:30 — AI-Native Operations (The core of our score — spend the most time here)**
- Go to /tutor.
- Ask a real question live on camera: "Explain why the softmax probabilities must sum to one in the bigram model."
- Show Gemini response streaming or appearing. Voiceover: "Every single interaction with our AI Tutor is a live Gemini API call. The agent has full context of the student's current level and the exact SUBJECT spec."
- Cut to /ops — "The Entmoot".
- Voiceover: "This is where judges can see that our *business itself* is operated by AI."
- Click the "Trigger Retention Agent" button (or show scheduled run).
- On camera: RetentionAgent runs → Gemini is called → it decides on a specific user, generates a personalized nudge + discount, and the decision + full log is saved and displayed.
- Read the decision out loud: "Stalled user #42 at phase 01 for 7 days on softmax → sent custom hint + 20% off Pro."
- Show the DB-backed log table with timestamps, agent name, Gemini prompt summary, output, action taken.
- Voiceover: "These agents run continuously in production on Cloud Run. Retention, content generation, revenue monitoring — all governed by Gemini. Humans set high-level strategy only."
- Show recent logs, perhaps "42 Gemini calls today" or similar metric.

**1:30 - 2:00 — Business Viability + Revenue Evidence**
- Go to /pricing.
- Briefly show the Stripe checkout flow (use test mode on camera if live keys not set, or pre-recorded successful payment screen).
- Cut to terminal or /ops or a dashboard: run `python scripts/export_revenue.py`.
- Show the output: Total revenue, breakdown by May/June/July/August 2026, costs description, marketing spend = $0 (disclosed), related-party separated.
- Voiceover: "Real revenue from arms-length customers during the window. All tracked via Stripe webhooks into our system. Full exports and P&L available in the submission."
- Quick cut to xprize_evidence/ folder or screenshots of Stripe dashboard (redacted).

**2:00 - 2:30 — Category Impact + The Unique Curriculum**
- Show the original local experience briefly (run the TUI game or one grademe.sh that passes ✅).
- Voiceover: "The secret sauce is the pre-existing 'Four Pillars' curriculum that forces students to implement embeddings, softmax, and tokenizers in JAX, MLX, MAX, *and* bare-metal Mojo. This is not another prompt-engineering course — it's how you actually wake up the models."
- Show a student "downloading the workspace" from the web lab.
- "Hybrid model: browser for access and AI tutoring + full local Oracle for the deep bare-metal work. Airplane-mode capable."

**2:30 - 2:55 — Google Stack + Closing**
- Show deployed URL in browser bar (Cloud Run domain).
- Mention in voice: "The entire platform runs on Google Cloud Run with auto-scaling. All LLM decisions use the Gemini API as required."
- Final screen: Team/contact, "Real users. Real revenue. AI agents running the business 24/7. Thank you."
- End card with links: Deployed demo, GitHub repo, Devpost submission, "Wake the Ents."

**Total target: 2:45 or less. Leave breathing room for natural pacing.**

## Filming Tips
- Use a clean browser profile, good lighting, clear audio.
- Zoom in on important UI (Gemini responses, agent log entries, revenue numbers).
- Show the *live* deployed site as much as possible for "this is running in production".
- If no real revenue yet, use the seeded realistic demo data + be transparent in narrative ("demo data for judging; live Stripe data attached separately").
- Film the agent trigger button press + resulting new log entry appearing.
- Include one shot of the original TUI game or a successful `./grademe.sh` for authenticity.
- End with the repo URL and "All source code + full logs + exports in the linked GitHub."

## Assets to Prepare
- Screenshots of /ops with several real Gemini agent decisions.
- Redacted Stripe dashboard showing revenue by month.
- The generated `xprize_evidence/revenue_*.json` and `.csv`.
- A couple of testimonials (even if from early testers).
- The Cloud Run URL prominently.

Record this, upload unlisted or public, paste the link into the Devpost form.

Good luck — this video + the /ops live demo is what will separate us on the AI-Native Operations criterion.
