from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QListWidget, QSpinBox
from PyQt5 import uic
import sys, json

class QTWindow(QMainWindow):
	ui_filename = 'horo_info.ui'
	ui_title    = 'Minecraft events helper'

	def __init__(self):
		super().__init__()
		uic.loadUi	   (self.ui_filename, self)
		self.setWindowTitle(self.ui_title)

		self.config_file_name 			= 'config.json'
		self.config 	  			= {}

		self.interval				= 36
		self.start_delay 			= 2
		self.day 				= 1

		self.after_days 			= 0
		self.on_day 				= 0
		self.total_events 			= 0
		self.another_events 			= 0
		self.event_today 			= False
		self.events 				= []

		self.data_sboxes = {
			'sbox_day'			: 'day',
			'sbox_start_delay'		: 'start_delay',
			'sbox_interval'			: 'interval',
			'sbox_another_events'		: 'another_events'
		}
		self.data_labels = {
			'label_after_days' 	 	: 'after_days',
			'label_on_day' 		 	: 'on_day',
			'label_total_events' 		: 'total_events'
		}

		self.start()

	def start(self):

		self.read_config()
		self.init_signals()
		self.label_events_today.show() if self.event_today else self.label_events_today.hide()


	def init_signals(self):

		for sbox_name in self.data_sboxes.keys():
			getattr(self, sbox_name).valueChanged.connect(self.value_changed)


	def read_config(self):

		try:
			with open(self.config_file_name, 'r', encoding='utf-8') as f:
				self.config = json.load(f)
		except Exception as e:
			print(e)

		for key, value in self.config.items():
			if hasattr(self, key) and value is not None:
				setattr(self, key, value)

		self.set_config_values()


	def save_config(self):

		keys_to_save = [key for key in self.config.keys() if hasattr(self, key)]
		data = {key: getattr(self, key) for key in keys_to_save}

		try:
			with open(self.config_file_name, 'w', encoding='utf-8') as f:
				json.dump(data, f, ensure_ascii=False, indent=4)
		except Exception as e:
			print(e)


	def set_config_values(self):

		self.update_labels_values()

		for sbox_name, attr_name in self.data_sboxes.items():
			getattr(self, sbox_name).setValue(getattr(self, attr_name))

		for day in self.events:
			self.list_widget_another_events.addItem(str(day))


	def value_changed(self):

		self.set_values()
		self.save_config()


	def update_labels_values(self):

		for label_name, attr_name in self.data_labels.items():
			value = getattr(self, attr_name)
			getattr(self, label_name).setText(str(value))

		self.label_events_today.show() if self.event_today else self.label_events_today.hide()


	def set_values(self):

		self.day 	 = self.sbox_day.value()
		self.start_delay = self.sbox_start_delay.value()
		self.interval  	 = self.sbox_interval.value()

		first_event_day  = self.interval + self.start_delay

		if self.day < first_event_day:
			self.after_days 	= first_event_day - self.day
			self.total_events 	= 0
		else:
			days_since_first_event = self.day - first_event_day
			self.total_events = days_since_first_event // self.interval + 1
			self.after_days = self.interval - (days_since_first_event % self.interval)
			if self.after_days == self.interval:
				self.after_days = 0

		self.on_day = self.day + self.after_days
		self.event_today = True if self.after_days == 0 else False

		self.update_labels_values()
		self.update_events_list()


	def update_events_list(self):

		self.another_events = self.sbox_another_events.value()
		new_events 	    = self.return_events_list(self.another_events)
		prev_events 	    = self.events

		if set(new_events) != set(prev_events):
			self.list_widget_another_events.clear()
			for event in new_events:
				self.list_widget_another_events.addItem(str(event))
			self.events = new_events


	def return_events_list(self, another_events):

		new_events = []
		event 	   = self.on_day

		for i in range(self.another_events):
			new_events.append(event)
			event += self.interval
		return new_events



if __name__ == '__main__':
	app     = QApplication(sys.argv)
	window  = QTWindow()
	window.show()
	sys.exit(app.exec_())
