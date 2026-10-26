#!/usr/bin/env python3
"""Generate hawthorn_review.tex + draft.md from PROSE + the citation ledger.

Single source of truth: DOC below — plain Unicode text with [n] citation
markers and *italics*. Emits LaTeX (escaped, \\src{} macros, \\emph from
*...*) and a markdown mirror for the grounded-citations verifier. The
Sources block is generated mechanically from the ledger, never typed.
"""
import json, os, re, subprocess, sys

PROJ = os.path.expanduser('~/projects/hawthorn-research')
S = '/home/walker/.hermes/skills/research/grounded-citations/scripts/sources.py'
LEDGER = f'{PROJ}/citations/ledger.json'
PAPER = f'{PROJ}/paper'
os.makedirs(PAPER, exist_ok=True)

TITLE = (r"Hawthorn (\emph{Crataegus} spp.): A Clinician-Oriented Review of the Past "
         r"Year's Medical Literature (October 2025--October 2026) with a Phytochemical Update")
TITLE_PLAIN = ("Hawthorn (Crataegus spp.): A Clinician-Oriented Review of the Past Year's "
               "Medical Literature (October 2025 - October 2026) with a Phytochemical Update")
AUTHOR = "Walker Kirkpatrick, ND"
DATE = "October 25, 2026"

NOTICE = ("Draft prepared with AI assistance (Hermes Agent) as literature-review support for the "
          "authoring clinician. Not medical advice; factual claims drawn from the literature carry "
          "numbered citations to retrieved sources, and the full evidence trail (verbatim quotes, "
          "ledger, fetched text) is preserved in the project repository. Clinical decisions remain "
          "the responsibility of the treating practitioner.")

# ---------------------------------------------------------------- compound table
TABLE = [
    ("Vitexin", "Flavone C-glycoside", "C21H20O10", "432.4",
     "Lead antihyperuricemic flavonoid; PPARγ/ABCG2 [16][70]"),
    ("Hyperoside", "Flavonol O-glycoside", "C21H20O12", "464.4",
     "Chief species-differentiating marker [50][71]"),
    ("Rutin", "Flavonol O-glycoside", "C27H30O16", "610.5",
     "Cardioprotective food flavonoid panel [30][84]"),
    ("Quercetin", "Flavonol aglycone", "C15H10O7", "302.2",
     "CNS-relevant constituent of *C. azarolus* [59][72]"),
    ("Isorhamnetin", "Methylated flavonol", "C16H12O7", "316.3",
     "Most active vasodilator in ex-vivo screen [54][73]"),
    ("Tamarixetin", "Methylated flavonol", "C16H12O7", "316.3",
     "Vasodilator; L-type Ca²⁺-channel blockade [54][74]"),
    ("(-)-Epicatechin", "Flavanol", "C15H14O6", "290.3",
     "741.3 mg/g in bark fraction I [18][75]"),
    ("(+)-Catechin", "Flavanol", "C15H14O6", "290.3",
     "Predominant fruit phenolic after digestion [24][76]"),
    ("Procyanidin B2", "Procyanidin dimer", "C30H26O12", "578.5",
     "88.8% of phenolics in bark fraction II [18][77]"),
    ("Procyanidin C1", "Procyanidin trimer", "C45H38O18", "866.8",
     "Senolytic-like; direct HSP90 target [15][78]"),
    ("Leucocyanidin", "Flavan-3,4-diol", "C15H14O7", "306.3",
     "Dual AMPK/NRF2 activator in MASLD [69][79]"),
    ("Ursolic acid", "Triterpenoid acid", "C30H48O3", "456.7",
     "Alters MRP2/UGT1A1 handling of THSG [56][80]"),
    ("Maslinic acid", "Triterpenoid acid", "C30H48O4", "472.7",
     "Synergy driver with notoginseng saponins [63][81]"),
    ("Chlorogenic acid", "Phenolic acid ester", "C16H18O9", "354.3",
     "Major phenolic-acid class in 4-species survey [68][82]"),
    ("Ellagic acid", "Phenolic acid lactone", "C14H6O8", "302.2",
     "109% intestinal bioaccessibility (hawthorn) [32][83]"),
    ("Cyanidin 3-O-arabinoside", "Anthocyanin", "C20H19O10+", "419.4",
     "CD36/AMPK/PGC-1α axis (*Malus doumeri*) [64][85]"),
    ("Lucenin-2", "Flavone C-glycoside", "C27H30O16", "610.5",
     "GC-MS constituent with CNS hypotheses [59][86]"),
    ("Pinnatichromen", "Novel flavone glycoside", None, None,
     "New natural product; inhibits IL-1β production [33]"),
]

