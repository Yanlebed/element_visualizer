# visualizer/utils.py
import json
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
import base64
import random
import math
import os
from django.conf import settings


class Element:
    """Class representing a single element from the JSON data"""

    def __init__(self, data):
        self.id = data.get('id')
        self.family_name = data.get('coordinates', {}).get('family_name')
        self.min_x = data.get('coordinates', {}).get('min', {}).get('x')
        self.min_y = data.get('coordinates', {}).get('min', {}).get('y')
        self.max_x = data.get('coordinates', {}).get('max', {}).get('x')
        self.max_y = data.get('coordinates', {}).get('max', {}).get('y')
        self.center_x = data.get('coordinates', {}).get('center', {}).get('x')
        self.center_y = data.get('coordinates', {}).get('center', {}).get('y')
        self.document = data.get('document')
        self.is_kit_ds1 = 'KIT(DS)1' in self.family_name if self.family_name else False

    @property
    def width(self):
        return self.max_x - self.min_x if self.max_x and self.min_x else 0

    @property
    def height(self):
        return self.max_y - self.min_y if self.max_y and self.min_y else 0

    @property
    def bounds(self):
        """Returns (min_x, min_y, max_x, max_y)"""
        return (self.min_x, self.min_y, self.max_x, self.max_y)

    @property
    def center(self):
        """Returns (center_x, center_y)"""
        return (self.center_x, self.center_y)

    def get_color(self):
        """Returns color based on element type"""
        return '#3498db' if self.is_kit_ds1 else '#cccccc'


class Tag:
    """Class representing a tag/label associated with an element"""

    def __init__(self, element, text=None, tag_size=8):
        self.element = element

        # Use ID as the tag text
        self.text = text or f"{element.id}"
        self.tag_size = tag_size

        # Default position (will be optimized later)
        self.x = element.center_x
        self.y = element.center_y

        # Calculate tag dimensions based on text length
        text_length = len(self.text)

        # Base dimensions on text length with constraints
        # These will be adjusted based on view area in place_tags_grid_snapping
        self.width = 0.2 * text_length + 0.4  # Increased for more room
        self.height = 0.6  # Increased for better text visibility

        # The actual size constraints will be applied after view area is known
        # in place_tags_grid_snapping and generate_visualization

        # Connection line start point (to element)
        self.line_start_x = element.center_x
        self.line_start_y = element.center_y

    def adjust_size_to_view(self, view_width, view_height):
        """Adjust tag size to be proportional to the view area"""
        # Make sure tag is not too large relative to the view area
        max_width = view_width / 7  # No more than 1/7 of X-axis
        max_height = view_height / 6  # No more than 1/6 of Y-axis

        # Apply constraints
        if self.width > max_width:
            self.width = max_width

        if self.height > max_height:
            self.height = max_height

        # Make sure the tag isn't too small either
        min_width = 0.5  # Minimum width for visibility
        min_height = 0.3  # Minimum height for text

        self.width = max(self.width, min_width)
        self.height = max(self.height, min_height)

        return self

    def overlaps(self, other_tag):
        """Check if this tag overlaps with another tag"""
        # Add a small buffer for visual separation
        buffer = 0.1

        # Bounding boxes overlap test with buffer
        if (self.x - buffer < other_tag.x + other_tag.width + buffer and
                self.x + self.width + buffer > other_tag.x - buffer and
                self.y - buffer < other_tag.y + other_tag.height + buffer and
                self.y + self.height + buffer > other_tag.y - buffer):
            return True
        return False

    def overlaps_element(self, element):
        """Check if tag overlaps with any element"""
        # Larger buffer for better separation
        buffer = 0.2  # Increased from 0.1 to 0.2

        if (self.x - buffer < element.max_x + buffer and
                self.x + self.width + buffer > element.min_x - buffer and
                self.y - buffer < element.max_y + buffer and
                self.y + self.height + buffer > element.min_y - buffer):
            return True
        return False

    def _line_intersects_rectangle(self, line_x1, line_y1, line_x2, line_y2,
                                   rect_x1, rect_y1, rect_x2, rect_y2):
        """Helper method to check if a line segment intersects a rectangle"""
        # Check if either endpoint is inside the rectangle
        if (rect_x1 <= line_x1 <= rect_x2 and rect_y1 <= line_y1 <= rect_y2) or \
                (rect_x1 <= line_x2 <= rect_x2 and rect_y1 <= line_y2 <= rect_y2):
            return True

        # Check if the line intersects any of the rectangle's edges
        # This is a simplified check - doesn't catch all cases but good enough for our purpose
        edges = [
            (rect_x1, rect_y1, rect_x2, rect_y1),  # Top edge
            (rect_x2, rect_y1, rect_x2, rect_y2),  # Right edge
            (rect_x1, rect_y2, rect_x2, rect_y2),  # Bottom edge
            (rect_x1, rect_y1, rect_x1, rect_y2)  # Left edge
        ]

        for edge_x1, edge_y1, edge_x2, edge_y2 in edges:
            if self._line_segments_intersect(
                    line_x1, line_y1, line_x2, line_y2,
                    edge_x1, edge_y1, edge_x2, edge_y2
            ):
                return True

        return False

    def _line_segments_intersect(self, line1_x1, line1_y1, line1_x2, line1_y2,
                                 line2_x1, line2_y1, line2_x2, line2_y2):
        """Check if two line segments intersect"""
        # Calculate the direction vectors
        dx1 = line1_x2 - line1_x1
        dy1 = line1_y2 - line1_y1
        dx2 = line2_x2 - line2_x1
        dy2 = line2_y2 - line2_y1

        # Calculate the determinant
        det = dx1 * dy2 - dy1 * dx2

        # If det is zero, lines are parallel
        if abs(det) < 1e-10:
            return False

        # Calculate parameters t and s for the intersection point
        t = ((line2_x1 - line1_x1) * dy2 - (line2_y1 - line1_y1) * dx2) / det
        s = ((line2_x1 - line1_x1) * dy1 - (line2_y1 - line1_y1) * dx1) / det

        # Check if intersection is within both line segments
        return 0 <= t <= 1 and 0 <= s <= 1

    def distance_to_element(self):
        """Calculate distance from tag center to element center"""
        tag_center_x = self.x + self.width / 2
        tag_center_y = self.y + self.height / 2
        dx = tag_center_x - self.element.center_x
        dy = tag_center_y - self.element.center_y
        return math.sqrt(dx * dx + dy * dy)

    def get_bounds(self):
        """Returns (min_x, min_y, max_x, max_y)"""
        return (self.x, self.y, self.x + self.width, self.y + self.height)


