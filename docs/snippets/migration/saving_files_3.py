from idfkit import write_idf, write_epjson

write_idf(doc, "out.idf")
write_epjson(doc, "out.epJSON")  # or convert to epJSON