# ---------------------------------------------------------------- prose
DOC = [
("Summary", [
 ('p', "This review covers the peer-reviewed medical and pharmacological literature on hawthorn "
       "(*Crataegus* spp.) published in the twelve months from October 25, 2025 through October 26, "
       "2026, as indexed in PubMed/MEDLINE. A topic search returned 502 date-matched records, of which "
       "89 carried *Crataegus* or hawthorn in the title; after relevance triage, 52 focused reports "
       "ground this review, supplemented by PubChem records for compound structures and a "
       "ClinicalTrials.gov query for the trial pipeline."),
 ('p', "The year's clinical yield was modest but real. A network meta-analysis of plant extracts in "
       "heart failure pooled 28 randomized trials (3,650 patients) and included hawthorn extract among "
       "15 evaluated botanicals [1]. A randomized, double-blind, placebo-controlled crossover trial found "
       "that a *Scutellaria baicalensis*/*Crataegus laevigata* supplement with magnesium and chromium "
       "improved mood and stress-buffered cognition in subjectively stressed adults [4]. A single-blind "
       "randomized trial found hawthorn vinegar gargle reduced oral mucositis and improved oral "
       "health-related quality of life in people with diabetes [6]."),
 ('p', "The mechanistic yield was dominated by compound-level work. A systematic ex-vivo screen of 21 "
       "hawthorn constituents identified the methylated flavonols isorhamnetin and tamarixetin as the "
       "most active vasodilators, acting via L-type calcium-channel interference at concentrations well "
       "above typical human plasma levels [54]. Procyanidin C1 emerged as a senolytic-like "
       "anti-atherosclerotic whose direct target is HSP90 [15]; leucocyanidin as a dual AMPK/NRF2 "
       "activator against steatotic liver disease [69]; and vitexin as a multitarget antihyperuricemic "
       "acting on PPARγ and ABCG2 [16]. A new natural product, pinnatichromen, was described from "
       "*C. pinnatifida* leaves [33]."),
 ('p', "Safety and quality signals warrant attention: a case report of acute diarrhea requiring "
       "emergency care after unsupervised use of a *Crataegus mexicana* root-based weight-loss "
       "supplement [57]; a pharmacokinetic demonstration that hawthorn's ursolic acid alters "
       "transporter-mediated handling of a co-administered phytochemical [56]; and metabolomic "
       "confirmation that species, geography, and processing drive large composition differences that "
       "argue for chemotype-controlled products [68][31]."),
]),
("Scope and method", [
 ('p', "Sources. PubMed was searched through NCBI E-utilities (esearch/esummary/efetch) with the term "
       "(*Crataegus* OR hawthorn OR \"WS 1442\") restricted by publication date to 2025/10/25–2026/10/26, "
       "plus seven themed sub-queries spanning clinical trial publication types, phytochemistry, "
       "cardiovascular, metabolic, mechanistic, safety, and neuropsychiatric topics. Titles and "
       "abstracts were triaged for substantive focus on *Crataegus*; 52 records were retained at "
       "abstract level. Chemical formulas and molecular weights in Table 1 were retrieved per compound "
       "from PubChem's PUG REST API, cited individually in the table."),
 ('p', "This is a rapid, structured review, not a systematic review: one database, abstract-level "
       "grounding, no protocol registration, and AI-assisted triage. The trial pipeline statement is "
       "grounded in a ClinicalTrials.gov API v2 query of interventional studies naming *Crataegus* or "
       "hawthorn [87]. Every claim carries a numbered citation to the retrieved record; verbatim "
       "supporting quotations for load-bearing claims are preserved in the project repository. The "
       "limitations of that scope are stated in the closing section."),
]),
("Hallmark phytochemistry: the compounds of *Crataegus*", [
 ('p', "The year's reviews converge on a stable chemical picture in which flavonoids and oligomeric "
       "proanthocyanidins are the principal cardioactive constituents, exhibiting vasodilatory, "
       "antioxidant, mild positive inotropic, and antiarrhythmic properties [11]. A comprehensive "
       "UHPLC-Q-Exactive Orbitrap survey of 54 samples from four species, eleven production areas, and "
       "three drying methods identified 117 components spanning seven chemical classes, with phenolic "
       "acids and flavonoids the predominant constituents [68]. Reviews of the full composition list "
       "flavonoids, triterpenoids, organic acids, and polysaccharides as the major bioactive groups, "
       "alongside coverage of pharmacokinetics and adverse reactions [53][45]."),
 ('p', "Marker flavonoids. The flavone C-glycoside vitexin and the flavonol O-glycoside hyperoside "
       "remain the workhorse markers for species differentiation and quality control: principal-component "
       "analysis of eleven Sicilian *Crataegus* taxa identified hyperoside and vitexin as the main "
       "contributors to sample differentiation, with hyperoside ranging up to 1.47 mg/g dry weight and "
       "total polyphenols peaking at 25.54 mg GAE/g in *C. laciniata* [50]. Among three Turkish endemic "
       "species, *C. peshmenii* leaf extract was richest in vitexin and hyperoside [13]. Free phenolics "
       "in *C. azarolus* leaves reached 78.61 mg GAE/g dry weight, with a further 13.56 mg GAE/g bound "
       "fraction [22]; ethanol extracts of *C. monogyna* carried 80.92 mg GAE/g total phenolics and "
       "51.94 mg RE/g flavonoids [42]. GC-MS profiling of *C. azarolus* flagged quercetin and the "
       "flavone C-glycoside lucenin-2 as constituents of proposed CNS relevance [59]."),
 ('p', "Procyanidins and flavanols. Hawthorn-leaf condensed tannins were confirmed by MALDI-TOF MS to "
       "consist mainly of procyanidins with smaller propelargonidin and prodelphinidin contributions "
       "[60]. Low-pressure chromatography of a procyanidin-rich *C. monogyna* bark extract produced a "
       "fraction that was almost pure procyanidin B2 (88.8% of total phenolics) and higher-polymer "
       "fractions whose antioxidant activity tracked procyanidin oligomer content [18]. A fraction "
       "containing 741.3 mg/g (-)-epicatechin anchored the low-molecular-weight end of that "
       "fractionation [18]. The first detailed phytochemical investigation of the endemic Kazakh "
       "*C. almaatensis* isolated (-)-epicatechin, the flavolignan cinchonain Ia, kakispyrol, and two "
       "diaryl-ether glucosides, with cinchonain Ia showing radical-scavenging activity comparable to "
       "ascorbic acid [26]."),
 ('p', "Triterpenoids, polysaccharides, anthocyanins. Ursolic acid, hawthorn's signature triterpenoid "
       "acid, was shown to enhance intestinal absorption of a co-administered stilbene glycoside by "
       "downregulating efflux transporter MRP2 while upregulating hepatic UGT1A1 [56]. Maslinic acid in "
       "hawthorn juice was implicated as a driver of synergy with notoginseng stem-leaf saponins [63]. "
       "Polysaccharide chemistry advanced on two fronts: acidic, galacturonic-acid-rich leaf "
       "polysaccharides (10.19–435.52 kDa) whose most active fraction suppressed the SREBP-1c pathway in "
       "HepG2 cells [37], and habitat-level quality control showing that galacturonic-acid content and "
       "molecular weight (2.07–5.57 × 10⁶ Da) correlate with radical-scavenging activity across ten "
       "growing regions [62]. The anthocyanin cyanidin 3-O-arabinoside was studied for metabolic "
       "effects, but note it derives from *Malus doumeri*, commercially called \"large-fruited "
       "hawthorn\" and not a *Crataegus* at all [64][34]."),
 ('table', None),
]),
("New natural products and species-level discoveries", [
 ('p', "A previously unreported flavone glycoside, pinnatichromen, was isolated from leaves of "
       "*C. pinnatifida* var. *major* and fully characterized by NMR and ESI-MS; it inhibited IL-1β "
       "production at 20 μM [33]. The *C. almaatensis* study above is the first detailed chemical report "
       "for that species [26], and first flavonoid profiles were published for the Turkish endemics "
       "*C. peshmenii*, *C. petrodavisii*, and *C. christensenii*, with *C. peshmenii* leaves richest in "
       "cardioactive markers [13]. Multi-technique characterization of *C. monogyna* (LC-MS/MS plus DFT "
       "plus docking) quantified antioxidant and enzyme-inhibition profiles relevant to neurochemical and "
       "glycemic targets [42]."),
 ('p', "Biosynthesis genetics moved the field toward predictable chemotypes. A genome-wide analysis "
       "identified 215 MYB transcription factors in *C. pinnatifida* and functionally validated CpMYB5 "
       "as a positive regulator of proanthocyanidin biosynthesis acting on the promoters of CpANR and "
       "CpLAR [65]. Chromosome-scale genomes of two cultivars (809.1 Mb and 760.5 Mb, scaffold N50 48.5 "
       "and 46.8 Mb) tied peel color to CpMYB114-CpANS anthocyanin regulation and seed hardness to "
       "CpMYB44-CpCOMT lignin biosynthesis [61]."),
 ('p', "Bioaccessibility work tempered raw-content claims. Under standardized INFOGEST simulated "
       "digestion, bioaccessible phenolics and antioxidant capacities fell substantially, though catechin "
       "remained the predominant bioaccessible phenolic across three *Crataegus* species [24]. Flavanols "
       "proved the most digestion-stable class in *C. monogyna* fruits, with epicatechin remaining "
       "97–98% bioaccessible and ellagic acid reaching approximately 109% in the intestinal phase [32]. "
       "Freeze-drying preserved the highest antioxidant activity among processing methods [68]."),
]),
("Cardiovascular findings", [
 ('p', "Heart failure. The year's most clinically consequential paper is a systematic review and network "
       "meta-analysis of plant extracts in heart failure, pooling 28 randomized trials and 3,650 "
       "patients across 15 botanicals, hawthorn extract among them [1]. On SUCRA ranking, water extract "
       "of *Terminalia arjuna* bark ranked first for NYHA-class improvement (80.4%), *Salvia "
       "miltiorrhiza* first for LVEF improvement (89.7%), oak wood extract first for quality of life "
       "(100%), and *Astragalus* first for the six-minute walk test (89.5%) [1]. The published abstract "
       "does not report hawthorn-specific ranking statistics, so hawthorn's comparative position within "
       "this network cannot be stated from the retrievable record. The authors' overall conclusion is "
       "that plant extracts can serve as effective adjunctive therapies to improve cardiac function, "
       "quality of life, and prognosis, with cautious interpretation owing to limited studies per "
       "intervention and scarce head-to-head evidence [1]."),
 ('p', "Vasodilatory actives identified. A Fitoterapia screening study tested 21 hawthorn constituents "
       "and absorbable metabolites on porcine coronary arteries, rat aorta, and rat mesenteric arteries, "
       "motivated by the observation that hawthorn lowers arterial blood pressure in humans while the "
       "active component remains unidentified [54]. Isorhamnetin and tamarixetin were the most active "
       "vasodilators, with EC50 values of 21.7 and 30.9 μM in porcine coronary arteries, 16.7 and 23.3 "
       "μM in rat aorta, and 22.2 and 16.8 μM in mesenteric arteries [54]. The relaxation was "
       "endothelium-independent, unaffected by K⁺-channel or cGMP/PKG manipulation, and instead blocked "
       "L-type Ca²⁺-channel-driven vasoconstriction in a dose-dependent fashion [54]. The authors note "
       "frankly that these EC50 values sit orders of magnitude above typical human plasma levels (tens "
       "to low hundreds of nM), so no single hawthorn compound yet explains the clinical blood-pressure "
       "effect at achievable exposures [54]."),
 ('p', "Atherosclerosis. Procyanidin C1 from hawthorn modulated the metabolic-inflammatory axis in "
       "ApoE-/- mice on a high-fat diet and in a D-galactose senescence model, improving serum lipids, "
       "reducing aortic root plaque, vascular senescence markers, and inflammatory adhesion molecules, "
       "suppressing arachidonic-acid metabolic enzymes, and — via DARTS, LC-MS/MS, CETSA, and docking — "
       "identifying HSP90 as a direct target while selectively clearing senescent cells [15]. Polydatin "
       "combined with hawthorn flavonoids reduced atherosclerotic lesion burden by 44.8%, 49.29%, and "
       "72.99% at low, medium, and high doses in ApoE-/- mice, lowering total cholesterol, "
       "triglycerides, LDL, and VLDL, and acting through a YTHDF2-dependent suppression of the "
       "mitochondrial fission effector DRP1 [25]. A seven-herb food-medicine formulation containing "
       "*C. pinnatifida* (Yaoshi Tongyuan Tablet) attenuated dyslipidemia and inflammation via "
       "PI3K/Akt/NF-κB signaling, with kaempferol, isorhamnetin, and quercetin identified as central "
       "actives on AKT1 [29]."),
 ('p', "Reviews and tissue-level support. Comprehensive reviews published this year restate the "
       "mechanistic case — antioxidant, anti-inflammatory, hypolipidemic, antihyperglycemic, "
       "antihypertensive, anticoagulant, anti-ischemic, diuretic, and cardiotonic — for *Crataegus* "
       "species [11][12][51]. The geroprotection frame is new and notable: *Crataegus* phytochemicals "
       "are proposed to act on oxidative stress, inflammaging, mitochondrial dysfunction, cellular "
       "senescence, and the senescence-associated secretory phenotype [51]. At tissue level, leaf "
       "extract of *C. peshmenii* reduced inflammatory and oxidative markers released from isolated rat "
       "thoracic aorta [13], and in a veterinary high-altitude model, *C. oxyacantha* extract in "
       "drinking water raised nitric oxide by 57.1%, SOD by 16.4%, and GPx by 20.6% while lowering "
       "hematocrit 13.1% and improving growth efficiency in cold-stressed broilers [47]. "
       "Food-medicine-continuum reviews position hawthorn fruit among the leading anti-atherosclerotic "
       "materia medica [35]."),
]),
("Metabolic, hepatic, and renal findings", [
 ('p', "Steatotic liver disease was the year's busiest front. Leucocyanidin, a hawthorn flavonoid, "
       "emerged as a dual-target agent in a 60%-fat-diet mouse model and a free-fatty-acid HepG2 model: "
       "dose-dependently reducing liver weight, serum triglycerides and cholesterol, and IL-6/TNF-α, "
       "restoring fatty-acid β-oxidation through the NRF2 antioxidant axis, and suppressing lipogenesis "
       "and fatty-acid uptake through direct allosteric binding to AMPK [69]. Hawthorn procyanidin "
       "extract attenuated NAFLD in mice by remodeling bile-acid profiles (ωMCA, TαMCA, TβMCA, and DCA) "
       "through the gut microbiota, activating hepatic FXR and CYP7A1, and downregulating SREBP1 via the "
       "FXR-FGF15 enterohepatic pathway [17]. A 70% ethanol fruit extract characterized as 17 primary "
       "compounds inhibited ERK and regulated hepatic purine metabolism in NAFLD mice and HepG2 cells "
       "[55]. Reviews synthesize the mechanism set — suppressed hepatic lipogenesis, enhanced fatty-acid "
       "β-oxidation, improved insulin signaling, adipose and bile-acid regulation, and gut-microbiota "
       "reshaping — and conclude the evidence base remains preclinical with limited clinical "
       "investigation [45][40]."),
 ('p', "Polysaccharides carried much of the hepatic story. North hawthorn polysaccharide (200–800 "
       "mg/kg/day for 12 weeks) dose-dependently alleviated weight gain, dyslipidemia, steatosis, and "
       "inflammation, activated the Nrf2/Keap1/HO-1 axis, and restored *Lactobacillus*, "
       "*Bifidobacterium*, and *Akkermansia muciniphila* abundance in mice [46]. Hawthorn polysaccharides "
       "lowered the Firmicutes/Bacteroidetes ratio, raised HDL-C, and lowered LDL-C in high-fat-fed mice "
       "[67], and leaf polysaccharide HLP-1 lowered hepatocyte triglycerides and cholesterol while "
       "suppressing SREBP-1c [37]."),
 ('p', "Urate. Vitexin was identified from 17 hawthorn flavonoid structures (UPLC-MS/MS) by SwissADME "
       "prioritization as the lead antihyperuricemic: in hyperuricemic mice it reduced serum uric acid "
       "by inhibiting hepatic xanthine oxidase (XOD) and ADA, upregulated renal and intestinal ABCG2 "
       "toward normal, modulated OAT1 and GLUT9, and protected liver, kidney, and intestine while "
       "restoring epithelial barrier integrity, consistent with its predicted PPARγ/ABCG2 mechanism "
       "[16]."),
 ('p', "Glycemic targets. Hawthorn-leaf condensed tannins inhibited α-glucosidase with an IC50 of 8.0 "
       "μg/mL (among the stronger botanical values reported this year) through noncovalent binding that "
       "perturbs the tyrosine/tryptophan microenvironment and enzyme secondary structure, and also "
       "suppressed nonenzymatic glycation products, protein carbonylation, and amyloid cross-β "
       "structures [60]. α-Glucosidase and α-amylase inhibition was likewise demonstrated for "
       "*C. azarolus* leaf phenolics [22], *C. monogyna* extracts [42], and machine-learning-optimized "
       "processed hawthorn vinegar [48]."),
 ('p', "Gastrointestinal inflammation. *C. monogyna* fruit extract (100–400 mg/kg, 10 days) "
       "dose-dependently protected colonic mucosa in an acetic-acid colitis model, restoring MDA, thiol, "
       "SOD, CAT, and GPx toward control and normalizing CRP and ALP [66]. Compound-level gut-axis "
       "pharmacology extended beyond the liver: hyperoside, a flavonol glycoside abundant in hawthorn "
       "fruits, protected against *E. coli* endometritis in mice through gut-microbiota-dependent "
       "production of hydroxyphenyllactic acid acting on TLR4 [28]."),
 ('p', "Combinations and caveats. In ovariectomized rats, combining high-intensity interval training "
       "with *C. pentagyna* fruit extract reduced visceral fat by 72.8%, versus 33.7% for training alone "
       "and 65.5% for extract alone, without dose-dependence across 100–300 mg/kg [58]. Hawthorn juice "
       "plus notoginseng stem-leaf saponins improved glucose and lipid parameters and blood viscosity in "
       "a high-fat, high-sugar model, with maslinic acid implicated in saponin transformation and synergy "
       "[63]. Readers should note that the cyanidin 3-O-arabinoside metabolic study, however favorable, "
       "concerns *Malus doumeri*, a species marketed as \"large-fruited hawthorn\" and taxonomically "
       "distinct from *Crataegus* [64][34]."),
]),
("Neuropsychiatric and neuroprotective findings", [
 ('p', "Stress and cognition RCT. In a randomized, double-blind, placebo-controlled crossover trial "
       "(43 enrolled, 35 analyzed; 15 days per arm; NCT05757050), a supplement combining *S. baicalensis* "
       "root and *C. laevigata* fruit extracts with magnesium and chromium acutely reduced serial-3s "
       "subtraction errors, improved serial-7s working-memory performance under a multitasking stressor, "
       "and chronically reduced total mood disturbance, anger/hostility, and trait anxiety, with no "
       "serious adverse effects [4]. Attribution to *Crataegus* specifically is not possible from this "
       "four-ingredient design — the trial supports the combination product, not any single botanical "
       "[4]."),
 ('p', "Neuroprotective mechanisms. Total flavonoids of hawthorn leaves (TFHL), a traditional Chinese "
       "medicine preparation, promoted motor recovery and preserved neurons after spinal cord injury in "
       "rats while inhibiting TLR4 complex formation, NF-κB nuclear translocation, and IL-1β, IL-6, and "
       "TNF-α mRNA expression in microglia [49]. A companion network-pharmacology study mapped 15 active "
       "TFHL compounds to 69 targets enriched in inflammation, oxidative stress, and apoptosis pathways, "
       "with MAPK signaling validated in BV-2 microglia and RAW264.7 macrophages [36]. These are early "
       "preclinical signals in a new indication area for hawthorn leaf flavonoids [49][36]."),
 ('p', "Psychiatric hypotheses and a methodological caution. A chromatographic study of *C. azarolus* "
       "proposed psychiatric implications from its chemistry, highlighting quercetin and lucenin-2 as "
       "constituents with preclinical anxiolytic and antidepressant-like signals [59]. The same GC-MS "
       "analysis tentatively identified \"digitoxin\" among major compounds — an implausible finding for "
       "a rosaceous fruit that illustrates why library-match GC-MS identifications require orthogonal "
       "confirmation before any clinical inference [59]."),
]),
("Safety, quality, and interactions", [
 ('p', "Adverse-event signal. A Colombian case report describes a 41-year-old woman who presented to "
       "the emergency department with 15 days of daily diarrhea, epigastric pain, and moderate "
       "dehydration after unsupervised use of a *Crataegus mexicana* root-based weight-loss supplement; "
       "she recovered with intravenous fluids and analgesics within 48 hours [57]. The report is a "
       "useful reminder that \"natural\" weight-loss products — here a root-based preparation, not the "
       "well-studied leaf and flower extracts — carry real risk when used without supervision [57]."),
 ('p', "Pharmacokinetic interactions. Hawthorn's ursolic acid increased Cmax of the *Polygonum "
       "multiflorum* constituent THSG while decreasing Tmax and terminal half-life, by downregulating "
       "intestinal efflux transporter MRP2 and upregulating hepatic UGT1A1, with reduced serum exosomal "
       "miR-150-5p [56]. This is direct evidence that a hawthorn triterpenoid can alter the disposition "
       "of a co-administered phytochemical — mechanistically relevant to the multi-botanical stacking "
       "common in practice [56]. A dedicated digoxin–hawthorn pharmacokinetic interaction trial "
       "(NCT00006330) is registered on ClinicalTrials.gov as completed, part of a registry record of 37 "
       "interventional studies matching *Crataegus* or hawthorn [87]."),
 ('p', "Quality and variability. Species, production area, and drying method each shifted the "
       "metabolome across 117 identified components, and vacuum freeze-drying preserved the highest "
       "antioxidant activity [68]. Polysaccharide chemistry and bioactivity varied across ten habitats "
       "with structure–activity correlations [62]; marker content varied several-fold across eleven "
       "Sicilian taxa [50]; extraction solvent shifted both yield and bioactivity in *C. monogyna* [42] "
       "and *C. azarolus* [22]. Reviews this year uniformly call for standardization: "
       "chemotype-controlled, preparation-defined formulations with PK/PD-guided dosing [31], "
       "standardization of bioactive components before efficacy and optimal-dose claims [41], and "
       "quality frameworks spanning germplasm to processed product [19]. Methodological guidance for "
       "flavonoid determination in cardioprotective foods, including hawthorn, was reviewed in detail "
       "[30]."),
 ('p', "Nomenclature and authentication. \"Hawthorn\" in commerce does not guarantee *Crataegus*: the "
       "metabolomics and cyanidin 3-O-arabinoside papers this year concern *Malus doumeri*, marketed as "
       "large-fruited hawthorn [34][64]. Combined with tentative GC-MS identifications [59] and "
       "species-dependent content [68][50], the year's literature makes botanical authentication and "
       "chemotype declaration a patient-safety issue, not merely a research nicety [31]."),
]),
("Trial pipeline", [
 ('p', "A ClinicalTrials.gov API query for interventional studies naming *Crataegus* or hawthorn "
       "returned 37 registrations: 23 completed, 9 of unknown status, 2 terminated, 2 not yet "
       "recruiting, and 1 enrolling by invitation [87]. The single active dedicated trial is NCT07166965, "
       "ketone plus hawthorn extract supplementation in congestive heart failure, enrolling by invitation "
       "[87]. Two not-yet-recruiting polyherbal protocols include hawthorn-containing formulas, "
       "including Longqi Jiangzhi decoction for NAFLD (NCT07320456) [87]. The registry anchors for "
       "hawthorn cardiology — the HERB CHF chronic heart failure trial (NCT00343902), the digoxin "
       "interaction study (NCT00006330), and a nitric-oxide-mediated vasodilation study of standardized "
       "extract (NCT01331486) — are all completed [87]. In short, the registered pipeline holds no large "
       "new dedicated hawthorn trial, and near-term evidence generation appears to be riding on small "
       "combination-product studies [87]."),
]),
("Clinical synthesis for practice", [
 ('p', "The paragraphs below are the authoring clinician's synthesis, labeled as interpretation rather "
       "than cited fact."),
 ('p', "Heart failure. The new network meta-analysis keeps plant extracts, hawthorn included, in the "
       "adjunctive conversation, but its headline rankings favor other botanicals, and no new dedicated "
       "hawthorn heart-failure trial appeared in this window [1][87]. Where hawthorn is used, the "
       "evidence base remains the historical leaf and flower extract literature; nothing this year "
       "changes that (interpretation)."),
 ('p', "Blood pressure. The vasodilator screening sharpens the target — methylated flavonols acting on "
       "vascular smooth-muscle calcium channels — while demonstrating that no single compound reaches "
       "active plasma concentrations, which argues either for whole-extract synergy or for formulation "
       "work rather than single-ingredient supplementation [54] (interpretation)."),
 ('p', "Metabolic and hepatic indications. The steatotic-liver mechanistic base (procyanidins, "
       "leucocyanidin, polysaccharide gut–liver signaling) grew substantially this year, but every "
       "relevant study was in mice or cells [69][17][15][46]; no human metabolic endpoint trial "
       "appeared in this window, so hawthorn's metabolic role remains adjunctive and unproven in humans "
       "(interpretation)."),
 ('p', "Stress, mood, and topical use. One positive multi-ingredient RCT supports a *Crataegus "
       "laevigata*-containing combination for stress and mood [4]; one positive RCT supports hawthorn "
       "vinegar gargle for diabetic oral mucositis [6]; neither licenses monotherapy claims for "
       "*Crataegus* (interpretation)."),
 ('p', "Product selection. Given demonstrated species-, geography-, and processing-driven composition "
       "differences, clinicians should prefer chemotype-declared, standardized extracts and treat "
       "authenticity — *Crataegus* versus marketed \"hawthorns\" from other genera — as a first-order "
       "selection criterion [68][31][34] (interpretation)."),
 ('p', "Safety. This year added a root-product case report [57] and a transporter-interaction "
       "mechanism [56] to the long-standing benign-tolerability record [4]; the practical takeaways are "
       "to avoid unregulated root-based weight-loss products, to review concomitant botanical stacks, "
       "and to remember the historical digoxin co-administration question when hawthorn is used "
       "alongside narrow-therapeutic-index cardiotonics [87] (interpretation)."),
]),
("Limitations", [
 ('p', "This review is deliberately scoped and its limits are explicit. It covers PubMed/MEDLINE "
       "only, so literature in databases or languages outside that index is not represented; grounding "
       "is at abstract level, with full texts not retrieved; triage was AI-assisted; the base "
       "literature is dominated by preclinical and food-science designs with heterogeneous species, "
       "plant parts, extracts, and doses, limiting synthesis [1]; several high-visibility items report "
       "hawthorn-inclusive rather than hawthorn-specific statistics [1]; and in-vitro potency values "
       "frequently exceed achievable human exposures [54]. Counts (502 records matched; 89 "
       "hawthorn-titled; 52 retained) are method outputs from this search, not bibliometric claims. No "
       "load-bearing claim in this review required an unverified marker; where the retrievable record "
       "could not support a claim, the claim was not made."),
]),
]

