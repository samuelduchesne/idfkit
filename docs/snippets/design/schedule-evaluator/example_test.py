def test_compact_weekday_schedule():
    doc = load_idf("tests/fixtures/office_schedules.idf")
    schedule = doc.get_schedule("Office Occupancy")

    # Monday 10am should be occupied
    assert evaluate(schedule, datetime(2024, 1, 8, 10, 0)) == 1.0

    # Saturday 10am should be unoccupied
    assert evaluate(schedule, datetime(2024, 1, 6, 10, 0)) == 0.0

    # Monday 6am should be unoccupied (before 8am)
    assert evaluate(schedule, datetime(2024, 1, 8, 6, 0)) == 0.0
