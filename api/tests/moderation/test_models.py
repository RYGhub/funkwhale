def test_setting_report_handled_to_true_sets_handled_date(factories, now):
    target = factories["music.Artist"]()
    report = factories["moderation.Report"](target=target)

    assert report.is_handled is False
    assert report.handled_date is None

    report.is_handled = True
    report.save()

    assert report.handled_date == now


def test_setting_report_handled_to_false_sets_handled_date_to_null(factories, now):
    target = factories["music.Artist"]()
    report = factories["moderation.Report"](
        target=target, is_handled=True, handled_date=now
    )
    report.is_handled = False
    report.save()

    assert report.handled_date is None
