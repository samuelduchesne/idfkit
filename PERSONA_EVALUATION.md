# idfkit — Persona-Driven Application Evaluation

**Date**: 2026-02-07
**Subject**: idfkit v0.1.0 (beta) — Python toolkit for EnergyPlus IDF/epJSON manipulation and building energy simulation
**Evaluator**: Product Research & UX Strategy Analysis

---

## Step 1 — Persona Generation

### Persona 1: Mei-Lin Chen — Senior Energy Modeler (Power User / Domain Expert)

- **Role / Background**: 12 years of building energy modeling at a large MEP engineering firm. Runs 50–200 EnergyPlus models per year. Has used eppy since 2016 and has extensive custom scripts.
- **Primary goals**: Migrate existing eppy-based parametric workflows to something faster. Batch-process hundreds of IDF variants for LEED/ASHRAE compliance.
- **Technical proficiency**: Advanced Python. Comfortable with pip, virtual environments, pandas. Not a software engineer — scripts are messy but functional.
- **Key constraints**: Cannot break existing workflows during migration. Needs to justify the switch to her manager. Deals with IDF files from 10+ EnergyPlus versions.
- **Success criteria**: Parametric runs complete in hours instead of days. Existing scripts require minimal rewriting. Reference tracking eliminates manual string-matching hacks.
- **Likely frustrations**: API differences from eppy that break muscle memory. Beta status raises trust concerns for production use. Unclear what "breaking changes" are coming before 1.0.

### Persona 2: James Okafor — PhD Researcher in Building Science (Researcher / Champion)

- **Role / Background**: 3rd-year PhD student studying urban building energy modeling. Runs sensitivity analyses across thousands of building archetypes. Published two papers using eppy + Python.
- **Primary goals**: Programmatically generate and simulate thousands of building variants. Extract time-series data for statistical analysis. Reproduce results reliably.
- **Technical proficiency**: Strong Python, numpy, pandas. Uses Jupyter notebooks exclusively. Comfortable with APIs but not with packaging or deployment.
- **Key constraints**: Limited compute budget (university cluster). No IT support — installs everything himself. Needs reproducible environments. Papers depend on consistent results across versions.
- **Success criteria**: Can create 5,000+ building variants in a single script. Simulation caching eliminates redundant runs. SQL output integrates cleanly with pandas.
- **Likely frustrations**: Beta version pinning in a paper's requirements.txt. Any schema change between idfkit versions would break reproducibility. Unclear caching invalidation semantics.

### Persona 3: Sarah Dalton — Junior Mechanical Engineer (Casual User / Non-Expert in Python)

- **Role / Background**: 2 years out of college. Uses EnergyPlus via OpenStudio/DesignBuilder GUIs. Her manager asked her to "automate some stuff with Python."
- **Primary goals**: Read an IDF file, change a few values (thermostat setpoints, insulation thicknesses), run a simulation, get the result.
- **Technical proficiency**: Completed one Python course in college. Can copy-paste code but struggles with debugging tracebacks. Has never used pip from the command line.
- **Key constraints**: Very limited time (this is a side task). No Python environment set up. Needs hand-holding through installation and first script. Intimidated by terminal.
- **Success criteria**: A working 15-line script that modifies one parameter and returns annual energy use within her first afternoon.
- **Likely frustrations**: Installation friction (uv vs pip, extras, EnergyPlus path). Error messages assume familiarity with EnergyPlus object types. No GUI or interactive mode. Documentation assumes too much prior knowledge.

### Persona 4: David Park — Software Architect at a PropTech Startup (Decision-Maker / Skeptic)

- **Role / Background**: Leads the engineering team at a startup building a SaaS platform for building energy audits. Evaluating idfkit as a core dependency.
- **Primary goals**: Determine if idfkit is stable enough to build a commercial product on. Assess API design quality, error handling, and maintainability. Estimate integration cost.
- **Technical proficiency**: Expert software engineer. Evaluates libraries on API consistency, test coverage, documentation, release cadence, and bus factor.
- **Key constraints**: Cannot depend on a library with one maintainer and no SLA. Needs predictable release schedule. Must assess licensing (MIT is fine). Needs to trust that breaking changes will be communicated.
- **Success criteria**: API is well-designed and stable. Error handling is explicit, not exception-heavy. Library can be embedded in async web services. Performance claims are backed by benchmarks.
- **Likely frustrations**: Single maintainer (bus factor = 1). v0.1.0 beta signals instability. No CHANGELOG or migration guide between versions. Unclear deprecation policy. Global state in schema management.

