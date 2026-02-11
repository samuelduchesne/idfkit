environments = sql.get_environments()

for env in environments:
    print(f"{env.index}: {env.name} (type={env.environment_type})")
