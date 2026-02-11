if index.check_for_updates():
    index = StationIndex.refresh()  # Downloads latest data