### Persona 5: Amara Obi — HVAC Controls Engineer (Domain Expert / First-Time idfkit User)

- **Role / Background**: 8 years designing HVAC systems. Uses EnergyPlus to validate control sequences. Knows IDF syntax intimately but writes Python only occasionally.
- **Primary goals**: Quickly swap HVAC system types in a model and compare energy results. Inspect schedule definitions to verify occupancy assumptions.
- **Technical proficiency**: Intermediate Python. Knows IDF field names by heart. Expects the library to use EnergyPlus terminology, not abstracted names.
- **Key constraints**: Time-pressured (deadlines for submittals). Needs to trust that field mappings are correct — a wrong field assignment could silently produce bad results. Works with very large models (2,000+ objects).
- **Success criteria**: Can navigate a 2,000-object model as fast as a text editor. Schedule evaluation matches EnergyPlus runtime behavior exactly. Thermal property calculations agree with manual checks.
- **Likely frustrations**: Python attribute name conversion (e.g., `x_origin` vs "X Origin") may cause confusion about which IDF field is actually being set. Silent coercion of field values. Large models taking too long to validate.

### Persona 6: Raj Patel — Sustainability Consultant (Non-Technical / Needs Results, Not Code)

- **Role / Background**: LEED AP with 15 years in green building consulting. Manages energy modeling projects but doesn't model himself. Oversees a team of modelers.
- **Primary goals**: Understand what idfkit can do for his team. Evaluate whether it's worth training staff on. Wants to see a demo, not read API docs.
- **Technical proficiency**: Cannot write Python. Uses Excel and PowerPoint. Understands building science concepts but not programming.
- **Key constraints**: Zero tolerance for command-line tools. Needs visual outputs (charts, reports). Decisions driven by ROI and team productivity, not technical elegance.
- **Success criteria**: A compelling 5-minute demo showing time savings. Clear documentation his team can follow. Visible community or vendor support.
- **Likely frustrations**: No GUI, no web interface. Documentation is developer-oriented. Cannot evaluate the library himself — entirely dependent on his technical staff's assessment. No case studies or testimonials.

### Persona 7: Tomoko Ishida — Building Energy Code Official (Regulator / Edge Case User)

- **Role / Background**: Reviews energy compliance submissions for a state energy office. Occasionally needs to open IDF files submitted by applicants and verify parameters.
- **Primary goals**: Spot-check specific values in submitted IDF files (envelope U-values, lighting power densities, HVAC efficiencies). Validate that models meet code requirements.
- **Technical proficiency**: Basic Python (took a data analysis course). Can run scripts but cannot debug them. Uses Windows.
- **Key constraints**: Government IT policies restrict software installation. Cannot install EnergyPlus on her machine. Needs read-only access to IDF files — never runs simulations. Works with models from many different EnergyPlus versions.
- **Success criteria**: Load any IDF file regardless of version, extract thermal properties, compare against code thresholds. No EnergyPlus installation required for file reading.
- **Likely frustrations**: Unclear whether idfkit requires EnergyPlus for basic file reading (it doesn't, but this isn't obvious). Windows installation friction. Multi-version support gaps. No pre-built compliance checking features.

### Persona 8: Lukas Brenner — Open-Source Contributor / Tool Builder (Implementer / Champion)

- **Role / Background**: Research software engineer at a national lab. Builds open-source tools for the building science community. Maintains two related Python packages.
- **Primary goals**: Integrate idfkit as a dependency in his own tools. Extend it with custom object types or validation rules. Contribute back upstream.
- **Technical proficiency**: Expert Python developer. Reads source code before reading docs. Evaluates codebases on architecture, test quality, and extensibility.
- **Key constraints**: Needs clean extension points (not monkey-patching). License must be compatible (MIT is good). Needs responsive maintainer for PRs.
- **Success criteria**: Can subclass or compose idfkit classes without fighting the framework. Plugin architecture for custom validators. CI/CD is reliable and fast.
- **Likely frustrations**: Tightly coupled internal modules. No plugin/extension API. Bundled schemas add package bloat. Global schema manager state makes testing hard. Slots on IDFObject limit subclassing.

