import os
from cube_viskit import Cube
import ipywidgets as widgets
import pyvista as pv
import ipyvolume as ipv
from IPython.display import display, clear_output
from gv_ui import gvWidgets, meshes
import matplotlib.pyplot as plt
from ipyvolume import Figure
import numpy as np
import vtk


class Visualizer:
    """
    A visualization class to create and display widgets from a provided Cube object.


    cube: cube_viskit.Cube
        Cube object created from the parsing of a .cube file.
    """


    cube: Cube
    figure: Figure


    def __init__(self, cube: Cube):
        self.cube = cube


    @staticmethod
    def __vertical_row(key: str, data: list[str]):
        """
        Creates a string in the format <tr><th>{key}</th><td>{data[i]}</td></tr>
        for all entries in the list data.
        """
        row = "<tr>"
        row = "<th>"+key+"</th>"
        for entry in data:
            row += "<td>"+entry+"</td>"
        row += "</tr>"
        return row


    @staticmethod
    def __horizontal_row(key: str, data: list[str]):
        """
        Creates a string in the format <tr><td>{data[i]}</td></tr> for all
        entries in the list data. The key is unused.
        """
        row = "<tr>"
        for entry in data:
            row += "<td>"+entry+"</td>"
        row += "</tr>"
        return row


    @staticmethod
    def __create_table_html(table_data: dict[str, list[str]], vertical: bool=False):
        """
        Creates an HTML <table></table> for all the keys in the table_data dict.
        Creates the rows based on if the vertical bool is true or false using
        the self.__horizontal_row() method if false otherwise
        self.__vertical_row().
        """
        create_row = Visualizer.__vertical_row if vertical else Visualizer.__horizontal_row
        table = "<table>"
        if not vertical:
            for key in table_data:
                table += "<th>" + key + "</th>"
        for key in table_data:
            table += create_row(key, table_data[key])
        table += "</table>"
        return table


    def display_cell_data(self):
        """
        Creates a tab widget returning the file name, prefix, scaling factor,
        units, symbols, periodic boundary conditions, cell vectors, and origin
        of the provided cell object.
        """
        cube = self.cube
        titles = ['Data', 'Cell']
        data = {
            "File Name": [os.path.basename(cube.fname)],
            "Prefix": [cube.prefix],
            "Scaling Factor": [str(cube.scaling_factor)],
            "Units": [cube.units],
        }
        data_table = widgets.HTML(
            value=Visualizer.__create_table_html(data, vertical=True))
        cell = {
            "Symbols": [str(cube.atoms.symbols)],
            "Periodic Boundary Conditions": [str(cube.atoms.pbc)],
            "Cell Vectors": [str(cube.cell)],
            "Origin": [str(cube.origin)],
        }
        cell_table = widgets.HTML(
            value=Visualizer.__create_table_html(cell, vertical=True)
        )
        children = [data_table, cell_table]
        tab = widgets.Tab(children=children, titles=titles)
        display(tab)


   
    def display_cell(self):
        """
        Displays the cube's data3D with the volshow() method.
        """
        cube = self.cube
        self.figure = ipv.figure()
        transfer = ipv.pylab.transfer_function(level=[0.03, 0.5, 0.47], opacity=[0.05, 0.09, 0.1], level_width=0.1, controls=False)
        ipv.style.background_color(gvWidgets.color.value)
        lengths = cube.atoms.cell.lengths()
        extent = [[0,lengths[0]],[0,lengths[1]],[0,lengths[2]]]
        ipv.pylab.volshow(cube.data3D, ambient_coefficient=0.8, lighting=True, tf=transfer, controls=False) # extent = extent
        ipv.show()
       
   
    def display_cell_slices(self):
        """
        Displays the cube's data3D with the volshow() method,
        and attach slices with textures set to the volume data.
        """
        cube = self.cube
        self.figure = ipv.figure()
        transfer = ipv.pylab.transfer_function(level=[0.03, 0.5, 0.47], opacity=[0.05, 0.09, 0.1], level_width=0.1, controls=False)
        ipv.style.background_color(gvWidgets.color.value)
       
        xLen = len(cube.data3D[0][0])
        yLen = len(cube.data3D[0])
        zLen = len(cube.data3D)
       
        ipv.pylab.xlim(0, xLen)
        ipv.pylab.ylim(0, yLen)
        ipv.pylab.zlim(0, zLen)
       
        volume = ipv.pylab.volshow(cube.data3D, ambient_coefficient=0.8, lighting=True, tf=transfer, controls=False, extent=[[0, xLen], [0, yLen], [0, zLen]])
       
        # Create planes, with textures set to the volume info        
        slice_x = ipv.plot_plane('x', volume=volume, description="Slice X", description_color="black", icon="mdi-knife", x_offset=70)
        slice_y = ipv.plot_plane('y', volume=volume, description="Slice Y", description_color="black", icon="mdi-knife", y_offset=70)
        slice_z = ipv.plot_plane('z', volume=volume, description="Slice Z", description_color="black", icon="mdi-knife", z_offset=70)
       
        #Set slider max to cube
        gvWidgets.slice_x_slider.max = xLen-1
        gvWidgets.slice_y_slider.max = yLen-1
        gvWidgets.slice_z_slider.max = zLen-1
       
        widgets.jslink((gvWidgets.slice_x_slider, 'value'), (slice_x, 'x_offset'))
        widgets.jslink((gvWidgets.slice_y_slider, 'value'), (slice_y, 'y_offset'))
        widgets.jslink((gvWidgets.slice_z_slider, 'value'), (slice_z, 'z_offset'))
       
        widgets.jslink((gvWidgets.slice_x_check, 'value'), (slice_x, 'visible'))
        widgets.jslink((gvWidgets.slice_y_check, 'value'), (slice_y, 'visible'))
        widgets.jslink((gvWidgets.slice_z_check, 'value'), (slice_z, 'visible'))
       
        ipv.show()
       
        plt.style.use('_mpl-gallery-nogrid')


        fig, (xSlice, ySlice, zSlice) = plt.subplots(1, 3)


        # Slice order is different to match ipyvolume, which plots the volume in a y-up orientation
        def update(x = 0, y = 0, z = 0):
            color = str(gvWidgets.slice_color.value)
            xSlice.imshow(cube.data3D[:, :, x], color=color,)
            ySlice.imshow(cube.data3D[:, y, :], cmap=color,)
            zSlice.imshow(cube.data3D[z, :, :], cmap=color,)
            plt.show()


        out = widgets.interactive_output(update, {'x':gvWidgets.slice_x_slider,
                         'y':gvWidgets.slice_y_slider,
                         'z':gvWidgets.slice_z_slider})
        display(out)


    def display_cell_pyvista_style(self):
        pv.global_theme.allow_empty_mesh = True
        """
        Fast version: build StructuredGrid from cube data (no plotting).
        """
        cube = self.cube
        data = np.array(cube.data3D)  # (nz, ny, nx)
        nx, ny, nz = data.shape


        a_vec, b_vec, c_vec = np.array(cube.cell)
        origin = np.array(cube.origin)


        # Generate grid points
        points = np.zeros((nx * ny * nz, 3))
        index = 0
        for k in range(nz):
            for j in range(ny):
                for i in range(nx):
                    points[index] = origin + \
                        (i / (nx - 1)) * a_vec + \
                        (j / (ny - 1)) * b_vec + \
                        (k / (nz - 1)) * c_vec
                    index += 1


        grid = pv.StructuredGrid()
        grid.points = points
        grid.dimensions = (nx, ny, nz)
        grid["values"] = data.flatten(order="F")


        return grid, a_vec, b_vec, c_vec, origin


   


    
    def display_cell_slices_pyvista_style(self):
        cube = self.cube

        # Get grid and geometry
        grid, a_vec, b_vec, c_vec, origin = self.display_cell_pyvista_style()
        vtk_data = grid
        xmin, xmax, ymin, ymax, zmin, zmax = grid.bounds

        # Setup PyVista plotter
        plotter = pv.Plotter()
        plotter.set_background("white")

        # Add isosurface
        surface = grid.threshold(value=0.1)

        if surface.n_points > 0:
            plotter.add_mesh(surface, cmap="reds", opacity=0.5)
        else:
            print("Empty mesh, skipped surface plotting.")

        # Bounding box
        corners = [
            origin, origin + a_vec, origin + b_vec, origin + c_vec,
            origin + a_vec + b_vec, origin + a_vec + c_vec,
            origin + b_vec + c_vec, origin + a_vec + b_vec + c_vec
        ]
        edges = [
            (0, 1), (0, 2), (0, 3), (1, 4), (1, 5),
            (2, 4), (2, 6), (3, 5), (3, 6), (4, 7), (5, 7), (6, 7)
        ]
        for i, j in edges:
            line = pv.Line(corners[i], corners[j])
            plotter.add_mesh(line, color="black", line_width=1)

        # Dimensions
        xLen, yLen, zLen = cube.data3D.shape[2], cube.data3D.shape[1], cube.data3D.shape[0]
        gvWidgets.slice_x_slider.max = xLen - 1
        gvWidgets.slice_y_slider.max = yLen - 1
        gvWidgets.slice_z_slider.max = zLen - 1

        x0, y0, z0 = 0.5 * (xmin + xmax), 0.5 * (ymin + ymax), 0.5 * (zmin + zmax)

        # Planes
        plane_x = vtk.vtkPlane(); plane_x.SetNormal(1, 0, 0); plane_x.SetOrigin(x0, 0, 0)
        plane_y = vtk.vtkPlane(); plane_y.SetNormal(0, 1, 0); plane_y.SetOrigin(0, y0, 0)
        plane_z = vtk.vtkPlane(); plane_z.SetNormal(0, 0, 1); plane_z.SetOrigin(0, 0, z0)

        # Cutters
        cutter_x = vtk.vtkCutter(); cutter_x.SetCutFunction(plane_x); cutter_x.SetInputData(vtk_data); cutter_x.Update()
        cutter_y = vtk.vtkCutter(); cutter_y.SetCutFunction(plane_y); cutter_y.SetInputData(vtk_data); cutter_y.Update()
        cutter_z = vtk.vtkCutter(); cutter_z.SetCutFunction(plane_z); cutter_z.SetInputData(vtk_data); cutter_z.Update()

        # Mappers & Actors
        def make_actor(cutter):
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(cutter.GetOutputPort())
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(0, 0, 0)
            actor.GetProperty().SetOpacity(0.5)
            plotter.renderer.AddActor(actor)
            return actor, mapper

        actor_x, mapper_x = make_actor(cutter_x)
        actor_y, mapper_y = make_actor(cutter_y)
        actor_z, mapper_z = make_actor(cutter_z)

        # Matplotlib figure for 2D slices
        fig, (ax_x, ax_y, ax_z) = plt.subplots(1, 3, figsize=(12, 4))
        fig.tight_layout()
        plt.subplots_adjust(wspace=0.4)

        img_x = ax_x.imshow(cube.data3D[0, :, :], cmap="gray")
        img_y = ax_y.imshow(cube.data3D[:, 0, :], cmap="gray")
        img_z = ax_z.imshow(cube.data3D[:, :, 0], cmap="gray")
        ax_x.set_title("X Slice")
        ax_y.set_title("Y Slice")
        ax_z.set_title("Z Slice")

        
        # 3. Display figure inside an Output widget to keep it live
        slice_output = widgets.Output()
        display(slice_output)
        # --- UPDATE FUNCTION ---
        

        def update(x=0, y=0, z=0, x_check=False, y_check=False, z_check=False):
            x = min(max(x, 0), xLen - 1)
            y = min(max(y, 0), yLen - 1)
            z = min(max(z, 0), zLen - 1)

            x_ratio = x / (xLen - 1) if xLen > 1 else 0
            y_ratio = y / (yLen - 1) if yLen > 1 else 0
            z_ratio = z / (zLen - 1) if zLen > 1 else 0

            plane_x.SetOrigin(xmin + x_ratio * (xmax - xmin), y0, z0)
            plane_y.SetOrigin(x0, ymin + y_ratio * (ymax - ymin), z0)
            plane_z.SetOrigin(x0, y0, zmin + z_ratio * (zmax - zmin))

            # VTK slice visibility
            if x_check:
                cutter_x.Update()
                mapper_x.Update()
                actor_x.SetVisibility(True)
            else:
                actor_x.SetVisibility(False)

            if y_check:
                cutter_y.Update()
                mapper_y.Update()
                actor_y.SetVisibility(True)
            else:
                actor_y.SetVisibility(False)

            if z_check:
                cutter_z.Update()
                mapper_z.Update()
                actor_z.SetVisibility(True)
            else:
                actor_z.SetVisibility(False)

            # 3D render
            plotter.render()

            # Matplotlib 2D slices update
            if x_check:
                img_x.set_data(cube.data3D[x, :, :])
                ax_x.set_title(f"X Slice @ {x}")
            else:
                img_x.set_data(np.zeros_like(cube.data3D[:, :, 0]))

            if y_check:
                img_y.set_data(cube.data3D[:, y, :])
                ax_y.set_title(f"Y Slice @ {y}")
            else:
                img_y.set_data(np.zeros_like(cube.data3D[:, 0, :]))

            if z_check:
                img_z.set_data(cube.data3D[:, :, z])
                ax_z.set_title(f"Z Slice @ {z}")
            else:
                img_z.set_data(np.zeros_like(cube.data3D[0, :, :]))

            with slice_output:
                clear_output(wait=True)
                fig.canvas.draw()
                display(fig)


        # Initial update call to set images and slices correctly
        update(
            x=gvWidgets.slice_x_slider.value,
            y=gvWidgets.slice_y_slider.value,
            z=gvWidgets.slice_z_slider.value,
            x_check=gvWidgets.slice_x_check.value,
            y_check=gvWidgets.slice_y_check.value,
            z_check=gvWidgets.slice_z_check.value,
        )

        # Hook up widgets
        out = widgets.interactive_output(update, {
            'x': gvWidgets.slice_x_slider,
            'y': gvWidgets.slice_y_slider,
            'z': gvWidgets.slice_z_slider,
            'x_check': gvWidgets.slice_x_check,
            'y_check': gvWidgets.slice_y_check,
            'z_check': gvWidgets.slice_z_check
        })
        display(out)
        meshes.plot_atoms_pyvista(cube = self.cube, plotter = plotter, origin = origin)
        # Launch PyVista
        pv.set_jupyter_backend('trame')
        plotter.show(jupyter_backend='client')
        plotter.ren_win.DoubleBufferOn()











   
   
   






       











