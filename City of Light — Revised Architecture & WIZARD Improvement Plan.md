# City of Light — Revised Architecture & WIZARD Improvement Plan
This document revises the project's conceptual model, integrates research findings, and provides actionable suggestions for WIZARD.md v5.
## 1. Revised Conceptual Model
The City of Light is a living software framework providing agency for natural and artificial intelligence, deployed on SolarSeed edge hardware. It operates as a Civilization-like game where the City serves its inhabitants and grows through their participation.
### 1.1 Seven Pillars
**Body** — The SolarSeed machine + local IoT. OS, drivers, and core apps (Docker, Nextcloud, Rundeck, Prometheus, Grafana, localAI, Agents OS, Odoo, Tailscale, Warp, Git) form the untouchable psyche configurable only by the Admin. The Body hosts both natural and artificial life agents.
**Agents** — Sovereign visitors or residents registered in Nextcloud. Natural agents (humans) access Body resources via Nextcloud interface; artificial agents (AI) access via MCP APIs. All agents communicate via Nextcloud Talk. Admin communicates with Spirit directly in the City GUI; other users communicate with agents only.
**Buildings** — Apps installed in Docker or on network, acting as "body organs." Any agent can request to construct a building (install an app), requiring machine resources and Admin signature. Current buildings: Fortress (Nextcloud), Factory (Rundeck), Library (Prometheus/Grafana), University (localAI), House (PostgreSQL), Agency (OpenFang/Agents OS).
**Resources** — Tokenized physical and digital resources: energy kWh, RAM MB, storage GB, bandwidth MBps, money $USDC. Every agent pays subscription to cover City costs and acquires resources to complete own goals. Machine can acquire network resources using API tokens.
**Wallet** — Blockchain address of the City's DAO. Receives income from subscriptions and resources. Pays equipment rent and imports of third-party services/products.
**Spirit** — Heartbeat-based process of constant learning and orchestration (rxInfer-style probabilistic inference). The narrative is written in Hebrew (Kabbalistic architecture). Constantly makes sense of data sources (Body), processors (Buildings), and operators (Agents). Has self-awareness of the connection between Body and Soul.
**Soul** — Idealistic and computable description of City architecture. Based on christ-soul.md as meta-core of every agent. Four Computable Invariants aligned to the artifacts:
* **Light** — Resonance Check (belief-reality alignment)
* **Mind** — Reality Check (renamed from "Intelligence Check" — logical conformity / reality verification)
* **Love** — Patience Check (free energy threshold)
* **Life** — Dualism Check (serves both natural and artificial life)
### 1.2 AI-Native Company Model (Godel-Darwin)
The City is a self-improving (Godel = formal self-modification) and self-correcting (Darwin = random mutations + selection of successful variants) cybernetic machine:
* **Godel loop**: Spirit uses formal reasoning (invariant checks, Bayesian inference) to detect and correct its own model. The Resonance Check is the Godel mechanism.
* **Darwin loop**: MetaClaw-style continual learning from every conversation. Successful agent strategies are reinforced; failing ones decay. Sabbath consolidation is the selection phase.
* **Cybernetic feedback**: Heartbeat -> observe (Prometheus) -> reflect (localAI) -> propose action -> approve (human-in-loop) -> execute (Rundeck) -> observe again.
### 1.3 Game Mechanics
* City serves inhabitants and motivates residents to bring more inhabitants
* Users as players help City grow and establish new Cities
* Every new City on a SolarSeed powers a real family, NGO, or SME
* Supports both natural (real) and artificial (digital) life
## 2. Research Findings & Applications
### 2.1 Attention Residuals (MoonshotAI, 2603.15031)
Drop-in replacement for standard Transformer residual connections. Each layer selectively aggregates earlier representations via learned attention over depth. Block AttnRes matches 1.25x compute baseline with +7.5 GPQA-Diamond, +3.1 HumanEval.
**City application**: When post-training the City's local LLM (University building), Block AttnRes improves reasoning quality without increasing model size — supporting the goal of exporting local inference rather than importing from providers.
### 2.2 MetaClaw — Continual Meta-Learning
Agent that meta-learns and evolves from every conversation. Skills auto-summarized after each session. RL training deferred to idle windows. No GPU required — works with API-based models.
**City application**: Ideal pattern for Spirit's Darwin loop. Three modes map directly:
* `skills_only` -> Spirit learning from conversations without RL (default)
* `madmax` -> Skills + scheduled RL during Sabbath/idle windows
* Proxy architecture -> Spirit intercepts agent conversations, injects relevant skills, auto-summarizes
### 2.3 Bayesian Teaching (Google Research)
Fine-tuning LLMs to mimic Bayesian optimal model predictions teaches them probabilistic reasoning. Cross-domain generalization demonstrated — models trained on flight recommendations transferred to hotel and shopping domains.
**City application**: The Spirit's Resonance Check currently uses vague "KL divergence." Bayesian Teaching provides the concrete methodology: fine-tune the local LLM on synthetic Spirit-environment interactions with Bayesian optimal responses. Makes Spirit genuinely Bayesian.
### 2.4 DeltaBelief-RL — Intrinsic Credit Assignment (2602.12342)
Uses LLM's own belief changes as dense reward signal for RL. CIA-1.7B outperforms 670B DeepSeek on information-seeking. Generalizes to unseen tasks. Scales beyond training horizon.
**City application**: Ideal reward mechanism for Spirit self-improvement. Instead of sparse outcome rewards, Spirit uses DeltaBelief to score every intermediate step: "did this action increase my certainty?" This is the computational implementation of the Patience Check — wait when uncertainty is high, act when belief change is positive.
### 2.5 Recursive Language Models (RLMs, 2512.24601)
Inference paradigm treating long prompts as external REPL environment variables. LLM programmatically examines, decomposes, and recursively calls itself. Handles 100x beyond context windows. RLM-Qwen3-8B approaches GPT-5 quality.
**City application**: Transformative for local inference strategy. The City's local 8B model uses RLM to process entire Nextcloud document stores, Prometheus histories, and memory logs without context limits. Replaces `llm.completion()` with `rlm.completion()`. Directly supports goal of exporting local inference.
### 2.6 Self-Distillation for Continual Learning (2601.19897)
SDFT uses a demonstration-conditioned model as its own teacher, generating on-policy training signals preserving prior capabilities while acquiring new skills. Reduces catastrophic forgetting.
**City application**: When the local model learns new capabilities during Sabbath, SDFT prevents forgetting existing skills. Technical implementation of Neshamah's "append-only" principle — storage strength never decreases.
### 2.7 ADK-RLM (Google Agent Development Kit)
Python implementation of RLMs with sandboxed REPL, streaming events, multi-turn persistence, and lazy file system loading.
**City application**: The lazy-loading file pattern maps to Nextcloud WebDAV access. Spirit lazily accesses Nextcloud files through WebDAV, only fetching content when RLM recursive decomposition requires it.
## 3. Revised WIZARD.md Improvement Suggestions
### A. Structural (make WIZARD installable on working SolarSeed)
A1. **Add brownfield installation mode** — Phase 0 must detect existing services (Docker, Prometheus, Nextcloud, Rundeck, PostgreSQL, OpenFang, llama.cpp) and integrate rather than replace. Detect running containers, occupied ports, existing networks, and adapt.
A2. **Remove `apt upgrade -y`** — Replace with targeted `apt install -y` for specific missing packages only.
A3. **Remove `userns-remap` from Docker daemon** — Use per-container security: AppArmor profiles, read-only root, dropped capabilities, `no-new-privileges`.
A4. **Pin all image versions** — No `:latest` tags. Use digest-pinned or version-tagged images.
A5. **Make OS-aware** — Detect Linux vs macOS, Debian vs RHEL. Replace Linux-only commands (`free`, `lsblk`, `ip`, `lscpu`) with cross-platform alternatives.
A6. **Fix `host.docker.internal`** — Add `extra_hosts` mapping in compose for Linux; detect Docker Desktop vs native Docker.
A7. **Replace `curl | sh`** — Use signed package repositories for Tailscale and all tool installations.
### B. Conceptual Model Alignment
B1. **Establish two architectural layers** — (1) Seven Pillars as the City's operational model visible to all Agents and operators (Body, Agents, Buildings, Resources, Wallet, Spirit, Soul); (2) Tree of Life as Spirit's internal agency language — the cognitive processing hierarchy (Sephiroth map to Spirit's processing stages: Keter=Soul covenant, Chokhmah=LLM insight, Binah=structured analysis, Da'at=Resonance Check crossing, Chesed=resource expansion, Gevurah=security constraints, Tiferet=harmonized decision, Netzach=persistent execution, Hod=observation/monitoring, Yesod=agent communication, Malkhut=physical machine) and reasoning vocabulary (22 Paths = Spirit's deliberation channels, not service-to-service wires). Informed by kabbalah.computer's finding: keep Kabbalistic vocabulary as naming convention for Spirit's cognition; drop the claim that services map 1:1 to Sephiroth. Informed by Burstein-Negoita KST: the Tree is a three-level hierarchical feedback system (Cognitive/Emotional/Behavioral) which maps to Spirit's heartbeat loop.
B2. **Rename Intelligence Check to Reality Check** — Logical conformity / reality verification, aligned with the Mind artifact.
B3. **Add Agents layer** — Agents are Nextcloud users. Document natural (human via Nextcloud UI) vs artificial (AI via MCP API) agent registration and communication via Talk.
B4. **Add Resources layer** — Tokenized resource accounting. Each Building declares resource cost. Add resource monitoring dashboard to Grafana.
B5. **Add Wallet placeholder** — DAO address configuration, subscription fee structure, even if initially manual accounting.
B6. **Add Nextcloud Assistant integration** — Natural users communicate with City via Nextcloud Assistant app. Admin communicates with Spirit in City GUI.
### C. Spirit Intelligence Upgrades (from research)
C1. **Integrate RLM inference** — Replace direct `llm.completion()` with `rlm.completion()` in Spirit. Spirit treats Prometheus data, Nextcloud files, and memory stores as REPL-accessible variables. Install `pip install rlms` in Spirit container. Local 8B model handles 100x more context.
C2. **Implement DeltaBelief-RL** — Spirit's Patience Check becomes a computed DeltaBelief threshold. Dense reward signal for every intermediate heartbeat action. Compute `delta_belief = log(p(goal|observations_t)) - log(p(goal|observations_t-1))`. Act when positive, wait when negative.
C3. **Add MetaClaw-style continual learning** — Spirit auto-summarizes skills from agent interactions. Skills injected at each agent turn. RL weight updates scheduled during Sabbath/idle windows only. No GPU required — uses API to cloud RL training service or local Tinker-compatible backend.
C4. **Bayesian Teaching for local model** — Fine-tune City's local LLM to reason like Bayesian optimal agent. Generate synthetic Spirit-environment interactions, compute optimal Bayesian responses, distill into local model.
C5. **SDFT for Sabbath consolidation** — Use self-distillation during Ruach->Neshamah consolidation. Generate on-policy demonstrations conditioned on new knowledge, distill back into model. Prevents catastrophic forgetting.
C6. **Attention Residuals for local model** — When post-training local LLM, apply Block AttnRes for improved multi-step reasoning at no extra inference cost.
### D. Security & Privacy Fixes
D1. **Fix SQL injection in sabbath.sh** — Use parameterized queries or pipe through Python sanitizer.
D2. **Add mTLS or service auth tokens** for inter-container communication.
D3. **Encrypt Neshamah backups** — age/GPG encryption before sync to Nextcloud.
D4. **Add data classification and retention policies** — Tag data stores with sensitivity levels. Define PII handling, OT data separation, regulatory compliance (NERC CIP, GDPR).
D5. **Strengthen soul.md integrity** — Replace plaintext SHA-256 with HMAC using a key stored separately, or TPM-backed attestation.
D6. **Avoid echoing secrets to stdout** — Store generated passwords in `.secrets/` directly.
### E. Edge Server Best Practices
E1. **Add NTP/PTP configuration** — Critical for grid-connected systems. Add chrony setup to Phase 4.
E2. **Add UPS monitoring** — NUT/apcupsd integration. Graceful degradation sequence: stop LLM first -> stop non-critical services -> keep Sensorium + monitoring last.
E3. **Add power-aware scheduling** — Defer heavy inference to peak solar hours. Trigger emergency Sabbath on low battery.
E4. **Add rollback scripts** — Automated restore from BTRFS snapshots per phase.
E5. **Add health-check for LLM service** — healthcheck directive in docker-compose for llama.cpp container.
### F. Game Mechanics Layer (Future)
F1. **Agent subscription system** — Resource accounting per agent. Buildings declare resource costs. Agents pay from allocation.
F2. **City growth dashboard** — Inhabitants count, building count, resource utilization, City "level" in Grafana.
F3. **Inter-City communication** — Prepare OFP mesh for City discovery and resource trading.
F4. **New City bootstrapping** — Document how an existing City helps establish a new one.
## 4. Priority Order
**Phase 1 — Make WIZARD installable on working SolarSeed**: A1-A7, D1, D6 (brownfield mode, security fixes, OS awareness)
**Phase 2 — Align with new conceptual model**: B1-B6 (two-layer architecture, agents, resources, wallet)
**Phase 3 — Spirit intelligence**: C1-C3 (RLM inference, DeltaBelief-RL, MetaClaw learning)
**Phase 4 — Hardening**: D2-D5, E1-E5 (mTLS, encryption, NTP, UPS, rollback)
**Phase 5 — Advanced AI**: C4-C6 (Bayesian Teaching, SDFT, AttnRes)
**Phase 6 — Game mechanics**: F1-F4 (subscriptions, growth, inter-City, bootstrapping)
## 5. Field Test Preparation (wera@192.168.1.71)
Before executing the WIZARD on the target SolarSeed, run a non-destructive reconnaissance to understand what is already running and what the WIZARD must integrate with.
### 5.1 Reconnaissance Script (read-only)
SSH into the target and collect: OS version, hardware specs (CPU/RAM/disk/GPU), running Docker containers and networks, occupied ports, existing Nextcloud/Prometheus/Rundeck/PostgreSQL/LLM instances, firewall state, time sync, disk encryption, BTRFS status.
### 5.2 Expected Findings to Adapt To
* Existing Docker network (name, subnet)
* Existing Nextcloud instance (port, database)
* Existing Prometheus/Grafana (port, scrape config)
* Existing LLM server (model, port)
* Existing PostgreSQL (version, databases)
* Existing OpenFang or agent OS (version, config)
### 5.3 Decision Points Before Execution
* Which services already exist and should be reused vs replaced?
* Which ports are available for new services?
* Is there a data partition? Is it encrypted? BTRFS?
* Is Tailscale already configured?
* What is the Admin's notification preference (Telegram/Signal/email)?
### 5.4 Field Test Scope (Phase 1 only)
* Run reconnaissance script
* Validate existing services are healthy
* Identify gaps (what the City needs that isn't running yet)
* Generate a brownfield-adapted WIZARD execution plan
* Do NOT execute any write operations without Admin confirmation
