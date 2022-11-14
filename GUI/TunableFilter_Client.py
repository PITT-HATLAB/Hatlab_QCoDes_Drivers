#!/usr/bin/env python3

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
#----------------------------------------------------------------------------------------------------#
# Import Packages

#--------------------------------------------------#
# System Packages

import sys
import ctypes
import pathlib
apppath=pathlib.Path(__file__).parent.resolve()
appid = u'toolsforexperiments.TunableFilter.1.0.0' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
# System Packages
#--------------------------------------------------#
# Customization Packages
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QSlider, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QWidget	# Slider package and widget auto arrangement package
from PyQt5.QtCore import Qt	# Name space
from PyQt5 import QtGui

import matplotlib.pyplot as plt	# Plotting package
plt.ioff()	# Turn the interactive mode off (so that it doesn't show plots without the "show" command)
import numpy as np	# Numpy package
import random
import h5py

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas	# Provides canvas for the graph
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar	# Provides navigation tool bar

# Customization Packages
#--------------------------------------------------#
# Filter Packages

from Hatlab_QCoDes_Drivers.AnalogDevices_ADMV8818 import AnalogDevices_ADMV8818
from instrumentserver.client import Client
# Filter Packages
#--------------------------------------------------#

# Import Packages
#----------------------------------------------------------------------------------------------------#
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
#----------------------------------------------------------------------------------------------------#
# Global File Path

"""
This is the general format for the data path used by the "get" button, to represent specific file path, format this path with the "serial_number".
"""

DATAPATH = r"L:\Data\00_Calibrations\RT Equipment calibrations\ADMV8818_Filters\{}\\"

# Global File Path
#----------------------------------------------------------------------------------------------------#
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
#----------------------------------------------------------------------------------------------------#
# The "Main_Window" Class
cli = Client()

def getFilters():
	instruments = cli.list_instruments()
	Serial_Number_list = []
	filter_dict = {}
	for name, driver in instruments.items():
		if driver == AnalogDevices_ADMV8818:
			inst = cli.get_instrument(name)
			Id = inst.IDN()["hardwareID"].split("&")
			Serial_Number = Id[2]
			Serial_Number_list.append(Serial_Number)
			filter_dict[Serial_Number] = inst
	return Serial_Number_list, filter_dict


