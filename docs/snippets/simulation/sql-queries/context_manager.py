with SQLResult("/path/to/eplusout.sql") as sql:
    ts = sql.get_timeseries("Zone Mean Air Temperature", "ZONE 1")
    # Connection automatically closed on exit
