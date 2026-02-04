# Evaluation: IDFkit as a VS Code Backend for IDF Model Development

## Executive Summary

IDFkit has the architectural foundation to power a VS Code extension that
provides live validation, auto-completion, hover documentation, and reference
navigation for EnergyPlus IDF and epJSON files. Its schema-driven design,
O(1) lookup indexes, and on-demand validation system map directly onto Language
Server Protocol (LSP) capabilities. This document evaluates each feature area,
identifies what IDFkit already provides, and describes what would need to be
built.

---

## 1. The Core Problem: Determining Required Attributes

EnergyPlus models contain up to **847 distinct object types** organized across
**59 groups**, with a total of **12,652 fields**. A user editing an IDF file by
hand faces several challenges:

- **Which fields exist?** A `BuildingSurface:Detailed` object has 14+ fixed
  fields plus extensible vertex groups. A `Material` object has 8 fields, 5 of
  which are required. Without the IDD reference open in a separate window,
  users must guess or memorize field names.
- **Which fields are required?** The schema marks required fields per object
  type (e.g., `roughness`, `thickness`, `conductivity`, `density`,
  `specific_heat` for `Material`), but IDF files give no visual indication of
  which fields can be omitted.
- **What values are valid?** Fields carry type constraints (`number`,
  `string`, `integer`), enumerations (e.g., `Rough`, `Smooth`,
  `MediumRough` for roughness), numeric ranges (`exclusiveMinimum: 0.0`,
  `maximum: 0.99999`), units (`W/m-K`, `m`, `kg/m3`), and special sentinel
  values like `Autocalculate` or `Autosize`.
- **What do fields reference?** Reference fields like `zone_name` or
  `construction_name` must point to names defined by other objects in the
  model. A typo produces a simulation error that can be hard to trace.

IDFkit already stores all of this information in its `EpJSONSchema` class and
can answer every one of these questions programmatically.

---

## 2. IDFkit Capabilities Mapped to VS Code Features

### 2.1 Auto-Completion

| What users need | IDFkit API that provides it |
|---|---|
| Complete object type names while typing | `schema.object_types` — returns all 847 type names |
| Complete field names within an object | `schema.get_field_names(obj_type)` — ordered field list |
| Complete enum values for a field | `schema.get_field_schema(obj_type, field)["enum"]` |
| Complete reference targets (e.g., zone names) | `schema.get_field_object_list()` to find the list name, `schema.get_types_providing_reference()` to find source types, then enumerate matching names from the document |
| Show default values in completion items | `schema.get_field_default(obj_type, field)` |
| Show units alongside completions | Field schema `"units"` key (covers 4,692 of 12,652 fields) |
| Suggest `Autocalculate`/`Autosize` where valid | `"anyOf"` entries in field schema |

**Coverage assessment:** IDFkit exposes all metadata needed for full
auto-completion. The schema contains descriptions (`note`) for 6,055 fields
that can populate completion item documentation. The `legacy_idd.fields` array
preserves canonical field ordering for positional IDF completion.

**Gap:** IDFkit does not currently expose a dedicated "list all valid names for
an object_list reference" convenience method. This would require iterating the
document's collections filtered by `schema.get_types_providing_reference()`.
This is straightforward to add.

### 2.2 Live Validation (Diagnostics)

| Validation check | IDFkit implementation | LSP Diagnostic |
|---|---|---|
| Required fields missing | `validate_document(check_required=True)` → code `E001` | Error severity |
| Type mismatch | `validate_document(check_types=True)` → code `E003` | Error severity |
| Enum value not allowed | code `E004` | Error severity |
| Value below minimum | code `E005` / `E006` | Error severity |
| Value above maximum | code `E007` / `E008` | Error severity |
| Dangling reference | code `E009` | Error severity |
| anyOf type mismatch | code `E002` | Error severity |
| Unknown object type | code `W002` | Warning severity |
| Unknown field name | code `W003` | Warning severity |
| No schema available | code `W001` | Warning severity |

**Coverage assessment:** IDFkit's validation system already produces structured
`ValidationError` objects with severity levels, object/field locations, and
machine-readable codes. These map one-to-one onto LSP `Diagnostic` objects.
The `validate_document` function supports selective validation via
`object_types` parameter, enabling incremental validation of only the objects
that changed.

