err_text = Path("eplusout.err").read_text()
errors = ErrorReport.from_string(err_text)
