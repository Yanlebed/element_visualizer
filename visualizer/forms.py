# visualizer/forms.py
from django import forms


class JsonUploadForm(forms.Form):
    json_file = forms.FileField(
        label='Select a JSON file',
        help_text='JSON file with element coordinates.',
        widget=forms.FileInput(attrs={'accept': '.json'})
    )

    # Optional settings for visualization
    show_other_families = forms.BooleanField(
        required=False,
        initial=False,
        label='Show other element families (in gray)',
        help_text='Displays elements from families other than KIT(DS)1'
    )

    tag_size = forms.IntegerField(
        required=False,
        initial=12,  # Increased default size for better visibility
        min_value=5,
        max_value=24,
        label='Tag text size',
        help_text='Size of the tag labels (5-24)'
    )

    auto_scale = forms.BooleanField(
        required=False,
        initial=True,
        label='Auto-scale small elements',
        help_text='Automatically scale up elements that are too small for proper visualization'
    )