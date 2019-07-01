def test_domain_14_migration(migrator):
    a, f, t = ("federation", "0014_auto_20181205_0958", "0015_populate_domains")

    migrator.migrate([(a, f)])
    old_apps = migrator.loader.project_state([(a, f)]).apps
    Actor = old_apps.get_model(a, "Actor")
    a1 = Actor.objects.create(
        fid="http://testmigration1.com",
        preferred_username="test1",
        old_domain="dOmaiN1.com",
    )
    a2 = Actor.objects.create(
        fid="http://testmigration2.com",
        preferred_username="test2",
        old_domain="domain1.com",
    )
    a3 = Actor.objects.create(
        fid="http://testmigration3.com",
        preferred_username="test2",
        old_domain="domain2.com",
    )

    migrator.loader.build_graph()
    migrator.migrate([(a, t)])
    new_apps = migrator.loader.project_state([(a, t)]).apps

    Actor = new_apps.get_model(a, "Actor")
    Domain = new_apps.get_model(a, "Domain")

    a1 = Actor.objects.get(pk=a1.pk)
    a2 = Actor.objects.get(pk=a2.pk)
    a3 = Actor.objects.get(pk=a3.pk)

    assert Domain.objects.count() == 2
    assert a1.domain == Domain.objects.get(pk="domain1.com")
    assert a2.domain == Domain.objects.get(pk="domain1.com")
    assert a3.domain == Domain.objects.get(pk="domain2.com")

    assert Domain.objects.get(pk="domain1.com").creation_date == a1.creation_date
    assert Domain.objects.get(pk="domain2.com").creation_date == a3.creation_date
