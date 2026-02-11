# Get DataFrame
df = ts.to_dataframe()

# Matplotlib via pandas
df.plot(figsize=(12, 6))

# Plotly via pandas
import plotly.express as px

fig = px.line(df.reset_index(), x="timestamp", y=ts.variable_name)
