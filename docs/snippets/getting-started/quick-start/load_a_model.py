from idfkit import load_idf

# Load an existing IDF file
model = load_idf("building.idf")
print(f"Loaded {len(model)} objects")
