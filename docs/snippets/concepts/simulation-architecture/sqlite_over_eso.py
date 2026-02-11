# All time-series data is accessible via SQL queries
ts = result.sql.get_timeseries(
    variable_name="Zone Mean Air Temperature",
    key_value="ZONE 1",
)

# Tabular reports (normally in HTML) are also in SQLite
tables = result.sql.get_tabular_data("AnnualBuildingUtilityPerformanceSummary")
