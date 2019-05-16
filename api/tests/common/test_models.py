import pytest

from django.urls import reverse

from funkwhale_api.federation import utils as federation_utils


@pytest.mark.parametrize(
    "model,factory_args,namespace",
    [("common.Mutation", {"created_by__local": True}, "federation:edits-detail")],
)
def test_mutation_fid_is_populated(factories, model, factory_args, namespace):
    instance = factories[model](**factory_args, fid=None, payload={})

    assert instance.fid == federation_utils.full_url(
        reverse(namespace, kwargs={"uuid": instance.uuid})
    )
