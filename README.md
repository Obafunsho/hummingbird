# 🐦 Hummingbird

**GP Cancer Referral Decision Support — Lower GI MVP**

> Clinical lead: Prof Aneel Bhangu, Consultant Colorectal Surgeon  
> Technical lead: Data Analyst (TBC)  
> Version: 1.0 | March 2026 | Classification: Confidential

---

## What it does

Hummingbird takes a suspected colorectal cancer presentation and returns one of six defined recommendations in under 45 seconds. It reduces inappropriate urgent 2WW referrals without missing cancers.

**Six output tiers:**
1. `2WW_URGENT` — Refer immediately via USC pathway
2. `ROUTINE_REFERRAL` — Refer non-urgently to colorectal outpatients
3. `INVESTIGATE_FIRST` — Order FIT or other investigation first
4. `SAFETY_NET_ACTIVE` — Retain with specific booked review
5. `SAFETY_NET_PASSIVE` — Return if symptoms worsen/persist
6. `REASSURE_DISCHARGE` — Discharge with safety netting advice

---

## Setup

### 1. Clone and install

```bash
git clone <repo-url>
cd hummingbird
pip install -r requirements.txt
```

### 2. Set API key

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. Run

```bash
streamlit run app.py
```

---

## Repository structure

```
hummingbird/
├── app.py                          # Main Streamlit application
├── requirements.txt
├── .env.example                    # API key template (never commit .env)
├── prompts/
│   ├── prompt_registry.json        # Active version per cancer site
│   └── lower_gi/
│       └── system_prompt_v1.0.txt  # Versioned system prompt
├── validation/
│   ├── run_vignettes.py            # Automated validation runner
│   └── lower_gi/
│       └── vignettes.json          # 50 clinical test cases (to populate)
├── config/
│   ├── qr_urls.json                # URL mapping per output tier
│   └── output_taxonomy.json        # Six tier definitions
├── logic/
│   ├── hard_rules.py               # Layer 1 deterministic rules
│   ├── claude_layer.py             # Layer 2 API call and parsing
│   ├── pdf_generator.py            # WeasyPrint PDF output
│   ├── qr_generator.py             # QR code generation
│   └── audit_logger.py             # Append-only audit log
├── templates/
│   └── (PDF HTML template embedded in pdf_generator.py)
└── audit/
    └── audit_log.csv               # Append-only, never delete rows
```

---

## Clinical decision architecture

**Layer 1 — Deterministic hard rules** (run first, short-circuit to 2WW_URGENT):
- Rectal bleeding + age ≥50
- FIT positive (any presentation)
- Palpable mass (any presentation)
- Iron deficiency anaemia + age ≥60
- Change in bowel habit + age ≥60
- Rectal bleeding + change in bowel habit (any age)
- Unexplained weight loss + rectal bleeding (any age)
- IDA in females ≥50 or males ≥40

**Layer 2 — Claude AI reasoning** (only if Layer 1 does not trigger):
- Full clinical context passed to `claude-sonnet-4-6`
- System prompt: `prompts/lower_gi/system_prompt_v1.0.txt`
- Returns structured JSON with tier, rationale, safety net, confidence

---

## Prompt management

Every prompt change must be:
1. Saved as a new versioned file (e.g. `system_prompt_v1.1.txt`)
2. Registered in `prompt_registry.json` with date and rationale
3. Run through the full vignette validation suite (`python validation/run_vignettes.py`)
4. Signed off by Prof Aneel Bhangu before going live
5. Old prompts archived — **never deleted**

---

## Validation

```bash
python validation/run_vignettes.py --verbose
```

Minimum pass threshold: **96% (48/50)**  
Any Layer 1 failure is an automatic block regardless of overall score.

---

## Regulatory status

**MVP** launches as a clinical education and audit tool — outside SaMD classification.  
No MHRA registration required at this stage.

The audit logging, prompt versioning, and validation framework built here creates the evidence base for a future **Class IIa SaMD** submission.

See the technical briefing document for the full regulatory pathway.

---

## Audit log

Every recommendation is logged to `audit/audit_log.csv`. This file is:
- Append-only (rows are never deleted)
- A regulatory requirement
- The primary research dataset for NIHR validation
- Required for MHRA submission evidence

---

*This tool supports but does not replace clinical judgement.*