# ---------------------------------------------------------------- latex escaping
UMAP = {
 '\u03b1': r'$\alpha$', '\u03b2': r'$\beta$', '\u03b3': r'$\gamma$', '\u03b4': r'$\delta$',
 '\u03b5': r'$\varepsilon$', '\u03b6': r'$\zeta$', '\u03b7': r'$\eta$', '\u03b8': r'$\theta$',
 '\u03b9': r'$\iota$', '\u03ba': r'$\kappa$', '\u03bb': r'$\lambda$', '\u03bc': r'$\mu$',
 '\u00b5': r'$\mu$', '\u03bd': r'$\nu$', '\u03be': r'$\xi$', '\u03c0': r'$\pi$',
 '\u03c1': r'$\rho$', '\u03c3': r'$\sigma$', '\u03c4': r'$\tau$', '\u03c5': r'$\upsilon$',
 '\u03c6': r'$\varphi$', '\u03c7': r'$\chi$', '\u03c8': r'$\psi$', '\u03c9': r'$\omega$',
 '\u0391': r'$\Gamma$', '\u0392': r'$B$', '\u0394': r'$\Delta$', '\u0398': r'$\Theta$',
 '\u039a': r'$\Kappa$', '\u039b': r'$\Lambda$', '\u03a0': r'$\Pi$', '\u03a3': r'$\Sigma$',
 '\u03a6': r'$\Phi$', '\u03a8': r'$\Psi$', '\u03a9': r'$\Omega$',
 '\u00b1': r'$\pm$', '\u00d7': r'$\times$', '\u00f7': r'$\div$', '\u2248': r'$\approx$',
 '\u2264': r'$\leq$', '\u2265': r'$\geq$', '\u2192': r'$\rightarrow$',
 '\u2194': r'$\leftrightarrow$', '\u00b0': r'$^{\circ}$', '\u2022': r'\textbullet{}',
 '\u2013': '--', '\u2014': '---', '\u2018': '`', '\u2019': "'",
 '\u201c': '``', '\u201d': "''", '\u2026': r'\ldots{}', '\u00a7': r'\S{}',
 '\u2212': '-', '\u2245': r'$\cong$', '\u00bd': r'$\frac{1}{2}$',
 '\u207a': r'$^+$', '\u207b': r'$^-$', '\u00b2': r'$^2$', '\u00b3': r'$^3$',
 '\u2070': r'$^0$', '\u2074': r'$^4$', '\u2075': r'$^5$', '\u2076': r'$^6$',
 '\u2077': r'$^7$', '\u2078': r'$^8$', '\u2079': r'$^9$',
 '\u2080': r'$_0$', '\u2081': r'$_1$', '\u2082': r'$_2$', '\u2083': r'$_3$',
 '\u2084': r'$_4$', '\u2085': r'$_5$', '\u2086': r'$_6$', '\u2087': r'$_7$',
 '\u2088': r'$_8$', '\u2089': r'$_9$',
 '\u00fc': r'{\"u}', '\u00f6': r'{\"o}', '\u00e4': r'{\"a}', '\u00a0': ' ', '\u00df': r'{\ss}',
 '\u00e9': r"{\'e}", '\u00e8': r"{\`e}", '\u00ea': r'{\^e}', '\u00e1': r"{\'a}",
 '\u00e0': r"{\`a}", '\u00e2': r'{\^a}', '\u00ed': r"{\'i}", '\u00ec': r"{\`i}",
 '\u00ee': r'{\^i}', '\u00f3': r"{\'o}", '\u00f2': r"{\`o}", '\u00f4': r'{\^o}',
 '\u00fa': r"{\'u}", '\u00f9': r"{\`u}", '\u00fb': r'{\^u}', '\u00f1': r'{\~n}',
 '\u00e7': r'{\c{c}}', '\u015f': r'{\c{s}}', '\u0163': r'{\c{t}}',
 '\u011f': r'{\u{g}}', '\u0131': r'{\i}', '\u0151': r'{\H{o}}', '\u0171': r'{\H{u}}',
 '\u00c5': r'{\AA}', '\u00e5': r'{\aa}', '\u00c4': r'{\"A}', '\u00d6': r'{\"O}',
 '\u00dc': r'{\"U}', '\u0142': r'{\l}', '\u0141': r'{\L}', '\u017c': r'{\.z}',
 '\u0105': r'{\k{a}}', '\u0119': r'{\k{e}}',
}

