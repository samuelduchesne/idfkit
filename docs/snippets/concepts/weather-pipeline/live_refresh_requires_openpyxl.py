# Check if upstream data has changed
if index.check_for_updates():
    index = StationIndex.refresh()  # Downloads ~10 Excel files
