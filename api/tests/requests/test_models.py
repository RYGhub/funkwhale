def test_can_bind_import_batch_to_request(factories):
    request = factories["requests.ImportRequest"]()

    assert request.status == "pending"

    # when we create the import, we consider the request as accepted
    batch = factories["music.ImportBatch"](import_request=request)
    request.refresh_from_db()

    assert request.status == "accepted"

    # now, the batch is finished, therefore the request status should be
    # imported
    batch.status = "finished"
    batch.save(update_fields=["status"])
    request.refresh_from_db()

    assert request.status == "imported"