def tex_escape(s):
    out = []
    for ch in s:
        if ch in UMAP:
            out.append(UMAP[ch])
        elif ch == '\\': out.append(r'\textbackslash{}')
        elif ch == '%': out.append(r'\%')
        elif ch == '&': out.append(r'\&')
        elif ch == '#': out.append(r'\#')
        elif ch == '_': out.append(r'\_')
        elif ch == '{': out.append(r'\{')
        elif ch == '}': out.append(r'\}')
        elif ch == '$': out.append(r'\$')
        elif ch == '~': out.append(r'\textasciitilde{}')
        elif ch == '^': out.append(r'\textasciicircum{}')
        elif ch == '<': out.append(r'$<$')
        elif ch == '>': out.append(r'$>$')
        elif ord(ch) < 128: out.append(ch)
        else: raise SystemExit(f'UNMAPPED UNICODE CHAR {ch!r} (U+{ord(ch):04X}) in: ...{s[-70:]}')
    return ''.join(out)

def tex_body(s):
    t = tex_escape(s)
    t = re.sub(r'\*([^*\n][^*\n]*?)\*', r'\\emph{\1}', t)   # *italics* -> \emph{}
    t = re.sub(r'\b(IC50|EC50|TC50)\b', lambda m: m.group(1)[:-2] + r'$_{50}$', t)
    return t

