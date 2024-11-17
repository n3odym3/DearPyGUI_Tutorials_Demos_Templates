
import ctypes
import dearpygui.dearpygui as dpg

ctypes.windll.shcore.SetProcessDpiAwareness(2)
dpg.create_context()
dpg.create_viewport(title='Hello World', width=1920, height=1080)

from NeoDark_Theme import theme #The theme SHOULD BE imported after the context is created
dpg.bind_theme(theme)

class Main_win :
	def __init__(self):
		self.winID = "main_win"
		with dpg.window(tag=self.winID) as win_main:
			with dpg.menu_bar(): #Create a menu bar with debugging tools
				with dpg.menu(label="Tools") :
					dpg.add_menu_item(label="Show Debug", callback=lambda:dpg.show_tool(dpg.mvTool_Debug))
					dpg.add_menu_item(label="Show Font Manager", callback=lambda:dpg.show_tool(dpg.mvTool_Font))
					dpg.add_menu_item(label="Show Item Registry", callback=lambda:dpg.show_tool(dpg.mvTool_ItemRegistry))
					dpg.add_menu_item(label="Show Metrics", callback=lambda:dpg.show_tool(dpg.mvTool_Metrics))
					dpg.add_menu_item(label="Toggle Fullscreen", callback=lambda:dpg.toggle_viewport_fullscreen())

			with dpg.theme() as mainwin_theme: #Edit the main window theme to make the background darker
				with dpg.theme_component(dpg.mvAll):
					dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (20,20,25,255))
			dpg.bind_item_theme(win_main,mainwin_theme)
main_win = Main_win()

import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib
import seaborn as sns
import numpy as np
matplotlib.use('agg')


xdata1 = np.linspace(0, 100, 20) 
ydata1 = 1 - np.exp(-0.1 * xdata1)

xdata2 = np.linspace(0, 100, 20) 
ydata2 = 1 - np.exp(-0.05 * xdata2)

