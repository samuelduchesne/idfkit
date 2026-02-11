sql = result.sql
if sql is not None:
    # Time-series data
    ts = sql.get_timeseries(
        variable_name="Zone Mean Air Temperature",
        key_value="THERMAL ZONE 1",
    )
    print(f"Max: {max(ts.values):.1f}°C")

    # Tabular reports
    rows = sql.get_tabular_data(report_name="AnnualBuildingUtilityPerformanceSummary")