def parse_json_data(file_content):
    """Parse JSON data and create Element objects"""
    try:
        data = json.loads(file_content)
        elements = [Element(item) for item in data]
        return elements
    except Exception as e:
        # Handle parsing errors
        print(f"Error parsing JSON: {e}")
        return []


def align_tags_in_groups(tags, proximity_threshold=50):
    """Aligns tags in horizontal or vertical groups based on proximity"""
    # Find horizontal groups (similar y-coordinates)
    y_groups = {}
    for tag in tags:
        # Round y to the nearest multiple of proximity_threshold
        group_y = round(tag.y / proximity_threshold) * proximity_threshold
        if group_y not in y_groups:
            y_groups[group_y] = []
        y_groups[group_y].append(tag)

    # Align tags within each horizontal group
    for group_y, group_tags in y_groups.items():
        if len(group_tags) > 1:
            # Find average y position
            avg_y = sum(tag.y for tag in group_tags) / len(group_tags)
            # Set all tags to that y position
            for tag in group_tags:
                tag.y = avg_y

    # Similar process for vertical groups (similar x-coordinates)
    x_groups = {}
    for tag in tags:
        group_x = round(tag.x / proximity_threshold) * proximity_threshold
        if group_x not in x_groups:
            x_groups[group_x] = []
        x_groups[group_x].append(tag)

    # Align tags within each vertical group
    for group_x, group_tags in x_groups.items():
        if len(group_tags) > 1:
            avg_x = sum(tag.x for tag in group_tags) / len(group_tags)
            for tag in group_tags:
                tag.x = avg_x

    return tags