---

## Step 2 — Persona-Driven Evaluation

### Evaluation: Mei-Lin Chen (Senior Energy Modeler / Power User)

**What she tries first**: Installs idfkit, loads her largest IDF file (~2,000 objects, EnergyPlus v9.6), and times `load_idf()` versus her current eppy script.

**Where the app helps**: The speed difference is immediately obvious — loading is near-instant vs. several seconds with eppy. O(1) lookups by name are transformative for her parametric scripts. `get_referencing()` eliminates 200+ lines of manual string-matching in her codebase. The eppy compatibility layer lets her migrate incrementally.

**Where friction occurs**:
- The eppy compatibility layer covers common operations but not her custom field access patterns. She hits edge cases where `idf.idfobjects["ZONE"][0].Name` works but other eppy idioms silently return wrong results.
- She doesn't immediately find the migration guide — it's buried in the docs under "Examples."
- Her scripts use EnergyPlus v9.6, and she's unsure whether idfkit's schema for 9.6 matches the official one exactly. No explicit schema versioning or checksum to verify.

**What she misunderstands**: She assumes `validate=True` on `add()` catches all problems. In reality, validation is schema-level — it doesn't catch semantic issues like incompatible HVAC configurations.

**Deal-breaker or recommendation**: She'd recommend it strongly to peers *if* she can verify the eppy compatibility layer handles her top 20 scripts. If more than 2–3 scripts require significant rewriting, she'll defer migration until v1.0. The beta label is a real barrier — she won't deploy to her firm's production pipeline until it's stable.

---

### Evaluation: James Okafor (PhD Researcher)

**What he tries first**: Opens the core tutorial notebook in JupyterLab. Follows along, then adapts the parametric study notebook to his urban archetype workflow.

**Where the app helps**: The Jupyter notebooks are excellent onboarding. SQL output integration with pandas is exactly what he needs. Simulation caching is a game-changer — re-running notebooks doesn't re-simulate unchanged models. The weather station index with 55,000 stations saves him weeks of manual EPW file management.

**Where friction occurs**:
- Caching semantics are unclear. He modifies a schedule in his model, but the cache key doesn't change because it's based on file content hashing and he's not sure if in-memory modifications are captured. He gets stale results and spends hours debugging.
- `simulate_batch()` doesn't expose progress callbacks or integrate with tqdm/rich for progress bars. On a 2,000-model run, he has no visibility into progress.
- He wants to pin idfkit in his paper's `requirements.txt`, but v0.1.0 with no stability guarantees makes reviewers nervous.

**What he misunderstands**: He assumes `simulate()` is thread-safe and tries to parallelize with `concurrent.futures`. The global schema manager and subprocess management may have subtle concurrency issues that aren't documented.

**Deal-breaker or recommendation**: He becomes a strong champion and even considers contributing. The caching confusion nearly made him distrust all results, though. Clear documentation on cache key computation and invalidation would prevent this. He'd cite idfkit in his next paper.

---

### Evaluation: Sarah Dalton (Junior Engineer / Casual User)

**What she tries first**: Googles "idfkit tutorial," lands on the getting started page. Tries `pip install idfkit`.

**Where the app helps**: The quick start guide shows a working example in ~10 lines. If she gets past installation, the attribute access API (`zone.x_origin = 10`) is intuitive. The `describe()` function helps her discover field names without leaving Python.

**Where friction occurs**:
- Installation is the first wall. She doesn't have Python properly set up. The docs recommend `uv`, which she's never heard of. She tries `pip install idfkit` and it works, but then `from idfkit import simulate` fails because she doesn't have the simulation extras installed. The error message doesn't tell her to install `idfkit[all]`.
- She can load her IDF file, but she doesn't know the EnergyPlus object type names to query. She types `doc["thermostat"]` instead of `doc["ThermostatSetpoint:DualSetpoint"]`. The error message lists all available types, which is overwhelming (500+ types).
- When the simulation fails, the traceback is long and references internal idfkit modules. She doesn't know which line is her mistake vs. library internals.

