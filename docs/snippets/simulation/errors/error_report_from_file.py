from idfkit.simulation import ErrorReport

errors = ErrorReport.from_file("/path/to/eplusout.err")
print(errors.summary())
