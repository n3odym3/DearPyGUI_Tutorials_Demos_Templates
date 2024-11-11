
import ctypes
import dearpygui.dearpygui as dpg

ctypes.windll.shcore.SetProcessDpiAwareness(2)

dpg.create_context()
dpg.create_viewport(title='Hello World', width=1280, height=720)

from NeoDark_Theme import theme #The theme SHOULD BE imported after the context is created
dpg.bind_theme(theme)

class Main_win :
	def __init__(self):
		self.winID = "main_win"
		with dpg.window(tag=self.winID) as win_main:
			#Create a menu bar with debugging tools
			with dpg.menu_bar(): 
				with dpg.menu(label="Tools") :
					dpg.add_menu_item(label="Show Debug", callback=lambda:dpg.show_tool(dpg.mvTool_Debug))
					dpg.add_menu_item(label="Show Font Manager", callback=lambda:dpg.show_tool(dpg.mvTool_Font))
					dpg.add_menu_item(label="Show Item Registry", callback=lambda:dpg.show_tool(dpg.mvTool_ItemRegistry))
					dpg.add_menu_item(label="Show Metrics", callback=lambda:dpg.show_tool(dpg.mvTool_Metrics))
					dpg.add_menu_item(label="Toggle Fullscreen", callback=lambda:dpg.toggle_viewport_fullscreen())
					dpg.add_menu_item(label="Hello World", callback=self.create_hello_world)
					dpg.add_menu_item(label="Reopen all windows", callback=self.reopen_all_win)

			#Edit the main window theme to make the background darker
			with dpg.theme() as mainwin_theme: 
				with dpg.theme_component(dpg.mvAll):
					dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (20,20,25,255))
			dpg.bind_item_theme(win_main,mainwin_theme)

	def create_hello_world(self):
		hello = Hello_World()
	
	def reopen_all_win(self):
		all_items = dpg.get_all_items()
		
		for item in all_items:
			if dpg.get_item_type(item) == "mvAppItemType::mvWindowAppItem":
				dpg.configure_item(item, show=True)

main_win = Main_win()

class Hello_World:
	def __init__(self, name = ""):
		self.winID = "Hello_World_win_" + str(dpg.generate_uuid())
		with dpg.window(tag=self.winID, pos=(50,50), width=-1, label="Hello World window " + str(name)) :
			dpg.add_text("Hello, World!")
			dpg.add_button(label="Kill window",width=-1, callback=lambda:dpg.delete_item(self.winID))

hello_world_win = Hello_World(1)
hello_world_win2 = Hello_World(2)

dpg.setup_dearpygui()
dpg.set_primary_window("main_win", True)
dpg.show_viewport()

while dpg.is_dearpygui_running():
	dpg.render_dearpygui_frame()

dpg.destroy_context()