plot_win = None
class Plot_Win:
    def __init__(self):
        self.winID = "plot_win"
        self.plotID = "plot"
        self.anotID = "plot_anot"
        self.datawin1ID = "data_win1"
        self.datawin2ID = "data_win2"
        self.table1ID = "data1_table"
        self.table2ID = "data2_table"
        self.settingswinID = "plotsettings_win"
        self.plotanotcheckID = "plot_anot_check"
        self.selected_serie = None

        #Plot window
        with dpg.window(label="Plot", pos=(25,50),width=1200, height=900, show=True, tag=self.winID) :
            #Create an empty plot that will be filled by the plot_callback
            with dpg.group(horizontal=True):
                dpg.add_button(label="Plot settings", callback=lambda s,a: dpg.show_item(self.settingswinID))
                dpg.add_button(label="Plot", callback=self.plot_canvas)

            with dpg.plot(label="Line Series", height=-1, width=-1, tag=self.plotID):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, label="X", tag="x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, label="Y", tag="y_axis")
            #Edit the plot settings
            dpg.configure_item(self.plotID, anti_aliased=True)
            dpg.configure_item(self.plotID, crosshairs=True)

            #Add mouse handlers to the plot to automatically update the crop values when the user zooms in/out
            with dpg.handler_registry():
                dpg.add_mouse_move_handler(callback=self.plot_change_callback)
                dpg.add_mouse_wheel_handler(callback=self.plot_change_callback)
                dpg.add_mouse_drag_handler(callback=self.plot_change_callback, button=dpg.mvMouseButton_Left)
                dpg.add_mouse_drag_handler(callback=self.plot_change_callback, button=dpg.mvMouseButton_Right)

        #Plot Settings window (for the final matplotlib plot)
        with dpg.window(label="Plot Settings", pos=(50,50), tag=self.settingswinID, width=290, height=250, show=False) as win_plotsettings:
            with dpg.group(horizontal=True):
                dpg.add_text("Title ")
                dpg.add_input_text(tag="plot_title", default_value="Demo plot")

            dpg.add_input_float(label="L crop", tag="plot_leftcrop", default_value=-1)
            dpg.add_input_float(label="R crop", tag="plot_rightcrop", default_value=-1)
            dpg.add_input_float(label="U crop", tag="plot_upcrop", default_value=-1)
            dpg.add_input_float(label="D crop", tag="plot_downcrop", default_value=-1)

        #Data table 1
        with dpg.window(label="Data 1", tag= self.datawin1ID, pos=(1250,50), width=300, height = 900 , show=True) :
            dpg.add_button(label="Plot Data 1", width = -1, callback=lambda:self.plot(ydata1,xdata1, "Demo data 1"))
            with dpg.table(header_row=True, tag=self.table1ID):
                dpg.add_table_column(label="X")
                dpg.add_table_column(label="Y")
                
                # Add values to the table
                for i in range(len(xdata1)):
                    with dpg.table_row():
                        dpg.add_text(round(xdata1[i], 2))
                        dpg.add_text(round(ydata1[i], 2))
        
        #Data table 2
        with dpg.window(label="Data 2", tag= self.datawin2ID, pos=(1575,50), width=300, height = 900 , show=True) :
            dpg.add_button(label="Plot Data 2", width = -1, callback=lambda:self.plot(ydata2,xdata2, "Demo data 2"))
            with dpg.table(header_row=True, tag=self.table2ID):
                dpg.add_table_column(label="X")
                dpg.add_table_column(label="Y")
                
                # Add values to the table
                for i in range(len(xdata2)):
                    with dpg.table_row():
                        dpg.add_text(round(xdata2[i], 2))
                        dpg.add_text(round(ydata2[i], 2))

    def find_closest_point(self, mouse_x, mouse_y, x_data, y_data):
        """
        Finds the index of the closest point in the dataset to the given mouse coordinates.
        Parameters:
        mouse_x (float): The x-coordinate of the mouse position.
        mouse_y (float): The y-coordinate of the mouse position.
        x_data (numpy.ndarray): The array of x-coordinates of the data points.
        y_data (numpy.ndarray): The array of y-coordinates of the data points.
        Returns:
        int: The index of the closest data point to the given mouse coordinates.
        """
        x_min, x_max = x_data.min(), x_data.max()
        y_min, y_max = y_data.min(), y_data.max()

        x_data = (x_data - x_min) / (x_max - x_min)
        y_data = (y_data - y_min) / (y_max - y_min)
        mouse_x = (mouse_x - x_min) / (x_max - x_min)
        mouse_y = (mouse_y - y_min) / (y_max - y_min)

        distance = np.hypot(x_data - mouse_x, y_data - mouse_y)
        return np.argmin(distance)

    def select_serie(self, sender, app_data, user_data):
        """
        Handles the selection of a series.

        This method is triggered when a series is selected in the GUI. It updates
        the `selected_serie` attribute with the provided user data.

        Args:
            sender: The sender of the event.
            app_data: Additional data provided by the application.
            user_data: The data associated with the selected series.
        """
        self.selected_serie = user_data

    def plot_change_callback(self):
        """
        Callback function to handle changes in the plot.
        This function is triggered when there is a change in the plot and performs the following actions:
        - Checks if the plot and annotation items exist and if the plot is hovered.
        - Updates or deletes the existing annotation.
        - Retrieves the data series from the plot and finds the closest data point to the mouse position.
        - Adds a new annotation at the closest data point with the index, X, and Y values.
        - Updates the plot limits and sets the corresponding values for cropping.
        """
        if dpg.does_item_exist(self.plotID) and dpg.is_item_hovered(self.plotID) :

            if dpg.does_item_exist(self.anotID) : #Update the anotation
                dpg.delete_item(self.anotID)

            axis = dpg.get_item_children("y_axis", 1)
            if len(axis) > 0: #If there is a plot in the preview window
                if self.selected_serie is not None and dpg.does_item_exist(self.selected_serie) and dpg.get_item_type(self.selected_serie) == "mvAppItemType::mvLineSeries" :
                    plot = dpg.get_value(self.selected_serie) #Get the selected serie
                else :
                    plot = dpg.get_value(axis[0]) #Get the first serie by default
                xplot = plot[0] #get the X data
                yplot = plot[1] #get the Y data
                
                mouse_x, mouse_y = dpg.get_plot_mouse_pos() #get the mouse position
                point_index = self.find_closest_point(mouse_x, mouse_y, np.array(xplot), np.array(yplot)) #Find the closest point between the mouse and the plot

                annot = f"Index : {point_index}\nX : {xplot[point_index]}\nY : {yplot[point_index]}"
                dpg.add_plot_annotation(tag=self.anotID, label=annot, default_value=(xplot[point_index], yplot[point_index]), offset=(25, -25), color=[255, 255, 0, 255], parent=self.plotID)

            x_min, x_max = dpg.get_axis_limits("x_axis") #Get the current xlim (for matplotlib)
            y_min, y_max = dpg.get_axis_limits("y_axis") #Get the current ylim (for matplotlib)

            # # Update the matplotlib plot settings with the current preview plot scaling
            dpg.set_value("plot_leftcrop", x_min)
            dpg.set_value("plot_rightcrop", x_max)
            dpg.set_value("plot_upcrop", y_min)
            dpg.set_value("plot_downcrop", y_max)
    
    def plot(self, data, xdata=None, name=None):
        """
        Plots the given data on a DearPyGUI plot.
        Parameters:
            data (list): The y-axis data points to plot.
            xdata (list, optional): The x-axis data points. If None, a range of integers will be used. Defaults to None.
            name (str, optional): The name of the series. Defaults to None.
        """
        if xdata is None :
            xdata = list(range(len(data)))

        serie_name = f"plot_{name}"

        if dpg.does_item_exist(serie_name) :
            dpg.delete_item(serie_name)

        else :
            dpg.add_line_series(x=xdata, y=data, label=name, parent="y_axis", tag=serie_name)
            dpg.add_button(label="Select serie", user_data =dpg.last_item() , parent=dpg.last_item(), callback=self.select_serie)

            if len(dpg.get_item_children("y_axis")[1]) < 2 :
                dpg.fit_axis_data("x_axis")
                dpg.fit_axis_data("y_axis")
    
    def clear_plot(self):
        """
        Clears all line series from the plot.

        This method retrieves all children items of the y-axis and deletes those
        that are of type 'mvLineSeries'.
        """
        children = dpg.get_item_children("y_axis", 1)
        for child in children:
            if dpg.get_item_type(child) == "mvAppItemType::mvLineSeries":
                dpg.delete_item(child)

    def plot_canvas(self) :
        #Create the matplotlib plot
        fig = plt.figure(figsize=(11.69, 8.26), dpi=100)
        canvas = FigureCanvasAgg(fig)

        axis = dpg.get_item_children("y_axis", 1)
        for ax in axis:
            if dpg.get_item_type(ax) == "mvAppItemType::mvLineSeries" :
                plot = dpg.get_value(ax)
                label = dpg.get_item_label(ax)

                sns.lineplot(x=plot[0], y=plot[1], linewidth=3, label=label)

        #Edit the plot
        plt.title(dpg.get_value("plot_title"))
        plt.xlim(dpg.get_value("plot_leftcrop"), dpg.get_value("plot_rightcrop"))
        plt.ylim(dpg.get_value("plot_upcrop"), dpg.get_value("plot_downcrop"))

        #Draw the plot and convert it to an image buffer
        canvas.draw()
        buf = canvas.buffer_rgba()
        image = np.asarray(buf)

        #Redraw the Matplotlib window if needed
        if dpg.does_item_exist("matplotlib_win"):
            dpg.delete_item("matplotlib_win")
            dpg.delete_item("plot_texture")
        
        #Send the image to the Matplotlib window of DPG
        image = image.astype(np.float32) / 255
        with dpg.texture_registry():
            dpg.add_raw_texture(1169, 826, image, format=dpg.mvFormat_Float_rgba, tag="plot_texture")

        with dpg.window(label="MatPlotLib", pos=(325,50),width=1200, height=900,tag="matplotlib_win"):
            dpg.add_image("plot_texture")

plot_win = Plot_Win()


dpg.setup_dearpygui()
dpg.set_primary_window("main_win", True)
dpg.show_viewport()
while dpg.is_dearpygui_running():
	dpg.render_dearpygui_frame()
dpg.destroy_context()
