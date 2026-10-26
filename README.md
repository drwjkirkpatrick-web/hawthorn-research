# Hawthorn (Crataegus spp.) — A Year in the Medical Literature, Fully Grounded

Welcome! This repository is a complete, citation-grounded review of everything
noteworthy published on hawthorn between **October 2025 and October 2026** —
built for a practicing naturopathic physician, and assembled so that *every
factual claim can be traced, in one hop, to the exact retrieved source.*

If you have ever read an herbal review and wondered "says who?" — this project
is the answer. Each numbered citation in the PDF resolves to a ledger entry,
and each ledger entry carries a **verbatim supporting quotation** captured from
the fetched record. Nothing is taken on faith.

## The headline findings (a taste)

- **Heart failure, network-meta-analyzed.** A 28-trial, 3,650-patient NMA of
  plant extracts in heart failure included hawthorn among 15 botanicals — with
  rankings led by *Terminalia arjuna*, *Salvia miltiorrhiza*, and others.
- **The vasodilator mystery, sharpened.** Isorhamnetin and tamarixetin emerged
  as hawthorn's most active vasodilatory compounds (L-type Ca²⁺-channel
  blockade) — at concentrations ~100× above human plasma levels, which is the
  most honest gap in hawthorn pharmacology this year.
- **Compound-level breakthroughs.** Procyanidin C1 as a senolytic-like
  HSP90-targeting agent; leucocyanidin as a dual AMPK/NRF2 activator in
  steatotic liver disease; vitexin as a PPARγ/ABCG2 antihyperuricemic; and
  **pinnatichromen**, a brand-new flavone glycoside from *C. pinnatifida*.
- **Safety signal.** A case report of *Crataegus mexicana* root-supplement
  intoxication, plus a transporter-level herb–herb interaction demonstration
  (ursolic acid altering MRP2/UGT1A1 handling of a co-administered compound).
- **A nomenclature landmine.** "Large-fruited hawthorn" (*Malus doumeri*) is
  not a *Crataegus* at all — and two of the year's "hawthorn" papers study it.

## What's inside

```
paper/
  hawthorn_review.pdf     the deliverable (12 pages, LaTeX/typeset)
  hawthorn_review.tex     generated LaTeX source
  gen_review.py           single source of truth: prose + table + generator
  draft.md                markdown mirror (runs the citation verifier)
citations/ledger.json     id -> URL -> verbatim evidence quotations
research/
  pages/                  fetched record text (the evidence base)
  batches/                raw search results, rankings, compound data
```

## Rebuild it yourself

```bash
python3 paper/gen_review.py          # regenerates .tex + draft.md from prose + ledger
python3 $SOURCES_PY --ledger citations/ledger.json render \
    --style evidence --replace-in paper/draft.md
python3 $SOURCES_PY --ledger citations/ledger.json verify \
    paper/draft.md --evidence --min-coverage 0.5
cd paper && pdflatex hawthorn_review.tex && pdflatex hawthorn_review.tex
```

(`$SOURCES_PY` = `~/.hermes/skills/research/grounded-citations/scripts/sources.py`)

## How the evidence trail works

1. **Search:** PubMed via NCBI E-utilities, window 2025-10-25 → 2026-10-26;
   502 records matched, 89 hawthorn-titled, 52 retained. Compound formulas and
   molecular weights come from PubChem PUG REST; the trial-pipeline section
   from the ClinicalTrials.gov API v2.
2. **Register:** every retrieved source entered a citation ledger *at retrieval
   time* — never reconstructed from memory.
3. **Quote:** each of the 70 cited sources carries a verbatim quotation,
   programmatically extracted from the saved record text (whitespace-collapsed
   match, never retyped).
4. **Verify:** the markdown mirror passes `verify --evidence` (66% of prose
   sentences carry declared provenance; 0 claims required an `[unverified]`
   marker). The rendered PDF is checked with `pdftotext`: every citation id
   resolves, every load-bearing fact string is present, zero overfull boxes,
   zero leaked markup.

## A note on AI assistance

This review was drafted with AI assistance (Hermes Agent) as support for the
authoring clinician. It is a literature synthesis, not medical advice, and the
clinical-synthesis section is explicitly labeled as interpretation. Final
clinical judgment belongs to the treating practitioner.

— Compiled October 25, 2026 · 70 cited sources · every one traceable.