class Main_Window(QMainWindow):
	#----------------------------------------------------------------------------------------------------#
	#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
	#----------------------------------------------------------------------------------------------------#
	# "__init__()"
	
	def __init__(self):
		super().__init__()	# Inherit all functionality from QMainWindow
		
		self.setWindowTitle("Filter Control")	# Set window title
		self.setFixedWidth(1000)		# "win.setGeometry(x,y,width,height)"	# Top left corner: (x,y) = (0,0)
		self.setWindowIcon(QtGui.QIcon(str(apppath) + '\\icons\\TunableFilter.ico'))
		# --------------------------------------------------#
		# Get Filter Serial Numbers and proxies
		Serial_Number_list, self.filter_dict = getFilters()

		# Get Filter Serial Numbers and proxies
		# --------------------------------------------------#

		widget_list = []

		for Serial_Number in Serial_Number_list:
			widget_list.append(self.Widget(Serial_Number))

		self.setFixedHeight(300 * len(widget_list))
		self.Append_Widgets_to_Window(widget_list)
	
	# "__init__()"
	#----------------------------------------------------------------------------------------------------#
	#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
	#----------------------------------------------------------------------------------------------------#
	# The "Widget" Function
	
	"""
	The "Widget" Function generates a Graph-ControlPanel pair
	"""
	
	def Widget(self, Serial_Number):
		#--------------------------------------------------#
		# Slider & Label 1 (High Pass Filter Switch)
		
		max_val = 4
		
		label = "High Pass Filter Switch\n[0-{}]"
		label = label.format(max_val)
		
		label_1 = QLabel(label)
		slider_1 = self.Make_Slider(range = max_val)
		High_Pass_Filter_Switch = self.Make_Value()
		
		self.Connect(slider = slider_1, line_edit = High_Pass_Filter_Switch, max_val = max_val)
		
		# Slider & Label 1 (High Pass Filter Switch)
		#--------------------------------------------------#
		# Slider & Label 2 (High Pass Filter Register)
		
		max_val = 15
		
		label = "High Pass Filter Register\n[0-{}]"
		label = label.format(max_val)
		
		label_2 = QLabel(label)
		slider_2 = self.Make_Slider(range = max_val)
		High_Pass_Filter_Register = self.Make_Value()
		
		self.Connect(slider = slider_2, line_edit = High_Pass_Filter_Register, max_val = max_val)
		
		# Slider & Label 2 (High Pass Filter Register)
		#--------------------------------------------------#
		# Slider & Label 3 (Low Pass Filter Switch)
		
		max_val = 4
		
		label = "Low Pass Filter Switch\n[0-{}]"
		label = label.format(max_val)
		
		label_3 = QLabel(label)
		slider_3 = self.Make_Slider(range = max_val)
		Low_Pass_Filter_Switch = self.Make_Value()
		
		self.Connect(slider = slider_3, line_edit = Low_Pass_Filter_Switch, max_val = max_val)
		
		# Slider & Label 3 (Low Pass Filter Switch)
		#--------------------------------------------------#
		# Slider & Label 4 (Low Pass Filter Register)
		
		max_val = 15
		
		label = "Low Pass Filter Register\n[0-{}]"
		label = label.format(max_val)
		
		label_4 = QLabel(label)
		slider_4 = self.Make_Slider(range = max_val)
		Low_Pass_Filter_Register = self.Make_Value()
		
		self.Connect(slider = slider_4, line_edit = Low_Pass_Filter_Register, max_val = max_val)
		
		# Slider & Label 4 (Low Pass Filter Register)
		#--------------------------------------------------#
		# Buttons
		
		get_button = QPushButton("Get")
		set_button = QPushButton("Set")
		
		buttons_group = self.Buttons_Group(get_button,set_button)
		
		# Buttons
		#--------------------------------------------------#
		# Plot
		
		"""
		Make a canvas and draw on it.
		"""
		
		plt.style.use('seaborn-whitegrid')	# Set plot style
		
		fig = plt.figure()	# Make a figure
		canvas = FigureCanvas(fig)	# Append the figure to canvas
		ax, blue_curve, grey_curve = self.Clear_Figure(Serial_Number, fig)	# Set up a blank figure to draw on
		
		get_button.clicked.connect(lambda: self.Get_Blue_Curve(ax, blue_curve, canvas, High_Pass_Filter_Switch, High_Pass_Filter_Register, Low_Pass_Filter_Switch, Low_Pass_Filter_Register, Serial_Number))
		set_button.clicked.connect(lambda: 
			self.Set_Blue_Curve(ax, blue_curve, canvas, High_Pass_Filter_Switch, High_Pass_Filter_Register, Low_Pass_Filter_Switch, Low_Pass_Filter_Register, Serial_Number))
		
		High_Pass_Filter_Switch.textChanged.connect(lambda:
			self.Draw_Grey_Curve(ax, grey_curve, canvas, High_Pass_Filter_Switch, High_Pass_Filter_Register, Low_Pass_Filter_Switch, Low_Pass_Filter_Register, Serial_Number))	# Connect High_Pass_Filter_Switch to Grey Curve
		High_Pass_Filter_Register.textChanged.connect(lambda:
			self.Draw_Grey_Curve(ax, grey_curve, canvas, High_Pass_Filter_Switch, High_Pass_Filter_Register, Low_Pass_Filter_Switch, Low_Pass_Filter_Register, Serial_Number))	# Connect High_Pass_Filter_Register to Grey Curve
		Low_Pass_Filter_Switch.textChanged.connect(lambda:
			self.Draw_Grey_Curve(ax, grey_curve, canvas, High_Pass_Filter_Switch, High_Pass_Filter_Register, Low_Pass_Filter_Switch, Low_Pass_Filter_Register, Serial_Number))	# Connect Low_Pass_Filter_Switch to Grey Curve
		Low_Pass_Filter_Register.textChanged.connect(lambda:
			self.Draw_Grey_Curve(ax, grey_curve, canvas, High_Pass_Filter_Switch, High_Pass_Filter_Register, Low_Pass_Filter_Switch, Low_Pass_Filter_Register, Serial_Number))	# Connect Low_Pass_Filter_Register to Grey Curve

		toolbar = NavigationToolbar(canvas , self)	# Create a toolbar for given canvas

		ToolBarCanvas = QVBoxLayout()	# Create a vertical layout with toolbar and canvas
		ToolBarCanvas.addWidget(toolbar)
		ToolBarCanvas.addWidget(canvas)

		# Plot
		#--------------------------------------------------#
		# Horizontal Layouts
		
		"""
		Group sliders to values.
		"""
		
		slider_group_1 = self.Slider_Group(label = label_1 , slider = slider_1 , line_edit = High_Pass_Filter_Switch)
		slider_group_2 = self.Slider_Group(label = label_2 , slider = slider_2 , line_edit = High_Pass_Filter_Register)
		slider_group_3 = self.Slider_Group(label = label_3 , slider = slider_3 , line_edit = Low_Pass_Filter_Switch)
		slider_group_4 = self.Slider_Group(label = label_4 , slider = slider_4 , line_edit = Low_Pass_Filter_Register)
		
		# Horizontal Layouts
		#--------------------------------------------------#
		# Nested Layout
		
		"""
		Nest the horizontal layouts for sliders into the vertical layout;
		And then nest the vertical layout into the horizontal layout of the Canvas-ControlPanel pair.
		"""
		
		control_panel = self.Controls_Panel_Vertical_Group(slider_group_1,slider_group_2,slider_group_3,slider_group_4,buttons_group)

		Horizontal_layout = QHBoxLayout()  # The Horizontal layout of the entire widget (Graph-ControlPanel Pair)
		Horizontal_layout.addLayout(ToolBarCanvas)		# Append canvas to widget
		Horizontal_layout.addLayout(control_panel)		# Append the vertical layout to the Horizontal layout
		
		self.widget = QWidget()	# Create a widget
		self.widget.setLayout(Horizontal_layout)	# Set the Horizontal layout to the widget
		
		# Nested Layout
		#--------------------------------------------------#
		# Create Widget
		
		"""
		Append the Horizontal layout to the window as a widget.
		"""
		
		Widget = QWidget()	# Create a Widget composed of stackable widgets
		Widget.setLayout(Horizontal_layout)	# Set the Graph-ControlPanel Pair as one widget
		
		return Widget
		
		# Create Widget
		#--------------------------------------------------#
		
	# # The "Widget" Function
	#----------------------------------------------------------------------------------------------------#
	#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
	#----------------------------------------------------------------------------------------------------#
	# Make Widgets
	
	#--------------------------------------------------#
	# Make Slider
		
	def Make_Slider(self,range):
		
		slider = QSlider(Qt.Horizontal, self)
		slider.setRange(0, range)
		slider.setFocusPolicy(Qt.NoFocus)
		slider.setPageStep(1)
		slider.setFixedWidth(125)
		
		return slider
	
	# Make Slider
	#--------------------------------------------------#
	# Make Value
	
	def Make_Value(self):
		
		value = QLineEdit('0', self)
		value.setFixedWidth(25)
		
		return value
	
	# Make Value
	#--------------------------------------------------#
	
	# Make Widgets
	#----------------------------------------------------------------------------------------------------#
	#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
	#----------------------------------------------------------------------------------------------------#
	# Connect Widgets
	
	#--------------------------------------------------#
	# Connect
	
	def Connect(self,slider,line_edit,max_val):
		
		slider.valueChanged.connect(lambda: self.Update_Value(slider = slider , line_edit = line_edit))	# Connect slider to value
		line_edit.textChanged.connect(lambda: self.Update_Slider(slider = slider , line_edit = line_edit , max_val = max_val))	# Connect value to slider
	
	# Connect
	#--------------------------------------------------#
	# "Update_Value()" Function
		
	"""
	This function gets the values from the sliders and display it on the boxes to the right.
	"""
		
	def Update_Value(self, slider, line_edit):
		slider_value = slider.value()
		line_edit.setText(str(slider_value))
		
	# "Update_Value()" Function
	#--------------------------------------------------#
	# "Update_Slider()" Function
		
	"""
	This function check the value inside the box and use it to reposition the sliders.
	"""
		
	def Update_Slider(self, slider, line_edit, max_val):
		
		try:	# Check the magnitude if the user entered a number
		
			box_value = int(line_edit.text())	# Read the value in the box (if the user changed it)
		
			#--------------------------------------------------#
			# Inspect the magnitude of the numbers in the box
		
			if box_value > max_val:
				box_value = max_val
				
			# Inspect the magnitude of the numbers in the box
			#--------------------------------------------------#
				
			slider.setValue(box_value)	# Set the slider value to the value after inspection
			line_edit.setText(str(box_value))	# Set the box value to the value after inspection
		
		except:	# Dealing with characters that are not numbers
		
			#--------------------------------------------------#
			# Understand the "" character
		
			try:		# Check if the value inside the box is the "" character (This happens when user deletes the character inside the box)
		
				if line_edit.text() == "":	# if the character inside the box is "", take it as '0'
					box_value = 0
		
				slider.setValue(box_value)	# Set the slider value to the value after inspection
				line_edit.setText(str(box_value))	# Set the box value to the value after inspection
		
			# Understand the "" character
			#--------------------------------------------------#
		
			except:	# If the character inside the box is neither a number nor the "" character, then ignore the user input
		
				slider_value = slider.value()	# Get the slider value
				line_edit.setText(str(slider_value))	# Set the box value to the slider value
		
	# "Update_Slider()" Function
	#--------------------------------------------------#
	
	# Connect Widgets
	#----------------------------------------------------------------------------------------------------#
	#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
	#----------------------------------------------------------------------------------------------------#
	# Figure and Canvas
		
	#--------------------------------------------------#
	# Clear Figure
		
	"""
	Clear_Figure for the given fig, returns the axes of the plot, the blue_curve, and the grey_curve
	"""
		
	def Clear_Figure(self, Serial_Number, fig):
		
		fig.clear()
		ax = fig.add_subplot(1,1,1)	 # "1x1 grid, 1st subplot"
		plt.title(Serial_Number)		# Set plot title
		
		blue_curve = ax.plot([],[],'b',linewidth=1)
		grey_curve = ax.plot([],[],'0.8',linewidth=3)
		ax.set_xlabel("Frequency (GHz)")
		ax.set_ylabel("Amplitude (dB)")
		
		return ax, blue_curve, grey_curve
	
	# Clear Figure
	#--------------------------------------------------#
	# Get Blue Curve

	"""
	Get the data from the file path of the given Serial_Number
	"""
	
	def Get_Blue_Curve(self, ax, blue_curve, canvas, value_1, value_2, value_3, value_4, Serial_Number):

		filter = self.filter_dict[Serial_Number]

		High_Pass_Filter_Switch = filter.get_HPF_setting()[0]  # Get the values for blue curve
		High_Pass_Filter_Register = filter.get_HPF_setting()[1]
		Low_Pass_Filter_Switch = filter.get_LPF_setting()[0]
		Low_Pass_Filter_Register = filter.get_LPF_setting()[1]

		data_path = DATAPATH.format(Serial_Number)

		frequency, magnitude = readData(data_path, [High_Pass_Filter_Switch, High_Pass_Filter_Register],
										[Low_Pass_Filter_Switch, Low_Pass_Filter_Register])

		blue_curve.pop(0).remove()  # Remove the given blue_curve

		blue_curve.append(
			ax.plot(frequency/1e9, magnitude, 'b', linewidth=1)[0])  # Draw the new blue_curve on the given figure
		canvas.draw()  # Append the new figure to the given canvas
		
	# Get Blue Curve
	#--------------------------------------------------#
	# Set Blue Curve
		
	def Set_Blue_Curve(self, ax, blue_curve, canvas, value_1, value_2, value_3, value_4, Serial_Number):

		High_Pass_Filter_Switch = value_1.text()  # Get the values for blue curve
		High_Pass_Filter_Register = value_2.text()
		Low_Pass_Filter_Switch = value_3.text()
		Low_Pass_Filter_Register = value_4.text()

		data_path = DATAPATH.format(Serial_Number)

		frequency, magnitude = readData(data_path, [High_Pass_Filter_Switch, High_Pass_Filter_Register],
										[Low_Pass_Filter_Switch, Low_Pass_Filter_Register])
		
		blue_curve.pop(0).remove()	# Remove the given blue_curve

		blue_curve.append(ax.plot(frequency/1e9,magnitude,'b',linewidth=1)[0])	# Draw the new blue_curve on the given figure
		canvas.draw()	# Append the new figure to the given canvas

		filter = self.filter_dict[Serial_Number]

		filter.set_HPF_setting([int(High_Pass_Filter_Switch), int(High_Pass_Filter_Register)])
		filter.set_LPF_setting([int(Low_Pass_Filter_Switch), int(Low_Pass_Filter_Register)])
		
	# Set Blue Curve
	#--------------------------------------------------#
	# Draw Grey Curve
		
	def Draw_Grey_Curve(self, ax, grey_curve, canvas, value_1, value_2, value_3, value_4, Serial_Number):

		High_Pass_Filter_Switch = value_1.text()  # Get the values for grey curve
		High_Pass_Filter_Register = value_2.text()
		Low_Pass_Filter_Switch = value_3.text()
		Low_Pass_Filter_Register = value_4.text()

		data_path = DATAPATH.format(Serial_Number)

		frequency, magnitude = readData(data_path, [High_Pass_Filter_Switch, High_Pass_Filter_Register],
										[Low_Pass_Filter_Switch, Low_Pass_Filter_Register])

		grey_curve.pop(0).remove()  # Remove the given grey_curve

		grey_curve.append(ax.plot(frequency/1e9, magnitude, '0.8', linewidth=3)[0])  # Draw the new blue_curve on the given figure
		canvas.draw()  # Append the new figure to the given canvas
		
	# Draw Grey Curve
	#--------------------------------------------------#
		
	# Figure and Canvas
	#----------------------------------------------------------------------------------------------------#
	#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
	#----------------------------------------------------------------------------------------------------#
	# Layout
	
	#--------------------------------------------------#
	# Slider_Group (Horizontal Layout)
	
	def Slider_Group(self,label,slider,line_edit):
		
		horizontal_layout = QHBoxLayout()
		horizontal_layout.addWidget(label)
		horizontal_layout.addWidget(slider)
		horizontal_layout.addSpacing(15)
		horizontal_layout.addWidget(line_edit)
		
		return horizontal_layout
	
	# Slider_Group (Horizontal Layout)
	#--------------------------------------------------#
	# Buttons_Group (Horizontal Layout)
	
	def Buttons_Group(self,button_1,button_2):
		
		horizontal_layout = QHBoxLayout()
		horizontal_layout.addWidget(button_1)
		horizontal_layout.addWidget(button_2)
		
		return horizontal_layout
	
	# Buttons_Group (Horizontal Layout)
	#--------------------------------------------------#
	# Controls_Panel_Vertical_Group
	
	def Controls_Panel_Vertical_Group(self,layout1,layout2,layout3,layout4,layout5):
		
		vertical_layout = QVBoxLayout()
		vertical_layout.addLayout(layout1)
		vertical_layout.addLayout(layout2)
		vertical_layout.addLayout(layout3)
		vertical_layout.addLayout(layout4)
		vertical_layout.addLayout(layout5)
		
		return vertical_layout
	
	# Controls_Panel_Vertical_Group
	#--------------------------------------------------#
	# Append Widgets to Window
	
	def Append_Widgets_to_Window (self,widget_list):
		
		Window_Layout = QVBoxLayout()
		
		for i in widget_list:
			Window_Layout.addWidget(i)
		
		Widget = QWidget()
		Widget.setLayout(Window_Layout)
		
		self.setCentralWidget(Widget)	# Append Widget to the window
		
	# Append Widgets to Window
	#--------------------------------------------------#
	
	# Layout
	#----------------------------------------------------------------------------------------------------#
	#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
	#----------------------------------------------------------------------------------------------------#

