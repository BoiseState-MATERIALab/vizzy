import os
from cube_viskit import Cube
import ipywidgets as widgets
import pyvista as pv
import ipyvolume as ipv
from IPython.display import display
from gv_ui import gvWidgets
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

    import vtk

    def display_cell_slices_pyvista_style(self):
        cube = self.cube

        # Get grid and geometry
        grid, a_vec, b_vec, c_vec, origin = self.display_cell_pyvista_style()
        vtk_data = grid  # Get underlying vtkStructuredGrid object

        xmin, xmax, ymin, ymax, zmin, zmax = grid.bounds

        # Setup plotter
        plotter = pv.Plotter()
        plotter.set_background("white")

        # Add isosurface as before
        surface = grid.threshold(value=0.1)
        plotter.add_mesh(surface, cmap="reds", opacity=0.5)

        # Add bounding box lines (same as before)
        corners = [
            origin,
            origin + a_vec,
            origin + b_vec,
            origin + c_vec,
            origin + a_vec + b_vec,
            origin + a_vec + c_vec,
            origin + b_vec + c_vec,
            origin + a_vec + b_vec + c_vec
        ]
        edges = [
            (0, 1), (0, 2), (0, 3),
            (1, 4), (1, 5),
            (2, 4), (2, 6),
            (3, 5), (3, 6),
            (4, 7), (5, 7), (6, 7)
        ]
        for i, j in edges:
            line = pv.Line(corners[i], corners[j])
            plotter.add_mesh(line, color="black", line_width=1)

        xLen = len(cube.data3D[0][0])
        yLen = len(cube.data3D[0])
        zLen = len(cube.data3D)

        gvWidgets.slice_x_slider.max = xLen - 1
        gvWidgets.slice_y_slider.max = yLen - 1
        gvWidgets.slice_z_slider.max = zLen - 1

        # Initial slice origins (middle)
        x0 = 0.5 * (xmin + xmax)
        y0 = 0.5 * (ymin + ymax)
        z0 = 0.5 * (zmin + zmax)

        # --- SETUP VTK CUTTERS FOR X, Y, Z slices ONCE ---

        # Create vtkPlanes for slicing
        plane_x = vtk.vtkPlane()
        plane_x.SetNormal(1, 0, 0)
        plane_x.SetOrigin(x0, 0, 0)

        plane_y = vtk.vtkPlane()
        plane_y.SetNormal(0, 1, 0)
        plane_y.SetOrigin(0, y0, 0)

        plane_z = vtk.vtkPlane()
        plane_z.SetNormal(0, 0, 1)
        plane_z.SetOrigin(0, 0, z0)

        # Create vtkCutter for each plane
        cutter_x = vtk.vtkCutter()
        cutter_x.SetCutFunction(plane_x)
        cutter_x.SetInputData(vtk_data)
        cutter_x.Update()

        cutter_y = vtk.vtkCutter()
        cutter_y.SetCutFunction(plane_y)
        cutter_y.SetInputData(vtk_data)
        cutter_y.Update()

        cutter_z = vtk.vtkCutter()
        cutter_z.SetCutFunction(plane_z)
        cutter_z.SetInputData(vtk_data)
        cutter_z.Update()

        # Build mappers and actors once
        # Create slice actors dictionary in enclosing scope
        slice_actors = {}
        # Add initial slice actors
        slice_actors = {
            "x": plotter.add_mesh(pv.wrap(cutter_x.GetOutput()), color="black", opacity=0.5),
            "y": plotter.add_mesh(pv.wrap(cutter_y.GetOutput()), color="black", opacity=0.5),
            "z": plotter.add_mesh(pv.wrap(cutter_z.GetOutput()), color="black", opacity=0.5)
        }
        mapper_x = vtk.vtkPolyDataMapper()
        mapper_x.SetInputConnection(cutter_x.GetOutputPort())
        actor_x = vtk.vtkActor()
        actor_x.SetMapper(mapper_x)
        actor_x.GetProperty().SetColor(0, 0, 0)
        actor_x.GetProperty().SetOpacity(0.5)
        plotter.renderer.AddActor(actor_x)

        mapper_y = vtk.vtkPolyDataMapper()
        mapper_y.SetInputConnection(cutter_y.GetOutputPort())
        actor_y = vtk.vtkActor()
        actor_y.SetMapper(mapper_y)
        actor_y.GetProperty().SetColor(0, 0, 0)
        actor_y.GetProperty().SetOpacity(0.5)
        plotter.renderer.AddActor(actor_y)

        mapper_z = vtk.vtkPolyDataMapper()
        mapper_z.SetInputConnection(cutter_z.GetOutputPort())
        actor_z = vtk.vtkActor()
        actor_z.SetMapper(mapper_z)
        actor_z.GetProperty().SetColor(0, 0, 0)
        actor_z.GetProperty().SetOpacity(0.5)
        plotter.renderer.AddActor(actor_z)
        
        # --- UPDATE FUNCTION using VTK plane origins ---
        def update(x=0, y=0, z=0):
            x_ratio = x / (xLen - 1) if xLen > 1 else 0
            y_ratio = y / (yLen - 1) if yLen > 1 else 0
            z_ratio = z / (zLen - 1) if zLen > 1 else 0

            new_x = xmin + x_ratio * (xmax - xmin)
            new_y = ymin + y_ratio * (ymax - ymin)
            new_z = zmin + z_ratio * (zmax - zmin)

            # Update plane origins
            plane_x.SetOrigin(new_x, 0, 0)
            plane_y.SetOrigin(0, new_y, 0)
            plane_z.SetOrigin(0, 0, new_z)

            # Update cutters
            cutter_x.Update()
            cutter_y.Update()
            cutter_z.Update()

            # Update actors with new geometry
            for axis, cutter in zip(["x", "y", "z"], [cutter_x, cutter_y, cutter_z]):
                mapper = slice_actors[axis].GetMapper()
                mapper.SetInputData(pv.wrap(cutter.GetOutput()))
                mapper.Update()

            plotter.render()

        out = widgets.interactive_output(update, {
            'x': gvWidgets.slice_x_slider,
            'y': gvWidgets.slice_y_slider,
            'z': gvWidgets.slice_z_slider
        })
        display(out)

        pv.set_jupyter_backend('trame')
        plotter.show()



    
    
    



        