**Gap:** Validation currently operates on in-memory `IDFDocument` objects. A
VS Code integration would need an incremental parsing layer that re-parses only
the modified text region and updates the document model. The current IDF parser
uses a single-pass regex over the full file content. For files under 10 MB (the
vast majority of IDF models), re-parsing the full file on each keystroke
debounce (~40 ms for a 1,700-object model) is fast enough. For larger models,
an incremental parser would be beneficial.

**Gap:** Line/column position mapping. IDFkit's parser does not currently track
source positions (line number, column) for parsed objects and fields. The LSP
requires diagnostics to carry exact text ranges. The IDF parser would need to
record byte offsets or line:column pairs during tokenization so that validation
errors can be mapped back to editor positions.

### 2.3 Hover Information

| Hover target | Information IDFkit can provide |
|---|---|
| Object type keyword | `schema.get_object_memo(obj_type)` — description, plus `schema.get_required_fields(obj_type)` to show required fields |
| Field name | `schema.get_field_schema(obj_type, field)["note"]` — description (available for 6,055 of 12,652 fields), plus type, units, default, constraints |
| Field value (reference) | Resolve reference target: show the referenced object's type, name, and summary fields |
| Enum value | Show the full enum list with current value highlighted |
| Numeric value | Show units and valid range |

**Coverage assessment:** The schema metadata is rich enough for informative
hover tooltips. The `note` field provides EnergyPlus documentation inline. The
`units` field allows display like `Thickness: 0.1 m` rather than just `0.1`.

**Gap:** Same source-position tracking gap as validation — the hover handler
needs to know which object type and field the cursor is on.

### 2.4 Go to Definition / Find References

| Navigation action | IDFkit support |
|---|---|
| Go to definition of a referenced object | `doc.getobject(obj_type, name)` — O(1) lookup. Requires source position of the target object. |
| Find all references to an object | `doc.references.get_referencing(name)` — O(1) lookup. Returns all objects that reference a given name. |
| Find all references from an object | `doc.references.get_references(obj)` — O(1) lookup. Returns all names an object references. |
| Peek references inline | Same as above, rendered as peek results |

**Coverage assessment:** IDFkit's `ReferenceGraph` provides exactly the
dependency tracking needed for reference navigation. The graph is built
automatically during parsing with no additional cost.

**Gap:** Source position tracking is again the missing piece. Each `IDFObject`
would need to store its source location (byte offset or line range) so that
the extension can navigate to the correct position in the file.

### 2.5 Document Symbols / Outline

| Symbol type | IDFkit source |
|---|---|
| Object types as sections | `doc.collections.keys()` |
| Individual objects as children | `collection._items` with `.name` and `.obj_type` |
| Field names within objects | `obj.field_order` or `obj.data.keys()` |

**Coverage assessment:** The hierarchical structure of IDFDocument → collections
→ objects → fields maps naturally to LSP `DocumentSymbol` trees. Groups are
available from the schema (`"group"` key on each object type definition in 59
categories).

### 2.6 Code Actions and Quick Fixes

IDFkit's validation errors carry enough information to power quick fixes:

| Validation error | Possible quick fix |
|---|---|
| `E001` Required field missing | Insert field with default value (available via `get_field_default`) |
| `E004` Invalid enum value | Offer all valid enum values as replacements |
| `E009` Dangling reference | Offer existing object names from the referenced object-list as replacements |
| `W003` Unknown field | Offer closest matching field name (fuzzy match against `get_field_names`) |

### 2.7 Snippet Generation

IDFkit can generate complete object templates:

```python
schema = get_schema((24, 1, 0))
fields = schema.get_all_field_names("Material")
required = schema.get_required_fields("Material")
# Generate: Material, ${1:Name}, ${2:Roughness}, ${3:Thickness}, ...
```

For each field, the snippet can include:
- Placeholder with default value or required marker
- Tab stop ordering matching canonical field order
- Enum choices as dropdown selections (VS Code snippet choice syntax)

### 2.8 Format Conversion

IDFkit's bidirectional IDF ↔ epJSON conversion (`convert_idf_to_epjson`,
`convert_epjson_to_idf`) can power VS Code commands:

- "Convert to epJSON" / "Convert to IDF" via command palette
- Side-by-side preview of alternate format
- Automatic format detection and appropriate parser selection

---

## 3. Architecture Options

### 3.1 Option A: Python Language Server (pygls)

Build a Language Server in Python using `pygls` (Python Language Server
framework) with IDFkit as the core library.

```
VS Code Extension (TypeScript)
  ↕ LSP (JSON-RPC over stdio/tcp)
Python Language Server (pygls)
  ↕ API calls
IDFkit (parsing, schema, validation)
```

**Advantages:**
- Direct use of IDFkit's Python API with no serialization boundary
- Full access to all schema metadata, validation, and reference graph
- `pygls` handles LSP protocol boilerplate
- Python ecosystem for future ML-based suggestions

**Disadvantages:**
- Requires Python runtime on user's machine (can bundle with extension)
- Higher memory footprint than native TypeScript
- Startup latency for Python interpreter

**Effort estimate:** The VS Code extension TypeScript shell is minimal
(activation, language client configuration). The bulk of work is in the
Python language server:
1. IDF text document parsing with source positions
2. LSP handler implementations (completion, diagnostics, hover, etc.)
3. Incremental document update handling
4. File watcher for multi-file models

### 3.2 Option B: TypeScript Extension with IDFkit as Subprocess

Run IDFkit as a subprocess, communicating via JSON:

```
VS Code Extension (TypeScript)
  ↕ JSON over stdin/stdout
IDFkit CLI (Python subprocess)
```

**Advantages:**
- Decoupled architecture; extension and IDFkit evolve independently
- Can cache schema data in TypeScript for faster completions

**Disadvantages:**
- Serialization overhead for every interaction
- Must define and maintain a JSON protocol
- Harder to provide responsive real-time features

### 3.3 Option C: Compile Schema to JSON Schema for Native VS Code

Since epJSON files are JSON, VS Code's built-in JSON language support can
validate them using JSON Schema. IDFkit's schema files *are* JSON Schema
(with EnergyPlus extensions).

```
VS Code Settings (jsonValidation)
  → Energy+.schema.epJSON → Built-in JSON validation
```

**Advantages:**
- Zero additional code for basic epJSON validation
- Built-in completion for field names and enum values in epJSON files
- No Python dependency

**Disadvantages:**
- Only works for epJSON, not IDF text format
- No reference resolution or cross-object validation
- No hover documentation from `note` fields
- No Go to Definition
- Limited to JSON Schema capabilities (no extensible field validation)

### 3.4 Recommendation

**Option A (Python Language Server)** is the strongest approach. It provides
the richest feature set with the least duplication. IDFkit's existing API
already covers 80%+ of the data access patterns needed; the main work is in
the LSP integration layer and source-position tracking.

Option C can be offered as a lightweight complement for epJSON users who don't
need the full feature set.

---

## 4. What IDFkit Already Provides vs. What Must Be Built

### Already provided by IDFkit

| Capability | Module | Key API |
|---|---|---|
| IDF parsing | `idf_parser.py` | `parse_idf()` |
| epJSON parsing | `epjson_parser.py` | `parse_epjson()` |
| Schema loading (16 versions) | `schema.py` | `SchemaManager.get_schema()` |
| All 847 object type definitions | `schema.py` | `EpJSONSchema.object_types` |
| Field names, types, defaults | `schema.py` | `get_field_names()`, `get_field_type()`, `get_field_default()` |
| Required fields | `schema.py` | `get_required_fields()` |
| Enum values | `schema.py` | `get_field_schema()["enum"]` |
| Field descriptions | `schema.py` | `get_field_schema()["note"]` |
| Object descriptions | `schema.py` | `get_object_memo()` |
| Units metadata | `schema.py` | `get_field_schema()["units"]` |
| Numeric range constraints | `schema.py` | `get_field_schema()["minimum"]`, etc. |
| Reference resolution | `references.py` | `ReferenceGraph.get_referencing()` |
| Dependency tracking | `references.py` | `ReferenceGraph.get_references()` |
| Dangling reference detection | `references.py` | `get_dangling_references()` |
| Type validation | `validation.py` | `validate_document(check_types=True)` |
| Range validation | `validation.py` | `validate_document(check_ranges=True)` |
| Required field validation | `validation.py` | `validate_document(check_required=True)` |
| Reference integrity validation | `validation.py` | `validate_document(check_references=True)` |
| Format conversion | `writers.py` | `write_idf()`, `write_epjson()` |
| Version management | `versions.py` | 16 supported versions with schema fallback |
| Object groups | Schema data | `"group"` key on each object type |