**What she misunderstands**: She thinks `doc.zones` returns a Python list and tries `doc.zones.append(new_zone)`. The IDFCollection API doesn't support this — she needs `doc.add()`.

**Deal-breaker or recommendation**: She abandons the project after 3 hours if she can't get a simulation running. She goes back to manually editing IDF files in a text editor. A "copy-paste-and-run" recipe page with the 5 most common tasks (change a setpoint, run a simulation, get annual energy) would save her. The library fundamentally isn't designed for her, but a thin wrapper or cookbook could make it accessible.

---

### Evaluation: David Park (Software Architect / Skeptic)

**What he tries first**: Reads the README benchmarks, then opens `pyproject.toml` to assess dependencies. Reads the source code architecture. Runs the test suite.

**Where the app helps**: The API design is genuinely good — clean separation between I/O, object model, simulation, and weather. The slot-based IDFObject is a smart performance choice. MIT license is perfect. Test coverage across 48 modules is reassuring. The schema-driven design means it can support new EnergyPlus versions with minimal code changes.

**Where friction occurs**:
- **Bus factor = 1**. One maintainer, one contributor. For a commercial dependency, this is a non-starter without a support contract.
- **Global state**: `get_schema_manager()` returns a module-level singleton. This complicates testing, multi-tenant usage, and serverless deployments.
- **Process spawning**: `simulate()` spawns subprocesses directly. In a web service, this needs to be wrapped in a job queue, and idfkit provides no hooks for this. The synchronous API doesn't play well with async frameworks (FastAPI, etc.).
- **No semantic versioning commitment**. v0.1.0 with no CHANGELOG means any update could break his product.
- **Bundled schemas** add ~50MB+ to the package. In a Docker container, this bloat matters.

**What he misunderstands**: Nothing. He reads it correctly.

**Deal-breaker or recommendation**: He forks it. He can't depend on a single-maintainer beta library for a commercial product. He'll use the core parsing/object model (which is excellent) but wrap simulation and weather in his own service layer. He'd *pay* for a supported version. If the maintainer offered a commercial support tier, he'd be the first customer.

---

### Evaluation: Amara Obi (HVAC Controls Engineer)

**What she tries first**: Loads a large model and navigates to `doc["AirLoopHVAC"]` to inspect system configurations.

**Where the app helps**: O(1) collection access is immediately useful — she's used to text-editor Ctrl+F. `get_referencing()` answers "what uses this chiller?" instantly, which previously took 10 minutes of manual tracing. Schedule evaluation with `evaluate()` lets her verify occupancy assumptions at specific timestamps.

**Where friction occurs**:
- **Field name mapping**: She knows the IDF field "Cooling Design Air Flow Rate" but has to guess the Python attribute name (`cooling_design_air_flow_rate`). The conversion is systematic but she doesn't trust it for fields with unusual names, abbreviations, or special characters.
- **No tab completion in her workflow**: She uses VS Code with a Python script, not Jupyter. Tab completion only works in IPython/Jupyter.
- **Schedule evaluation edge cases**: She's testing a schedule with holiday overrides and RunPeriod interactions. She's not sure if `evaluate()` handles `Schedule:Year` with `ScheduleTypeLimits` clamping correctly. The docs don't specify edge case behavior.

**What she misunderstands**: She assumes `calculate_u_value()` accounts for air films and thermal bridging corrections per ASHRAE methodology. It computes center-of-cavity U-value only — which is correct for EnergyPlus inputs, but not what she expects for code compliance reporting.

**Deal-breaker or recommendation**: She becomes a regular user for model inspection and schedule verification. She won't use it for simulation orchestration (she prefers manual EnergyPlus runs). Her biggest request would be a `print(obj)` that shows the original IDF field names alongside the Python attribute names, so she can verify mappings at a glance.

---

### Evaluation: Raj Patel (Sustainability Consultant / Non-Technical)

