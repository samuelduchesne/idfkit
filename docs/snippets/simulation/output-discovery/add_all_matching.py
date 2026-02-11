# Add all temperature outputs
count = variables.add_all_to_model(
    model,
    filter_pattern="Zone.*Temperature",
)
print(f"Added {count} output requests")
