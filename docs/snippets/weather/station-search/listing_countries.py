# Get all available countries
countries = index.countries

for country in sorted(countries)[:10]:
    count = len(index.filter(country=country))
    print(f"{country}: {count} stations")