def place_tags_grid_snapping(kit_elements, other_elements=None, tag_size=8):
    """
    Place tags using a grid snapping approach

    Args:
        kit_elements: List of Element objects from KIT(DS)1 family
        other_elements: Optional list of other Element objects
        tag_size: Size of the tags

    Returns:
        A list of Tag objects with optimized positions
    """
    if not kit_elements:
        return []

    # Create initial tags
    tags = [Tag(element, tag_size=tag_size) for element in kit_elements]

    # Find overall bounds of all elements to create our grid
    all_elements = kit_elements + (other_elements or [])
    min_x = min(e.min_x for e in all_elements)
    min_y = min(e.min_y for e in all_elements)
    max_x = max(e.max_x for e in all_elements)
    max_y = max(e.max_y for e in all_elements)

    # Calculate view dimensions for tag size constraints
    view_width = max_x - min_x
    view_height = max_y - min_y

    # Apply size constraints to each tag
    for tag in tags:
        tag.adjust_size_to_view(view_width, view_height)

    # Special case for single element or very few elements - place tags very close
    if len(all_elements) <= 3:
        for tag in tags:
            element = tag.element

            # Determine view boundaries for smart positioning
            base_x = int(element.center_x)
            base_y = int(element.center_y)

            # For single elements, ensure appropriate view dimensions for constraints
            if len(all_elements) == 1:
                # Approximate the expected view area (similar to generate_visualization)
                expected_view_width = 3  # About 3 units for 1705-1708
                expected_view_height = 3  # About 3 units for 100-103

                # Re-adjust tag size with expected view dimensions
                tag.adjust_size_to_view(expected_view_width, expected_view_height)

            # Determine which side has more room (assuming a 3-unit view)
            # If element is at 1706.x, there's more room to the right (1707-1708)
            # than to the left (1705-1706)
            remaining_right = (base_x + 2) - element.max_x
            remaining_left = element.min_x - (base_x - 1)

            # Place tag on the side with more space
            if remaining_right >= remaining_left:
                # Place to the right
                offset_x = max(element.width * 1.2, 0.1)
                tag.x = element.center_x + offset_x
            else:
                # Place to the left
                offset_x = max(element.width * 1.2, 0.1)
                tag.x = element.center_x - offset_x - tag.width

            # Vertical alignment with element center
            tag.y = element.center_y - (tag.height / 2)

            # Update connection line endpoints
            tag.line_start_x = element.center_x
            tag.line_start_y = element.center_y

        # No need for grid placement or alignment with so few elements
        return tags

    # Regular case - multiple elements, use grid placement
    # Calculate view dimensions
    view_width = max_x - min_x
    view_height = max_y - min_y

    # Get average element dimensions for perspective
    avg_element_width = sum(e.width for e in all_elements) / len(all_elements)
    avg_element_height = sum(e.height for e in all_elements) / len(all_elements)

    # Get average tag dimensions
    avg_tag_width = sum(t.width for t in tags) / len(tags)
    avg_tag_height = sum(t.height for t in tags) / len(tags)

    # Create grid with cells sized based on the view and elements
    # For multiple elements scenario like in the test JSON
    grid_density = 40  # Increased for even finer grid (was 30)

    # Calculate cell dimensions based on view size and desired density
    # We want cells that are small enough for precise placement but
    # large enough to fit tags
    grid_cell_width = max(view_width / grid_density, avg_tag_width * 0.7)
    grid_cell_height = max(view_height / grid_density, avg_tag_height * 0.7)

    # Calculate grid dimensions
    grid_width = max(15, int(view_width / grid_cell_width) + 2)  # Increased minimum size
    grid_height = max(15, int(view_height / grid_cell_height) + 2)  # Increased minimum size

    # Create grid to track occupied cells
    grid = [[False for _ in range(grid_width)] for _ in range(grid_height)]

    # Mark cells occupied by elements with a larger margin
    for element in all_elements:
        # Use a safety margin around elements to prevent tags overlapping
        safety_margin = max(element.width, element.height) * 1.5  # Increased margin

        start_col = max(0, int((element.min_x - safety_margin - min_x) / grid_cell_width))
        end_col = min(grid_width - 1, int((element.max_x + safety_margin - min_x) / grid_cell_width) + 1)
        start_row = max(0, int((element.min_y - safety_margin - min_y) / grid_cell_height))
        end_row = min(grid_height - 1, int((element.max_y + safety_margin - min_y) / grid_cell_height) + 1)

        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                if 0 <= row < grid_height and 0 <= col < grid_width:
                    grid[row][col] = True

    # Place tags in unoccupied cells close to their elements
    for tag in tags:
        element = tag.element
        center_col = int((element.center_x - min_x) / grid_cell_width)
        center_row = int((element.center_y - min_y) / grid_cell_height)

        # Try to find the best position based on scoring
        best_cell = None
        min_distance = float('inf')

        # For multiple elements, increase the search radius to find better tag positions
        search_radius = max(10, min(grid_width, grid_height) // 2)  # Increased from 8 to 10

        # Score possible positions instead of just using distance
        for r in range(-search_radius, search_radius + 1):
            for c in range(-search_radius, search_radius + 1):
                row, col = center_row + r, center_col + c

                # Check if cell is within grid and unoccupied
                if (0 <= row < grid_height and 0 <= col < grid_width and not grid[row][col]):
                    # Calculate position score based on multiple factors
                    # Euclidean distance (lower is better)
                    distance = math.sqrt(r * r + c * c)

                    # Prefer positions to the right or left of the element
                    # rather than above/below for better readability
                    horizontal_bias = 0.7 if abs(r) < abs(c) else 1.0

                    # Prefer positions that align with existing tags
                    alignment_bonus = 0.0
                    for existing_tag in tags:
                        if tag != existing_tag:
                            exist_y = existing_tag.y
                            potential_y = min_y + row * grid_cell_height
                            if abs(exist_y - potential_y) < grid_cell_height / 2:
                                alignment_bonus = 0.5  # Bonus for horizontal alignment
                                break

                    # Calculate final score (lower is better)
                    score = distance * horizontal_bias - alignment_bonus

                    if score < min_distance:
                        min_distance = score
                        best_cell = (row, col)

        # Use the best cell or default to element center if none found
        if best_cell:
            # Calculate actual coordinates from grid cell
            tag.y = min_y + best_cell[0] * grid_cell_height
            tag.x = min_x + best_cell[1] * grid_cell_width

            # Mark this cell as occupied
            row, col = best_cell
            grid[row][col] = True

            # Keep track of the line that connects tag to element
            tag.line_start_x = element.center_x
            tag.line_start_y = element.center_y
        else:
            # If no good position found, place far from the element to avoid overlap
            # Use a larger offset for safety
            offset = max(element.width, element.height) * 3  # Increased from 1.5 to 3
            tag.x = element.center_x + offset
            tag.y = element.center_y + offset

    # Resolve remaining overlaps if any
    max_adjustment_attempts = 5  # Increased from 3 to 5
    for _ in range(max_adjustment_attempts):
        overlap_found = False

        # Check each tag against all other tags
        for i, tag1 in enumerate(tags):
            for j, tag2 in enumerate(tags):
                if i != j and tag1.overlaps(tag2):
                    overlap_found = True

                    # Move tags slightly away from each other
                    dx = (tag1.x + tag1.width / 2) - (tag2.x + tag2.width / 2)
                    dy = (tag1.y + tag1.height / 2) - (tag2.y + tag2.height / 2)

                    # Determine primary direction of separation
                    if abs(dx) > abs(dy):
                        # Horizontal separation
                        if dx > 0:
                            tag1.x += 0.3  # Increased from 0.2 to 0.3
                            tag2.x -= 0.3
                        else:
                            tag1.x -= 0.3
                            tag2.x += 0.3
                    else:
                        # Vertical separation
                        if dy > 0:
                            tag1.y += 0.3
                            tag2.y -= 0.3
                        else:
                            tag1.y -= 0.3
                            tag2.y += 0.3

        # If no overlaps were found, we're done
        if not overlap_found:
            break

    # Add extra checks to ensure tags don't overlap elements
    # This ensures we catch any remaining overlaps after grid placement
    for tag in tags:
        # Check against all elements, not just the one the tag belongs to
        for element in all_elements:
            if tag.overlaps_element(element):
                # Move tag away from element
                dx = tag.x + tag.width / 2 - element.center_x
                dy = tag.y + tag.height / 2 - element.center_y

                # Calculate distance and normalize
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < 0.001:  # Avoid division by zero
                    dx, dy = 1.0, 0.0  # Default to moving right
                else:
                    dx, dy = dx / dist, dy / dist

                # Move tag outward along this direction
                move_distance = element.width + tag.width / 2 + 0.3  # Ensure enough clearance
                tag.x = element.center_x + dx * move_distance
                tag.y = element.center_y + dy * move_distance

    # Align tags in horizontal or vertical groups
    align_tags_in_groups(tags, proximity_threshold=grid_cell_height)

    # Final check for edge cases - make sure all tags are within reasonable bounds
    # and not too far from their elements
    for tag in tags:
        # Get the distance from tag to its element
        dx = tag.x + tag.width / 2 - tag.element.center_x
        dy = tag.y + tag.height / 2 - tag.element.center_y
        distance = math.sqrt(dx * dx + dy * dy)

        # If tag is too far from its element, bring it closer along the same direction
        if distance > 10:  # Maximum allowed distance
            # Normalize direction vector
            dx, dy = dx / distance, dy / distance

            # Move tag closer to element but still maintain direction
            new_distance = 5  # Reasonable distance
            tag.x = tag.element.center_x + dx * new_distance - tag.width / 2
            tag.y = tag.element.center_y + dy * new_distance - tag.height / 2

    return tags

def create_element_data_json(kit_elements, other_elements=None):
    """Create a JSON string with element data for JavaScript interaction"""
    all_elements = kit_elements + (other_elements or [])
    element_data = {}

    for element in all_elements:
        element_data[str(element.id)] = {
            'id': element.id,
            'family': element.family_name or '',
            'document': element.document or '',
            'min_x': element.min_x,
            'min_y': element.min_y,
            'max_x': element.max_x,
            'max_y': element.max_y,
            'is_kit_ds1': element.is_kit_ds1
        }

    return json.dumps(element_data)


# Replace the generate_visualization function in visualizer/utils.py with this improved version

def generate_visualization(kit_elements, tags, other_elements=None, tag_size=12, auto_scale=True):
    """
    Generate a static image of the elements and tags with clear axes

    Args:
        kit_elements: List of Element objects from KIT(DS)1 family
        tags: List of Tag objects with positions
        other_elements: Optional list of other Element objects
        tag_size: Size of the tags
        auto_scale: Whether to automatically scale elements

    Returns:
        Tuple of (Base64 encoded image data, Element data JSON)
    """
    # Determine plot size
    all_elements = kit_elements + (other_elements or [])

    if not all_elements:
        return None, "{}"

    # Get original element bounds
    orig_min_x = min(e.min_x for e in all_elements)
    orig_min_y = min(e.min_y for e in all_elements)
    orig_max_x = max(e.max_x for e in all_elements)
    orig_max_y = max(e.max_y for e in all_elements)

    # Get tag boundaries if present
    if tags:
        tag_min_x = min(t.x for t in tags)
        tag_min_y = min(t.y for t in tags)
        tag_max_x = max(t.x + t.width for t in tags)
        tag_max_y = max(t.y + t.height for t in tags)

        # Extend element bounds to include tags
        view_min_x = min(orig_min_x, tag_min_x)
        view_min_y = min(orig_min_y, tag_min_y)
        view_max_x = max(orig_max_x, tag_max_x)
        view_max_y = max(orig_max_y, tag_max_y)
    else:
        view_min_x = orig_min_x
        view_min_y = orig_min_y
        view_max_x = orig_max_x
        view_max_y = orig_max_y

    # Add padding around the view area for better visualization
    x_range = view_max_x - view_min_x
    y_range = view_max_y - view_min_y

    # Add more padding for a better view
    padded_min_x = view_min_x - x_range * 0.15
    padded_max_x = view_max_x + x_range * 0.15
    padded_min_y = view_min_y - y_range * 0.15
    padded_max_y = view_max_y + y_range * 0.15

    # Ensure there's enough padding even for small ranges
    if x_range < 10:
        padded_min_x = min(padded_min_x, view_min_x - 1)
        padded_max_x = max(padded_max_x, view_max_x + 1)

    if y_range < 10:
        padded_min_y = min(padded_min_y, view_min_y - 1)
        padded_max_y = max(padded_max_y, view_max_y + 1)

    # Calculate aspect ratio for the figure
    view_width = padded_max_x - padded_min_x
    view_height = padded_max_y - padded_min_y
    aspect_ratio = view_width / view_height

    # Create a figure with appropriate dimensions
    if aspect_ratio > 1.5:
        # Wide view
        fig_width = 12
        fig_height = fig_width / aspect_ratio
    elif aspect_ratio < 0.67:
        # Tall view
        fig_height = 9
        fig_width = fig_height * aspect_ratio
    else:
        # Balanced view
        fig_width = 10
        fig_height = 8

    # Create figure and axis with better DPI for clarity
    fig = Figure(figsize=(fig_width, fig_height), dpi=150)
    ax = fig.add_subplot(111)

    # Set axis limits with a bit more padding
    ax.set_xlim(padded_min_x, padded_max_x)
    ax.set_ylim(padded_min_y, padded_max_y)

    # Plot elements with improved visibility
    for element in all_elements:
        color = element.get_color()
        # Use a thicker line for better visibility
        line_width = 2 if element.is_kit_ds1 else 1.5
        rect = patches.Rectangle(
            (element.min_x, element.min_y),
            element.width,
            element.height,
            linewidth=line_width,
            edgecolor=color,
            facecolor=color,
            alpha=0.7
        )
        ax.add_patch(rect)

    # Plot tags with improved style
    for tag in tags:
        element_color = tag.element.get_color()
        tag_rect = patches.Rectangle(
            (tag.x, tag.y),
            tag.width,
            tag.height,
            linewidth=1.5,
            edgecolor=element_color,
            facecolor='white',
            alpha=0.9
        )
        ax.add_patch(tag_rect)

        # Calculate appropriate font size based on tag height
        font_size = max(tag.height * 0.85, 9)

        ax.text(
            tag.x + tag.width / 2,
            tag.y + tag.height / 2,
            tag.text,
            horizontalalignment='center',
            verticalalignment='center',
            fontsize=font_size,
            color='black',
            weight='bold'
        )

        # Draw connection line
        ax.plot(
            [tag.line_start_x, tag.x + tag.width / 2],
            [tag.line_start_y, tag.y + tag.height / 2],
            color=element_color,
            linestyle='-',
            linewidth=1.5
        )

    # Improve axes labels with larger font
    ax.set_xlabel('X Coordinate', fontsize=12)
    ax.set_ylabel('Y Coordinate', fontsize=12)

    # Add title with larger font
    ax.set_title('Element Visualization', fontsize=14, pad=20)

    # Add grid for better readability
    ax.grid(True, linestyle='--', alpha=0.5)

    # Add more tick marks for better reference
    ax.xaxis.set_major_locator(plt.MaxNLocator(10))
    ax.yaxis.set_major_locator(plt.MaxNLocator(10))

    # Add minor grid lines
    ax.minorticks_on()
    ax.grid(which='minor', linestyle=':', alpha=0.2)

    # Improve tick label formatting with better precision
    import matplotlib.ticker as ticker
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))

    # Make tick labels larger for better readability
    ax.tick_params(axis='both', which='major', labelsize=10)

    # Use tight layout with more padding
    fig.tight_layout(pad=2.5)

    # Render and return image
    canvas = FigureCanvas(fig)
    buffer = io.BytesIO()
    canvas.print_png(buffer)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close(fig)

    # Generate element data JSON
    element_data_json = create_element_data_json(kit_elements, other_elements)

    return image_base64, element_data_json
