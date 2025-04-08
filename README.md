# Element Visualizer

A Django web application for visualizing KIT(DS)1 family elements from JSON data. This tool provides a clear visualization of spatial elements with interactive features.

## Features

- Upload JSON files containing element coordinate data
- Visualize elements with tags for easy identification
- Display element details on click
- View statistics about the visualized elements
- Support for KIT(DS)1 element families
- Option to show other element families

## Requirements

- Python 3.9 or higher
- Django 4.2.10
- Matplotlib 3.7.2

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/element_visualizer.git
   cd element_visualizer
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the Django development server:
   ```bash
   python manage.py runserver
   ```

2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:8000/
   ```

## Usage

1. On the home page, use the file upload form to select your JSON file.
2. Optionally enable "Show other element families" to display elements from families other than KIT(DS)1.
3. Click "Upload & Visualize" to generate the visualization.
4. On the results page, you can:
   - View the visualization of elements and their tags
   - See statistics about the elements
   - Click on elements to view their details
   - Upload another file if needed

## JSON File Format

The application expects JSON files with the following structure:

```json
[
  {
    "id": 7866474,
    "coordinates": {
      "family_name": "KIT(DS)1_Socket",
      "min": { "x": 1706.7449, "y": 101.2527, "z": 116.5833 },
      "center": { "x": 1706.8283, "y": 101.3360, "z": 116.6666 },
      "max": { "x": 1706.9116, "y": 101.4193, "z": 116.7499 }
    },
    "document": "BES - model (R23)"
  },
  {
    "id": 7866475,
    "coordinates": {
      "family_name": "KIT(DS)1_Socket",
      "min": { "x": 1710.5449, "y": 105.2527, "z": 116.5833 },
      "center": { "x": 1710.6283, "y": 105.3360, "z": 116.6666 },
      "max": { "x": 1710.7116, "y": 105.4193, "z": 116.7499 }
    },
    "document": "BES - model (R23)"
  }
]
```

## Project Structure

```
element_visualizer/
├── element_visualizer/      # Project settings
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL routing
│   └── wsgi.py
├── visualizer/              # Main app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py             # Form definitions
│   ├── models.py
│   ├── static/              # Static files
│   │   └── visualizer/
│   │       ├── css/
│   │       │   └── styles.css
│   │       └── js/
│   │           └── visualization.js
│   ├── templates/           # HTML templates
│   │   └── visualizer/
│   │       ├── index.html   # Upload form page
│   │       └── result.html  # Visualization results page
│   ├── urls.py              # App URL routing
│   ├── utils.py             # Visualization logic
│   └── views.py             # View functions
├── manage.py                # Django management script
└── requirements.txt         # Project dependencies
```