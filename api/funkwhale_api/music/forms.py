from django import forms

from . import models


class TranscodeForm(forms.Form):
    FORMAT_CHOICES = [
        ('ogg', 'ogg'),
        ('mp3', 'mp3'),
    ]

    to = forms.ChoiceField(choices=FORMAT_CHOICES)
    BITRATE_CHOICES = [
        (64, '64'),
        (128, '128'),
        (256, '256'),
    ]
    bitrate = forms.ChoiceField(
        choices=BITRATE_CHOICES, required=False)

    track_file = forms.ModelChoiceField(
        queryset=models.TrackFile.objects.exclude(audio_file__isnull=True)
    )