### Must be built for VS Code integration

| Capability | Description | Difficulty |
|---|---|---|
| Source position tracking | Record line:column ranges during IDF parsing for each object and field | Medium |
| LSP server shell | `pygls`-based server with document sync, lifecycle management | Medium |
| Completion provider | Map schema metadata to LSP `CompletionItem` objects | Low-Medium |
| Diagnostics provider | Map `ValidationError` objects to LSP `Diagnostic` objects with positions | Low |
| Hover provider | Compose hover content from schema notes, types, units, constraints | Low |
| Definition provider | Navigate to referenced object's source position | Low (once positions tracked) |
| References provider | Map `ReferenceGraph` results to source positions | Low (once positions tracked) |
| Document symbol provider | Build symbol tree from document collections | Low |
| Code action provider | Generate quick fixes from validation error codes | Medium |
| Snippet generation | Generate object templates from schema metadata | Low |
| IDF syntax highlighting | TextMate grammar for IDF file format | Low |
| Extension packaging | VS Code extension manifest, Python bundling, activation | Medium |
| Incremental document updates | Re-parse modified regions without full file re-parse | Medium-High |
| Multi-file support | Handle `##include` directives and file references | Medium |

---

## 5. Schema Metadata Depth

The EnergyPlus schema (v24.1) contains metadata that enables extremely
detailed editor assistance:

| Metric | Count |
|---|---|
| Object types | 847 |
| Object groups | 59 |
| Total fields | 12,652 |
| Fields with descriptions (`note`) | 6,055 (47.9%) |
| Fields with default values | 3,764 (29.7%) |
| Fields with enum constraints | 1,505 (11.9%) |
| Fields with units | 4,692 (37.1%) |
| Unique field metadata keys | 20 (type, enum, minimum, maximum, exclusiveMinimum, exclusiveMaximum, default, note, units, ip-units, object_list, reference, data_type, external_list, anyOf, items, maxItems, minItems, retaincase, unitsBasedOnField) |

This metadata density means nearly every field can receive meaningful editor
assistance:
- Almost half of all fields have inline documentation
- Nearly 30% have default values that can pre-populate completions
- Over a third have units that can be shown in hover/completion detail
- Nearly 12% have enum constraints for dropdown-style completion

---

## 6. Performance Considerations

IDFkit's performance characteristics are favorable for real-time editor use:

| Operation | Latency | Notes |
|---|---|---|
| Full IDF parse (1,700 objects) | ~40 ms | Fast enough for debounced re-parse on edit |
| Object lookup by name | ~0.3 μs | O(1), negligible for completion/hover |
| Schema load (first time) | ~200 ms | One-time cost per session, cached afterward |
| Validation (full document) | ~50 ms | Can be limited to `object_types` for incremental |
| Reference graph query | O(1) | Pre-built during parsing |

For a typical editing workflow with 500 ms debounce on keystrokes, a full
re-parse + validation cycle completes well within the budget for models up to
~5,000 objects. Larger models (10,000+ objects) would benefit from incremental
parsing.

---

## 7. Comparison with Existing IDF Editing Tools

| Feature | Text editor (current) | IDF Editor (EnergyPlus) | Proposed IDFkit + VS Code |
|---|---|---|---|
| Syntax highlighting | No | Custom | Yes (TextMate grammar) |
| Auto-completion for object types | No | Dropdown | Yes (fuzzy, filtered) |
| Auto-completion for field names | No | Table columns | Yes (contextual, ordered) |
| Auto-completion for enum values | No | Dropdown | Yes (with descriptions) |
| Auto-completion for references | No | Dropdown | Yes (live from model) |
| Live validation | No | On save | Yes (on keystroke, debounced) |
| Required field indicators | No | Bold columns | Yes (diagnostics + squiggles) |
| Hover documentation | No | Tooltip | Yes (rich markdown) |
| Go to referenced object | No | No | Yes (Ctrl+Click) |
| Find all references | No | No | Yes (Shift+F12) |
| Rename with reference update | No | No | Yes (F2, via `doc.rename()`) |
| Multi-file support | No | No | Possible |
| Version control integration | No | No | Yes (VS Code built-in) |
| Format conversion | External tool | No | Yes (command palette) |
| Extensibility (plugins) | No | No | Yes (VS Code extension API) |

