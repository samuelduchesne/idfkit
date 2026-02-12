# EPPY to IdfKit Migration Evaluation

**Perspective**: An EPPY user evaluating IdfKit as a replacement.

## Executive Summary

IdfKit is a well-designed, production-ready replacement for EPPY. The migration
path is smooth for most common workflows, thanks to a deliberate compatibility
layer that preserves the majority of EPPY's API surface. The library is faster,
better-typed, and has a richer feature set. However, there are several
roadblocks and rough edges that a migrating user would encounter.

---

## What Went Smoothly

### 1. Loading Files: Night-and-Day Improvement

The biggest immediate win. EPPY requires locating and passing the IDD file:

```python
# EPPY — tedious and error-prone
from eppy.modeleditor import IDF
IDF.setiddname("/path/to/Energy+.idd")
idf = IDF("/path/to/in.idf")
```

IdfKit bundles schemas for v8.9–v25.2 and auto-detects the version:

```python
# IdfKit — just works
from idfkit import load_idf
doc = load_idf("in.idf")
```

No more hunting for IDD files, no version mismatches, no class-level global
state. This alone justifies the switch.

### 2. The Compatibility Layer Actually Works

The eppy-compatible aliases (`newidfobject`, `idfobjects`, `getobject`,
`getreferingobjs`, `fieldnames`, `fieldvalues`, `theidf`, `key`, etc.) all
resolve correctly. I could take existing EPPY code and most of it ran with
only import changes. The 66 eppy compatibility tests all pass.

### 3. Reference Tracking is Transformative

EPPY has no built-in way to answer "what objects reference this zone?" You end
up writing ad-hoc iteration loops. IdfKit maintains a live `ReferenceGraph`
with O(1) lookups:

```python
for obj in doc.get_referencing("Office"):
    print(obj.obj_type, obj.name)
```

And cascading renames (change a zone name and all surfaces/people/lights
automatically update) eliminate an entire class of bugs in parametric scripts.

### 4. Built-in Geometry

No need for the separate `geomeppy` package. `Vector3D`, `Polygon3D`,
surface area/tilt/azimuth, zone volume/height, building translate/rotate are
all built in with no external dependencies.

### 5. Performance

O(1) object lookups via dict-indexed collections vs. EPPY's linear scans.
For large models (1,700+ objects), this is a 750x speedup on lookups.

### 6. Validation and Introspection

`validate_document()` catches issues (missing required fields, out-of-range
values, dangling references) before simulation. `describe()` shows all
available fields for an object type with their types, defaults, and
constraints — much better than scanning IDD files manually.

---

## Roadblocks Encountered During Migration

### Roadblock 1: Field Name Casing (Moderate Friction)

EPPY uses capitalized IDD field names (`zone.X_Origin`). IdfKit uses
snake_case (`zone.x_origin`). Both work in IdfKit due to `__getattr__`
resolution, but:

- **Find-and-replace across a codebase is unreliable** because `X_Origin` could
  mean different things in different contexts.
- **Documentation and stack traces show snake_case**, so when debugging you see
  `x_origin` even if your code says `X_Origin`. This is disorienting at first.
- The migration guide documents this well, but it's still the most tedious part
  of a bulk migration.

**Verdict**: Not a blocker, but the single largest source of manual work.

### Roadblock 2: Object Type Casing (Minor Friction)

EPPY uses ALL CAPS for object types (`idf.idfobjects["ZONE"]`). IdfKit uses
proper case (`doc["Zone"]`). The `idfobjects` compatibility view handles
case-insensitive lookups, so old-style EPPY code works. But if you start mixing
the two APIs, you can get confused about whether `doc["ZONE"]` and `doc["Zone"]`
return the same collection (they do, via different code paths).

**Verdict**: Handled well by the compatibility layer, minimal friction.

### Roadblock 3: `outputtype` Property Missing (Minor)

EPPY sets output formatting on the document:

```python
idf.outputtype = "compressed"
idf.saveas("out.idf")
```

IdfKit has no `outputtype` property on `IDFDocument`. Instead, you pass it to
the writer:

```python
write_idf(doc, "out.idf", output_type="compressed")
```

This means `save()` / `saveas()` / `savecopy()` don't accept an `output_type`
parameter — they always write in standard format. If your EPPY code relied on
setting `outputtype` before calling `save()`, you need to switch to the
`write_idf()` function instead.

**Verdict**: Minor API gap. The workaround is straightforward but undocumented
in the migration guide's save section.

### Roadblock 4: No `idf.run()` Equivalent on the Document (Moderate)

EPPY provides `idf.run()` directly on the document object. IdfKit requires
importing a separate function:

```python
from idfkit.simulation import simulate
result = simulate(doc, weather="weather.epw")
```

This is arguably better design (separation of concerns), but it breaks the
common EPPY pattern of `idf.run()`. Users who have `idf.run()` calls
scattered through their code need to refactor each one.

**Verdict**: Good design, but a migration friction point not covered in the
migration guide.

### Roadblock 5: `getiddgroupdict()` Returns Simplified Groups (Minor)

The migration guide lists `getiddgroupdict()` as compatible. However, the
implementation splits on `:` to infer groups rather than using actual IDD
group metadata:

