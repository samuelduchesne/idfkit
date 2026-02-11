from idfkit.simulation import ProgressParser

parser = ProgressParser()

# Parse a log file
with open("energyplus_stdout.log") as f:
    for line in f:
        event = parser.parse_line(line)
        if event is not None:
            print(f"{event.phase}: {event.message}")