**What he tries first**: Asks his junior modeler (Sarah) to evaluate it. Opens the README himself and reads the first paragraph.

**Where the app helps**: The README badges (MIT, Python 3.10+, tested) look professional. The benchmarks chart (750x faster) is a compelling visual he can show in a slide deck. The weather station feature could save his team hours per project.

**Where friction occurs**:
- He cannot evaluate the library himself. There is no web demo, no screencast, no "try it in your browser" link.
- No ROI calculator or case study. He can't make a business case without concrete time-savings numbers from a firm like his.
- The documentation is entirely developer-oriented. There's no "for managers" page explaining business value.

**What he misunderstands**: He assumes idfkit is a complete replacement for OpenStudio or DesignBuilder. He doesn't understand that it's a library, not an application.

**Deal-breaker or recommendation**: He won't champion adoption unless Sarah (Persona 3) succeeds in her evaluation. If she fails, the library is invisible to his firm. A 3-minute screencast showing a before/after workflow comparison would be the single most impactful marketing asset for this persona.

---

### Evaluation: Tomoko Ishida (Building Energy Code Official)

**What she tries first**: `pip install idfkit` on her government-issued Windows laptop. Loads a submitted IDF file to extract envelope U-values.

**Where the app helps**: `load_idf()` works without EnergyPlus installed — this is critical for her use case. Multi-version support (8.9–25.2) covers all submissions she receives. `calculate_u_value()` directly answers her primary question. `validate_document()` could catch common submission errors.

**Where friction occurs**:
- **Installation on Windows**: Government IT may block pip. No pre-built wheel or standalone executable. She has to go through an IT request process.
- **It's not obvious that EnergyPlus isn't required for reading**: The README opens with "building energy simulation" — she assumes she needs EnergyPlus and almost gives up before trying.
- **Thermal properties API is limited**: She wants assembly U-values including air films per ASHRAE/IECC methodology, not just center-of-cavity values from EnergyPlus material definitions.
- **No compliance checking features**: She needs to compare extracted values against code thresholds. idfkit gives her the values but she must build the comparison logic herself.

**What she misunderstands**: She thinks `validate_document()` checks for code compliance. It checks for EnergyPlus schema validity — an entirely different thing.

**Deal-breaker or recommendation**: idfkit partially solves her problem. She can extract values and build a spreadsheet comparison. But without compliance-specific features or a pre-built executable, the barrier to entry is too high. She'd use a purpose-built compliance checking tool instead — if one existed.

---

### Evaluation: Lukas Brenner (Open-Source Contributor / Tool Builder)

**What he tries first**: `git clone`, reads `pyproject.toml`, runs `make check && make test`. Reads the source code architecture.

**Where the app helps**: Code quality is high. Type hints everywhere. Clean module boundaries. Ruff + pyright + pytest is a modern, solid toolchain. The schema-driven architecture is elegant — adding a new EnergyPlus version is just dropping in a new JSON schema. MIT license is perfect for his use case.

**Where friction occurs**:
- **`__slots__` on IDFObject**: He can't add custom attributes to objects without subclassing, and subclassing slot-based classes is painful. He wants to attach metadata (e.g., `obj._source_file`, `obj._modified_by`) to objects in his tool.
- **No plugin/extension architecture**: Validation is a closed system. He can't register custom validators without forking. He wants to add project-specific rules (e.g., "all zones must have daylight sensors").
- **Global schema manager**: He's building a tool that processes models from multiple EnergyPlus versions simultaneously. The global state requires careful management.
- **No event system**: He wants to hook into object addition/removal/modification events to build a change-tracking layer. No observer pattern or callback mechanism exists.

**What he misunderstands**: He assumes the reference graph is a general-purpose dependency graph he can query with complex predicates. It's simpler than that — it tracks name-based references only, not semantic relationships.

**Deal-breaker or recommendation**: He integrates idfkit as a dependency despite the friction. The core parsing and object model are too good to rewrite. He works around the extension limitations with composition patterns. He opens 3 GitHub issues requesting: (1) plugin validators, (2) instance-level schema managers, (3) event hooks. If these are ignored, he'll eventually maintain a fork, which is a loss for the ecosystem.

