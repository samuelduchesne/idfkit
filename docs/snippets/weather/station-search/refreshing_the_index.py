# Check if upstream has updates
if index.check_for_updates():
    print("Updates available")

    # Refresh from climate.onebuilding.org (requires openpyxl)
    index = StationIndex.refresh()