# ---------------------------------------------------------------- build tex
def build_tex(cited_ids, id2src):
    L = []; A = L.append
    A(r'\documentclass[11pt]{article}')
    A(r'\usepackage{lmodern}')
    A(r'\usepackage[T1]{fontenc}')
    A(r'\usepackage{textcomp}')
    A(r'\usepackage[expansion=false]{microtype}')
    A(r'\usepackage{amsmath,amssymb}')
    A(r'\usepackage[version=4]{mhchem}')
    A(r'\usepackage{booktabs,longtable,array}')
    A(r'\usepackage{enumitem}')
    A(r'\usepackage{xcolor}')
    A(r'\usepackage{xurl}')
    A(r'\usepackage{hyperref}')
    A(r'\usepackage{geometry}')
    A(r'\geometry{margin=25mm}')
    A(r'\hypersetup{colorlinks=true,linkcolor=blue!50!black,urlcolor=blue!55!black,')
    A('  pdftitle={' + tex_escape(TITLE_PLAIN) + '},')
    A(f'  pdfauthor={{{AUTHOR}}},')
    A(r'  pdfkeywords={Crataegus, hawthorn, phytochemistry, procyanidins, cardiovascular, review},')
    A(r'  pdfsubject={Grounded literature review, October 2025 - October 2026}}')
    A(r'\newcommand{\src}[1]{[#1]}')
    A(r'\emergencystretch=3em')
    A(r'\setlength{\parindent}{0pt}')
    A(r'\setlength{\parskip}{0.55em}')
    A(r'\title{' + TITLE + '}')
    A(r'\author{' + AUTHOR + r'\thanks{Draft prepared with AI assistance (Hermes Agent); '
      r'see notice below.}}')
    A(r'\date{' + DATE + '}')
    A(r'\begin{document}')
    A(r'\maketitle')
    A(r'\begin{center}\fbox{\parbox{0.93\textwidth}{\small ' + tex_body(NOTICE) + r'}}\end{center}')
    A('')
    for heading, blocks in DOC:
        A(r'\section*{' + tex_body(heading) + '}')
        for kind, val in blocks:
            if kind == 'p':
                A(tex_body(val))
                A('')
            elif kind == 'ul':
                A(r'\begin{itemize}[leftmargin=1.4em,itemsep=0.15em]')
                for it in val: A(r'\item ' + tex_body(it))
                A(r'\end{itemize}')
            elif kind == 'table':
                A(r'\begin{center}\small')
                A(r'\textbf{Table 1. Hallmark \emph{Crataegus} compounds with 2025--26 findings.} '
                  r'Formulas and molecular weights were retrieved per compound from PubChem; the '
                  r"rightmost column cites the year's finding and the matching PubChem record.\\[0.4em]")
                A(r'\setlength{\tabcolsep}{3pt}')
                A(r'\begin{longtable}{@{}>{\raggedright\arraybackslash}p{2.55cm}'
                  r'>{\raggedright\arraybackslash}p{2.5cm}>{\raggedright\arraybackslash}p{2.0cm}'
                  r'>{\raggedright\arraybackslash}p{1.15cm}>{\raggedright\arraybackslash}p{6.85cm}@{}}')
                A(r'\toprule')
                A(r'Compound & Class & Formula & MW & 2025--26 highlight \\')
                A(r'\midrule')
                A(r'\endhead')
                for (name, cls, formula, mw, hl) in TABLE:
                    f_t = r'\ce{' + formula + '}' if formula else '---'
                    A(f'{tex_body(name)} & {tex_body(cls)} & {f_t} & {tex_body(mw) if mw else "---"} & {tex_body(hl)} \\\\')
                A(r'\bottomrule')
                A(r'\end{longtable}')
                A(r'\end{center}')
                A('')
    A(r'\section*{Sources}')
    A(r'\footnotesize Entries are numbered by retrieval identity, matching the inline [n] markers '
      r'inline. Every cited entry below carries a captured verbatim supporting quotation in the '
      r'project repository ledger (citations/ledger.json), alongside the fetched page text '
      r'(research/pages/). PubMed abstracts are the content of record; two retained items lacking '
      r'usable abstracts were not cited.')
    A(r'{\footnotesize')
    for sid in sorted(cited_ids):
        url, title = id2src[sid]
        A(r'\noindent\hangindent=2.6em\hangafter=1 '
          rf'[{sid}] {tex_escape(title)}. \url{{{url}}}\par')
    A(r'\vspace{0.3em}\noindent Retrieved October 25, 2026 via NCBI E-utilities, PubChem PUG REST, '
      r'and ClinicalTrials.gov API v2.}')
    A(r'\end{document}')
    return '\n'.join(L) + '\n'