# The "Main_Window" Class
#----------------------------------------------------------------------------------------------------#
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
#----------------------------------------------------------------------------------------------------#
# Read from Filter

#--------------------------------------------------#
# "readData" Function

def readData(filePath, HPF_setting, LPF_setting):
	fileName = dataFileName(HPF_setting, LPF_setting)
	f = h5py.File(filePath + fileName, "r")
	freq = f["freq"][()]
	mag = f["mag"][()]
	return  freq, mag

# "readData" Function
#--------------------------------------------------#
# "dataFileName" Function

def dataFileName(HPF_setting, LPF_setting):
	return  f"HPF{HPF_setting[0]}_{HPF_setting[1]}_LPF{LPF_setting[0]}_{LPF_setting[1]}"

# "dataFileName" Function
#--------------------------------------------------#

# Read from Filter
#----------------------------------------------------------------------------------------------------#
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
#----------------------------------------------------------------------------------------------------#

# Execute the Application

#--------------------------------------------------#
# Create an Instance with "QApplication" Class
		
app = QApplication(sys.argv)	

# Create an Instance with "QApplication" Class
#--------------------------------------------------#
# Generate the Window

window = Main_Window()	# Create a window with the "Main_Window" class
window.show()	# Show the window

# Generate the Window
#--------------------------------------------------#
# Execute the Instance

app.exec()	# Starts the event loop

# Execute the Instance
#--------------------------------------------------#

# Execute the Application
#----------------------------------------------------------------------------------------------------#
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#