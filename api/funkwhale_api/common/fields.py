from django.db import models


PRIVACY_LEVEL_CHOICES = [
    ('me', 'Only me'),
    ('followers', 'Me and my followers'),
    ('instance', 'Everyone on my instance, and my followers'),
    ('everyone', 'Everyone, including people on other instances'),
]


def get_privacy_field():
    return models.CharField(
        max_length=30, choices=PRIVACY_LEVEL_CHOICES, default='instance')


def privacy_level_query(user, lookup_field='privacy_level'):
    if user.is_anonymous:
        return models.Q(**{
            lookup_field: 'everyone',
        })

    return models.Q(**{
        '{}__in'.format(lookup_field): [
            'me', 'followers', 'instance', 'everyone'
        ]
    })
