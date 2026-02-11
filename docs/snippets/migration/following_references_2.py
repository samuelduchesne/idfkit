surface = doc["BuildingSurface:Detailed"][0]
construction = surface.get_referenced_object("construction_name")
