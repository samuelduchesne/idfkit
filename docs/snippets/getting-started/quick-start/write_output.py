from idfkit import write_idf, write_epjson

# Write to IDF format
write_idf(model, "output.idf")

# Or write to epJSON format
write_epjson(model, "output.epJSON")

# Get as string (no file path)
idf_string = write_idf(model)
