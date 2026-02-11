rows = sql.get_tabular_data(report_name="AnnualBuildingUtilityPerformanceSummary")

for row in rows[:5]:
    print(f"{row.table_name} | {row.row_name} | {row.column_name}: {row.value}")
