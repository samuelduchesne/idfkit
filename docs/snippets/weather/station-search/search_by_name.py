# Search by name
results = index.search("chicago ohare")

for r in results[:5]:
    print(f"{r.station.display_name} (score={r.score:.2f})")
