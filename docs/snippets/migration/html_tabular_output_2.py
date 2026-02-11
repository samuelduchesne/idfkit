result = simulate(doc, weather)
html = result.html  # HTMLResult, lazily parsed

# eppy-compatible (title, rows) pairs
for title, rows in html.titletable():
    print(title, len(rows), "rows")

# Lookup by name
table = html.tablebyname("Site and Source Energy")
print(table.to_dict())  # {row_key: {col_header: value}}

# Filter by report
annual = html.tablesbyreport("Annual Building Utility Performance Summary")