---

## Step 3 — Cross-Persona Synthesis

### 1. Recurring Strengths Across Personas

| Strength | Personas who benefit |
|----------|---------------------|
| **O(1) object lookup by name** | Mei-Lin, Amara, James, Tomoko — anyone navigating large models |
| **Reference tracking (`get_referencing()`)** | Mei-Lin, Amara — eliminates the #1 pain point with eppy/manual workflows |
| **Schema-driven multi-version support** | Tomoko, Mei-Lin, James — covers real-world version diversity |
| **Clean, Pythonic API** | James, Lukas, David — well-designed attribute access, good separation of concerns |
| **Simulation caching** | James — eliminates redundant compute in iterative workflows |
| **Weather station index** | James, Mei-Lin — massive time-saver for weather file management |
| **No EnergyPlus required for file I/O** | Tomoko — critical for non-simulation use cases |
| **Comprehensive documentation** | James, Mei-Lin — tutorials + API reference + migration guide |
| **High code quality** | David, Lukas — inspectable, tested, typed, well-structured |

### 2. Recurring Failure Modes or Risks

| Failure Mode | Affected Personas | Severity |
|-------------|-------------------|----------|
| **Beta status / no stability guarantees** | David, Mei-Lin, James | HIGH — blocks production adoption and academic citation |
| **Bus factor = 1** | David, Lukas | HIGH — existential risk for anyone depending on it |
| **Installation friction for non-developers** | Sarah, Tomoko, Raj | MEDIUM — excludes an entire user tier |
| **Unclear caching semantics** | James | MEDIUM — can produce silently wrong results |
| **No extension/plugin architecture** | Lukas | MEDIUM — forces forking instead of composing |
| **Global state (schema manager)** | David, Lukas | MEDIUM — complicates testing, multi-tenant, and concurrent use |
| **Field name mapping opacity** | Amara, Sarah | LOW-MEDIUM — erodes trust in correctness |
| **No async/non-blocking simulation API** | David | LOW-MEDIUM — blocks modern web service integration |

### 3. Persona-Specific Deal-Breakers

| Persona | Deal-Breaker | Root Cause |
|---------|-------------|------------|
| **Sarah (Junior Engineer)** | Cannot get a working script in one afternoon | Installation complexity + object type discovery friction + unhelpful error messages |
| **David (Architect)** | Cannot bet a commercial product on a single-maintainer beta | No support contract, no stability commitment, no governance model |
| **Raj (Consultant)** | Cannot evaluate or champion without a demo | No visual demo, screencast, or non-developer-oriented materials |
| **Tomoko (Code Official)** | IT blocks installation; thermal properties don't match compliance methodology | No standalone distribution; U-value calculation doesn't include code-required adjustments |

### 4. Misalignment Between Intended and Perceived Value

| Intended Value | Perceived Value | Gap |
|---------------|----------------|-----|
| "Drop-in replacement for eppy" | Users expect 100% API compatibility | The compatibility layer covers common patterns but breaks on edge cases. "Drop-in" overpromises. |
| "Fast, modern toolkit" | Non-developers perceive it as "another command-line tool I can't use" | The speed story is compelling to developers but invisible to decision-makers and casual users. |
| "Building energy simulation toolkit" | Tomoko assumes EnergyPlus is required; Raj assumes it's a full application | The README leads with simulation, but file I/O and analysis are independently valuable and should be promoted separately. |
| "Comprehensive documentation" | Sarah finds it overwhelming; Raj finds it developer-only | Documentation is comprehensive for developers but has no on-ramp for non-developers or decision-makers. |

### 5. Highest-Leverage Improvements Benefiting Multiple Personas