```python
# IdfKit implementation (document.py:322-334)
parts = obj_type.split(":")
group = parts[0] if len(parts) > 1 else "Miscellaneous"
```

This means `BuildingSurface:Detailed` lands in a group called
`"BuildingSurface"` rather than the IDD's `"Thermal Zones and Surfaces"`.
Code that relies on specific group names will break silently.

**Verdict**: Documented as compatible but actually diverges. Could cause subtle
bugs in code that filters by group name.

### Roadblock 6: No geomeppy High-Level Operations

EPPY users who rely on `geomeppy` for:

- `idf.set_wwr()` (window-wall ratio)
- `idf.intersect_match()` (surface intersection and boundary matching)
- `idf.set_default_constructions()`
- HVAC loop diagrams

will find no equivalent in IdfKit. IdfKit's geometry module provides low-level
primitives (`Vector3D`, `Polygon3D`, tilt/azimuth, translate/rotate) but not
the higher-level building manipulation functions. Users with these workflows
would need to either:

1. Reimplement the logic using IdfKit's geometry primitives
2. Keep geomeppy as a separate dependency for those operations (but geomeppy
   depends on EPPY, creating a circular dependency problem)

**Verdict**: Significant gap for users who rely on geomeppy's high-level API.
This is the biggest functional blocker.

### Roadblock 7: `__getattr__` Returns `None` for Missing Fields (Subtle)

In EPPY, accessing a non-existent field raises `AttributeError` (after the
field list is exhausted). In IdfKit, `IDFObject.__getattr__` returns `None`
for any field not found in the data dict:

```python
# objects.py:204
# Field not found - return None (eppy behavior)
return None
```

This means typos in field names silently return `None` instead of raising an
error. For example, `zone.x_orgin` (typo) returns `None` without warning.
While this was intentional for EPPY compatibility, it makes debugging harder
during migration when you're unsure of the correct snake_case names.

The `validate=True` flag on `add()` catches unknown fields at creation time,
but not for reads on existing objects.

**Verdict**: Design trade-off that hurts discoverability. The `describe()`
method helps, but a "strict mode" that raises on unknown field access would
be valuable during migration.

### Roadblock 8: `doc.update()` Key Format Doesn't Support Dots in Names (Minor)

The batch update API uses dot-separated keys (`"Zone.Office.x_origin"`), but
EnergyPlus object names can contain dots. The documentation acknowledges this
limitation but provides no workaround syntax (like escaping):

```python
# This would fail for an object named "Floor.1":
doc.update({"Zone.Floor.1.x_origin": 10.0})
```

**Verdict**: Edge case, but worth knowing. The workaround is to use
`getobject()` + direct attribute assignment instead.

### Roadblock 9: Missing `idf.model` / `idf.idd_info` Internals

Some EPPY scripts access the internal `idf.model` dict or `idf.idd_info` for
custom processing. IdfKit has no equivalent. You'd use `doc.collections` and
`doc.schema` instead, but the data structures are different enough that direct
translation isn't possible.

**Verdict**: Only affects users with deeply customized EPPY scripts.

---

## Migration Guide Quality

The migration guide (`docs/migration.md`) is well-structured with side-by-side
comparisons. However:

1. **Code snippets use include directives** (`--8<--`) rather than inline code,
   so the rendered documentation depends on a build step. Reading the raw
   markdown is less helpful.
2. **Missing coverage for `idf.run()`** — the simulation API change is not
   mentioned in the migration guide at all.
3. **Missing coverage for `outputtype` on save methods** — the guide shows
   `write_idf()` with `output_type` but doesn't note that `save()`/`saveas()`
   don't support it.
4. **No guidance on geomeppy replacement** — users relying on geomeppy features
   are left without a path forward.

---

## Recommendations for the IdfKit Project

1. **Add `simulate()` to the migration guide** — it's one of the most common
   EPPY operations.
2. **Add `output_type` parameter to `save()`/`saveas()`** — or document the
   gap explicitly.
3. **Implement `getiddgroupdict()` using actual schema group metadata** — the
   schema already exposes groups via `get_group()`, so the simplified
   implementation is unnecessarily inaccurate.
4. **Consider a strict mode for field access** — a flag or context manager that
   raises `AttributeError` on unknown fields would significantly help migration
   debugging.
5. **Document the geomeppy gap** — either plan to implement `set_wwr()` and
   `intersect_match()` or explicitly state these are out of scope.
6. **Add a `doc.run()` convenience method** — wrapping `simulate()` on the
   document object would reduce migration friction, even if the standalone
   function remains the recommended API.

---

## Bottom Line

IdfKit is a clear improvement over EPPY in every dimension that matters:
performance, type safety, API design, documentation, and feature breadth. For
new projects, it's an easy choice. For migration from EPPY, the compatibility
layer covers ~80% of the API surface with minimal changes. The remaining 20%
involves genuine refactoring work, primarily around field name casing,
simulation invocation, and any geomeppy dependencies. None of the roadblocks
are showstoppers for a determined migration, but the geomeppy gap and the
silent `None` on unknown fields are the two issues most likely to cause
frustration.