# ---------------------------------------------------------------- build md
def build_md():
    L = []; A = L.append
    A(f'# {TITLE_PLAIN}')
    A(f'\n{AUTHOR} — {DATE}\n')
    A(f'**Notice.** {NOTICE}\n')
    for n, (heading, blocks) in enumerate(DOC, 1):
        A(f'\n## {n}. {heading}\n')
        for kind, val in blocks:
            if kind == 'p':
                A(val + '\n')
            elif kind == 'ul':
                for it in val: A(f'- {it}')
                A('')
            elif kind == 'table':
                A('| Compound | Class | Formula | MW | 2025-26 highlight |')
                A('|---|---|---|---|---|')
                for (name, cls, formula, mw, hl) in TABLE:
                    A(f'| {name} | {cls} | {formula or "---"} | {mw or "---"} | {hl} |')
                A('')
    return '\n'.join(L) + '\n'

# ---------------------------------------------------------------- main
def main():
    r = subprocess.run(['python3', S, '--ledger', LEDGER, 'list', '--json'],
                       capture_output=True, text=True,
                       env=dict(os.environ, HERMES_CITATION_LEDGER=LEDGER))
    ledger = json.loads(r.stdout)
    id2src = {e['id']: (e['url'], e.get('title', '')) for e in ledger}

    md = build_md()
    all_text = ' '.join(
        (val if kind == 'p' else ' '.join(val) if kind == 'ul'
         else ' '.join(' '.join(str(c) for c in row if c) for row in TABLE))
        for heading, blocks in DOC for kind, val in blocks)
    cited = sorted({int(n) for n in re.findall(r'\[(\d+)\]', all_text)})
    missing = [i for i in cited if i not in id2src]
    if missing:
        sys.exit(f'PROBLEM: cited ids not in ledger: {missing}')
    n_pubmed = len([i for i in cited if 'pubmed.ncbi.nlm.nih.gov' in id2src[i][0]])
    if n_pubmed != 52:
        sys.exit(f'PROBLEM: prose claims 52 retained PubMed reports, but {n_pubmed} are cited.')
    json.dump(cited, open(f'{PROJ}/research/cited_ids.json', 'w'))

    open(f'{PAPER}/draft.md', 'w').write(md)
    open(f'{PAPER}/hawthorn_review.tex', 'w').write(build_tex(cited, id2src))
    print(f'cited ids: {len(cited)} (PubMed {n_pubmed}, PubChem '
          f'{len([i for i in cited if "pubchem" in id2src[i][0]])}, other '
          f'{len(cited) - n_pubmed - len([i for i in cited if "pubchem" in id2src[i][0]])})')
    print('wrote draft.md and hawthorn_review.tex')

if __name__ == '__main__':
    main()