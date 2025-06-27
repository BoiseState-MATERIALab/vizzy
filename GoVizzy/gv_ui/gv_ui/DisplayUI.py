"""
This module provides functionality to display output widgets for GoVizzy — without showing atoms or bonds.
"""

import ipywidgets as widgets
from ipywidgets import Dropdown, VBox, HBox, Output, AppLayout, Layout, Label, Button, Accordion
import ipyvolume as ipv
import matplotlib.pyplot as plt
from gv_ui import plotting, gvWidgets
from IPython.display import display
import os

# Define globals
selected_option = 'Slice Options'
options = ['Slice Options', 'Mesh Options']
dropdown = Dropdown(options=options, value=options[0], layout=Layout(margin='5px 0 0 5px'))
large_box = Output(layout=Layout(width="70%", height="100%"))
selected_view_options = Output(layout=Layout(width="auto", height='500px'))
slice_picker = Output(layout=Layout(flex='1', border='1px solid black'))
slice_picker_descr = widgets.Label(value="Slice Picker", layout=Layout(margin='5px 0 0 5px'))
exit_button = widgets.Button(description='[X]', button_style='danger')
exit_button.layout.margin = '0 0 0 auto'
in_app_exit = widgets.Button(description='[X]', button_style='danger')
spacer = Output(layout=Layout(flex='1'))
newCube_button = Button(description='New Cube', layout=Layout(width='auto'))
save_button = Button(description='Save', layout=Layout(flex='1'))

# No atom mesh globals, no atom or bond controls

visualizer = None

def show_menu():
    """
    Displays logo and hides the app output.
    """
    exit_button.layout.visibility = 'visible'
    selected_view_options.layout.visibility = 'hidden'
    dropdown.layout.visibility = 'hidden'
    slice_picker.layout.visibility = 'hidden'
    slice_picker_descr.layout.visibility = 'hidden'
    newCube_button.layout.visibility = 'hidden'
    with large_box:
        large_box.clear_output(wait=True)
        large_box.layout = Layout(width="100%", height="85%", justify_content="center", margin="0 0 5% 40%")
        module_path = os.path.abspath(__file__)
        module_dir = os.path.dirname(module_path)
        image_path = os.path.join(module_dir, 'gv.png')
        image_data = plt.imread(image_path)
        plt.figure()
        plt.imshow(image_data)
        plt.axis('off')
        plt.show()

def show_ui():
    """
    Sets the visibility of the GoVizzy output widgets to visible.
    """
    large_box.layout.visibility = 'visible'
    selected_view_options.layout.visibility = 'visible'
    dropdown.layout.visibility = 'visible'
    slice_picker.layout.visibility = 'visible'
    slice_picker_descr.layout.visibility = 'visible'
    newCube_button.layout.visibility = 'visible'

def display_cube(cube):
    """
    Displays the cube plot based on the value of the dropdown — no atoms/bonds.
    """
    global visualizer
    visualizer = plotting.Visualizer(cube)
    with large_box:
        large_box.clear_output()
        large_box.layout = Layout(width="75%", height="100%")

        if selected_option == 'Slice Options':
            visualizer.display_cell_slices()
        elif selected_option == 'Mesh Options':
            visualizer.display_cell()
        else:
            print("Invalid option selected")

def display_cube_mesh_on_slices(cube):
    global visualizer
    visualizer = plotting.Visualizer(cube)
    with large_box:
        large_box.clear_output()
        large_box.layout = Layout(width="75%", height="100%")
        
        if selected_option == 'Slice Options':
            # Show the mesh on slice option
            visualizer.display_cell_slices_pyvista_style()
        elif selected_option == 'Mesh Options':
            # Show the old volume rendering for mesh option
            visualizer.display_cell_pyvista_style()
        else:
            print("Invalid option selected")

    

def display_app():
    """
    Displays the visualization and sets the sidebar options.
    If ipyvolume is used, controls are functional.
    If PyVista is used, shows same widgets as placeholders.
    """
    global visualizer
    top_container = HBox([dropdown, in_app_exit])

    with selected_view_options:
        selected_view_options.clear_output()

        # Check if we have a valid ipyvolume figure with a volume
        if hasattr(visualizer, "figure") and visualizer.figure is not None:
            try:
                figure_controls = visualizer.figure.volumes[0].tf.control()
            except Exception:
                # fallback in case .volumes does not exist yet
                figure_controls = widgets.HTML("<b>Transfer function unavailable</b>")
        else:
            # We don't have ipyvolume — use a dummy placeholder
            figure_controls = widgets.HTML("<b>No transfer function controls (PyVista)</b>")

        if selected_option == 'Slice Options':
            slice_box = VBox([
                slice_picker_descr,
                gvWidgets.slice_x_slider,
                gvWidgets.slice_x_check,
                gvWidgets.slice_y_slider,
                gvWidgets.slice_y_check,
                gvWidgets.slice_z_slider,
                gvWidgets.slice_z_check,
                gvWidgets.slice_color,
                figure_controls,  # either real or placeholder
                newCube_button
            ])
            display(slice_box)

        elif selected_option == 'Mesh Options':
            mesh_box = VBox([
                figure_controls,  # either real or placeholder
                newCube_button
            ])
            display(mesh_box)

        else:
            print("Invalid option selected")

    view_bar = VBox(
        [top_container, selected_view_options],
        layout=Layout(flex='1')
    )
    display_box = HBox([large_box, view_bar])
    app_layout = AppLayout(
        header=None,
        left_sidebar=None,
        center=display_box,
        footer=None,
        pane_heights=['20px', 1, '20px']
    )
    display(app_layout)


def clear_all_outputs():
    """
    Clears the output of the GoVizzy widgets and hides them.
    """
    large_box.clea_


            
                
 
