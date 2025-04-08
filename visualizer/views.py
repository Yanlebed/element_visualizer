from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .forms import JsonUploadForm
from .utils import parse_json_data, place_tags_grid_snapping, generate_visualization


def index(request):
    """Home page with file upload form"""
    form = JsonUploadForm()
    return render(request, 'visualizer/index.html', {'form': form})


@csrf_exempt
def visualize(request):
    """Process the uploaded JSON file and visualize elements"""
    if request.method == 'POST':
        form = JsonUploadForm(request.POST, request.FILES)

        if form.is_valid():
            # Get form settings
            show_other_families = form.cleaned_data.get('show_other_families', False)

            # Use default values for visualization settings
            tag_size = 12
            auto_scale = True  # Always enable auto-scaling for better visualization

            # Get and save the file temporarily
            json_file = request.FILES['json_file']
            file_content = json_file.read().decode('utf-8')

            # Parse the JSON data
            elements = parse_json_data(file_content)

            if not elements:
                return render(request, 'visualizer/index.html', {
                    'form': form,
                    'error': 'No valid elements found in the JSON file.'
                })

            # Separate KIT(DS)1 elements from others
            kit_elements = [e for e in elements if e.is_kit_ds1]
            other_elements = [e for e in elements if not e.is_kit_ds1] if show_other_families else []

            if not kit_elements:
                return render(request, 'visualizer/index.html', {
                    'form': form,
                    'error': 'No KIT(DS)1 family elements found in the JSON file.'
                })

            # Generate tags with optimized positions
            tags = place_tags_grid_snapping(kit_elements, other_elements, tag_size)

            # Generate visualization
            image_data, element_data_json = generate_visualization(
                kit_elements, tags, other_elements, tag_size, auto_scale
            )

            # Statistics for the template
            stats = {
                'total_elements': len(elements),
                'kit_elements': len(kit_elements),
                'other_elements': len(other_elements),
                'tags_placed': len(tags)
            }

            return render(request, 'visualizer/result.html', {
                'image_data': image_data,
                'element_data_json': element_data_json,
                'stats': stats,
                'form': form
            })

        else:
            # Form is not valid
            return render(request, 'visualizer/index.html', {
                'form': form,
                'error': 'Please submit a valid JSON file.'
            })

    # If not POST, redirect to index
    return redirect('visualizer:index')