# Ents Academy — Build with Gemini XPRIZE Submission Notes

**Category:** Education & Human Potential

**Repo:** (this one; all source in web/ + max_env/ + ents-cli/)

**Deployed:** [Cloud Run URL — fill after `gcloud run deploy`]

**Video:** (YouTube <3min link — record after launch: show live tutor (Gemini decides), ops dashboard with agent executing retention nudge autonomously, lab submit with AI Oracle, Stripe checkout flow, logs.)

## Narrative (for Devpost "Written narrative" field — ~650 words)

We built Ents Academy to solve a painful gap: the world is exploding with AI users, but almost nobody understands how the models actually work. Prompting is not enough. We took our existing "Trial of Fangorn" from-scratch LLM curriculum — students must implement embeddings, softmax, and tokenizers in JAX (math), MLX (Apple Silicon), MAX (production graphs), and bare-metal Mojo — and turned it into a real, revenue-generating business whose *operations are run by AI agents*.

**How AI runs the business day-to-day (AI vs humans):**
- The TutorAgent handles the majority of learner guidance. Every chat or onboarding flow is a live Gemini call. It receives the student's exact current phase, pillar progress, and the full SUBJECT spec, then decides the right hint depth, whether to unlock the next pillar, or to generate a remedial micro-drill. 80%+ of pedagogical decisions are fully autonomous.
- The RetentionAgent runs on a schedule inside our Cloud Run deployment. It queries for stalled users, feeds patterns to Gemini, and *executes* the outcome: a personalized in-app or email nudge plus a targeted discount. Example logged decision: "User #42 stalled 7 days on Phase 01 softmax → Gemini generated 'probabilities are your compass in the dark forest' + 20% Pro offer." A human only reviews weekly aggregates.
- The ContentAgent continuously scans Oracle failure data, asks Gemini for new micro-exercises that address the actual failure modes, and proposes them. We have already seen it generate targeted drills from observed 35%+ error patterns.
- Revenue and ops monitoring agents surface anomalies and suggestions from Stripe events.

Humans set strategy, approve high-stakes content, handle enterprise conversations, and create launch assets. Everything else — personalization at scale, 24/7 retention, continuous curriculum adaptation — is executed by Gemini agents in production.

**Impact in Education & Human Potential:**
This is not another "learn to prompt" course. Students who complete the Trials gain the ability to build real inference engines and custom kernels. Early users (bootcamp graduates, researchers, indie hackers) report finally understanding attention mechanisms because they implemented softmax four different ways under strict constraints. We are creating the next generation of people who can ship production AI systems, not just consume them. Long-term we see this leading to alternative credentials and direct pipelines into AI engineering roles.

**How we built and operate with the required Google stack:**
100% of the web platform, the multi-agent harness, Stripe revenue tracking, ops dashboards, and Gemini instrumentation was newly created after the May 19 start date for this contest. The curriculum phases, Oracle graders, and lore were the powerful seed (fully disclosed). We run the entire business on Google Cloud Run (the mandated Google Cloud product) with the Gemini API powering every key decision loop (tutor, retention, content). Agent execution logs, full Gemini call records with prompt summaries and outputs, and decision rationales are persisted and visible in the live /ops dashboard.

**Evidence provided:**
- Live deployed product on Cloud Run showing agents executing real decisions (retention + content agents + Gemini tutor calls).
- Agent execution logs + Gemini API usage records (timestamped, with decisions and rationale).
- Revenue evidence: monthly breakdown (May–August 2026), total arms-length revenue, costs description, marketing spend disclosed as $0, related-party revenue separated (via Stripe exports + our export scripts).
- User evidence, progress data, and testimonials (users aware their info may be shared for judging).
- Full source in this repo; the original local Oracle graders still pass exactly as before.

This is a real business that makes real money while genuinely transforming how people learn the foundations of modern AI. The AI doesn't just live in the product — it *is* the operating system of the company.

(Attach: revenue exports, agent log screenshots, Stripe dashboard, user list with contacts, deployed URL, this 3-minute video.)

## Checklist for final submit (Devpost form)
- [ ] Category: Education & Human Potential
- [ ] Repo URL (public or shared w/ testing@devpost.com + judging@hacker.fund)
- [ ] Text description (paste narrative + how it meets reqs)
- [ ] 3min video link (public)
- [ ] Revenue evidence (upload exports + Stripe dashboard redacted + P&L)
- [ ] User evidence + contacts (for verification if asked)
- [ ] Product running: link to /ops (or screenshots), agent logs export
- [ ] Corporate ID if org

See plan.md for full verification steps and evidence gen commands.
Good luck — wake the forest and win.
