surface = idf.idfobjects["BuildingSurface:Detailed"][0]
construction = surface.get_referenced_object("Construction_Name")
