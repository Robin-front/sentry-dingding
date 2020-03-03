# coding: utf-8

from django import forms


class DingDingOptionsForm(forms.Form):
    access_token = forms.CharField(
        max_length=255,
        help_text='DingTalk robot access_token'
    )
    allow_environment = forms.CharField(
        max_length=255,
        required=False,
        help_text='allow environment for notification, split width ,'
    )
    at_mobiles = forms.CharField(
        max_length=255,
        required=False,
        help_text='phone number, split width ,'
    )