---

## 8. Addressing the Primary Challenge

The primary challenge stated is **"the difficulty in determining the necessary
attributes for a specific IDF object."** IDFkit addresses this at multiple
levels:

### Level 1: Discovery — "What fields does this object have?"
`schema.get_all_field_names("Material")` returns the ordered list:
`["Name", "Roughness", "Thickness", "Conductivity", "Density", "Specific Heat", "Thermal Absorptance", "Solar Absorptance", "Visible Absorptance"]`

In VS Code, this becomes: type `Material,` then press Ctrl+Space to see all
fields with types and defaults.

### Level 2: Obligation — "Which fields must I fill in?"
`schema.get_required_fields("Material")` returns:
`["roughness", "thickness", "conductivity", "density", "specific_heat"]`

In VS Code, required fields are visually distinct in completion lists and
generate error diagnostics if omitted.

### Level 3: Constraint — "What values are valid?"
`schema.get_field_schema("Material", "roughness")["enum"]` returns:
`["MediumRough", "MediumSmooth", "Rough", "Smooth", "VeryRough", "VerySmooth"]`

In VS Code, typing the roughness field value triggers enum completion with
all valid choices.

### Level 4: Context — "What does this field mean?"
`schema.get_field_schema("Zone", "ceiling_height")["note"]` returns:
`"If this field is 0.0, negative or autocalculate, then the average height
of the zone is automatically calculated..."`

In VS Code, hovering over the field shows this documentation plus the units
(`m`), default (`Autocalculate`), and valid types.

### Level 5: Relationships — "What objects reference this one?"
`doc.references.get_referencing("MyZone")` returns all surfaces, people,
lights, equipment, and HVAC objects that reference that zone.

In VS Code, right-click a zone name → "Find All References" shows every
object in the model that depends on it.

---

## 9. Implementation Roadmap

### Phase 1: Foundation
- Add source position tracking to IDF parser (line/column for each object
  and field)
- Create `pygls`-based language server skeleton
- Implement `textDocument/completion` for object types and field names
- Implement `textDocument/publishDiagnostics` from validation results
- Create TextMate grammar for IDF syntax highlighting

### Phase 2: Rich Editing
- Implement `textDocument/hover` with schema documentation
- Implement `textDocument/definition` and `textDocument/references`
- Implement `textDocument/documentSymbol` for outline view
- Add enum value completion and reference target completion
- Add snippet generation for new objects

### Phase 3: Advanced Features
- Implement code actions (quick fixes) for validation errors
- Add rename support (`textDocument/rename`) using `doc.rename()`
- Add format conversion commands
- Implement workspace-level features (multi-file models)
- Add semantic tokens for richer syntax coloring (object types, references,
  numeric values with units)

### Phase 4: Quality of Life
- Incremental parsing for large models
- Configuration for EnergyPlus version selection
- Status bar showing model statistics (object count, validation status)
- Problems panel integration with filtering by error code
- Breadcrumb navigation (Group → Object Type → Object Name → Field)

---

## 10. Conclusion

IDFkit provides a strong foundation for VS Code integration. Its schema system
contains the full depth of EnergyPlus object/field metadata needed for
auto-completion, validation, hover documentation, and reference navigation. Its
O(1) lookup architecture ensures responsive editor performance. The main
engineering work lies in:

1. **Source position tracking** — augmenting the parser to record where each
   object and field lives in the source text
2. **LSP integration** — connecting IDFkit's existing APIs to Language Server
   Protocol handlers via `pygls`
3. **IDF grammar** — a TextMate grammar for basic syntax highlighting

The library already solves the hardest problems (schema interpretation,
reference graph construction, validation logic). The VS Code integration layer
is primarily a translation between IDFkit's data model and the LSP protocol.