| Improvement | Benefits | Effort |
|------------|----------|--------|
| **1. Publish a 1.0 roadmap with stability guarantees and semver commitment** | David, Mei-Lin, James, Lukas — unblocks production/academic adoption | Low |
| **2. Add a "Common Tasks" cookbook with 5 copy-paste recipes** | Sarah, Amara, Tomoko — immediate on-ramp for non-expert users | Low |
| **3. Create a 3-minute screencast demo** | Raj, Sarah, Tomoko — enables non-developer evaluation and championing | Low |
| **4. Document caching semantics explicitly (cache key computation, invalidation rules)** | James — prevents trust-destroying bugs | Low |
| **5. Add plugin/extension points for validators and event hooks** | Lukas — prevents ecosystem fragmentation through forking | Medium |
| **6. Replace global schema manager with instance-based design** | David, Lukas — enables multi-tenant and concurrent usage | Medium |
| **7. Expose original IDF field names alongside Python attributes in repr/print** | Amara, Sarah — builds trust in field mapping correctness | Low |
| **8. Offer pre-built wheels and consider a PyInstaller-based standalone for Windows** | Tomoko, Sarah — removes installation barrier for constrained environments | High |

---

## Step 4 — Executive Summary

### Who idfkit clearly works for today

**Experienced Python developers who work with EnergyPlus models regularly.** This includes senior energy modelers migrating from eppy (Mei-Lin), researchers running parametric studies (James), and tool builders integrating EnergyPlus I/O into larger systems (Lukas). For these users, idfkit delivers genuine, measurable improvements: 750x faster lookups, automatic reference tracking, multi-version support, simulation caching, and a clean Pythonic API. The code quality is high, the documentation is thorough, and the architecture is sound.

### Who it does not work for (yet)

Three groups are currently excluded:

1. **Non-developers** (Raj, Tomoko): No visual interface, no standalone distribution, no demo materials. These users cannot evaluate or use the library regardless of its quality.
2. **Casual/junior developers** (Sarah): Installation and object-type discovery friction creates a 3-hour wall that most beginners won't push through. The library assumes EnergyPlus domain knowledge that casual users lack.
3. **Commercial adopters** (David): Single-maintainer beta status with no stability commitments, support contracts, or governance model makes idfkit too risky for production SaaS products despite excellent technical quality.

### What must be fixed immediately vs. later

**Immediately (before promoting broader adoption):**

- **Publish a 1.0 roadmap and semver stability commitment.** This is the single highest-ROI action. It costs nothing but a markdown file and unblocks production adoption, academic citation, and ecosystem integration. Without it, the library's best potential users (Mei-Lin, James, David, Lukas) all hesitate.
- **Document caching semantics.** Undocumented cache key computation can produce silently wrong simulation results. This is a correctness issue, not a convenience issue.
- **Add a "5 Common Tasks" cookbook page.** Five copy-paste-and-run recipes covering the five most common operations. This one page would cut the abandonment rate for junior users dramatically.

**Later (important but non-blocking):**

- Extension/plugin architecture for validators and events
- Instance-based schema management (replacing global state)
- Async simulation API for web service integration
- Standalone Windows distribution for constrained IT environments
- Compliance-specific thermal property calculations (ASHRAE/IECC methodology)

### One bold recommendation

**Stop marketing idfkit as a "simulation toolkit" and start marketing it as a "building model intelligence layer."**

The simulation features are genuinely useful, but they require EnergyPlus installation and are inherently limited to users who already run simulations. The library's most differentiated capabilities — O(1) model navigation, automatic reference tracking, multi-version schema support, thermal property extraction, schedule evaluation, and validation — require *no EnergyPlus installation at all*. These features serve a much larger audience: code officials reviewing submissions, consultants inspecting models, researchers analyzing building stocks, and developers building web-based model viewers.

The current README opens with simulation. The name "idfkit" emphasizes file format manipulation. Both undersell the library's actual value proposition. The reference graph, schedule evaluator, thermal calculator, and validation engine are analytical tools, not just I/O utilities. Repositioning around model intelligence — with simulation as one capability among many — would expand the addressable market from "Python developers who run EnergyPlus" to "anyone who works with building energy models," a 10x larger audience.

This repositioning also addresses the library's biggest structural weakness: dependence on EnergyPlus installation. By foregrounding EnergyPlus-independent features, idfkit becomes useful to Tomoko (code official), Raj's team (consultants), and Sarah (junior engineer) without requiring them to install and configure EnergyPlus first. The simulation features become an advanced capability for power users, not a prerequisite for entry.

---

*End of evaluation.*
