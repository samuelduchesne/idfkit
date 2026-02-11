zone = doc["Zone"]["Office"]

# eppy-compatible spelling
referrers = zone.getreferingobjs()

# Corrected spelling
referrers = zone.get_referring_objects()

# Optional filters -- by IDD group and/or field name
surfaces = zone.getreferingobjs(
    iddgroups=["Thermal Zones and Surfaces"],
    fields=["zone_name"],
)
