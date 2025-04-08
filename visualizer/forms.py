# visualizer/forms.py
from django import forms


class JsonUploadForm(forms.Form):
    json_file = forms.FileField(
        label='Select a JSON file',
        help_text='JSON file with element coordinates.',
        widget=forms.FileInput(attrs={'accept': '.json'})
    )

    # Optional setting for visualization
    show_other_families = forms.BooleanField(
        required=False,
        initial=False,
        label='Show other element families (in gray)',
        help_text='Displays elements from families other than KIT(DS)1'
    )