from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivymd.uix.button import MDRaisedButton
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import requests
import mysql.connector
from mysql.connector import Error
import json
from kivy.uix.popup import Popup


class CustomScreen(Screen):
    def __init__(self, **kwargs):
        super(CustomScreen, self).__init__(**kwargs)
        # Set the background image
        self.add_widget(Image(source="/home/hadeel/Desktop/mock/com.png", allow_stretch=True, keep_ratio=False))

        # Add your UI elements on top of the background
        layout = FloatLayout(size=(300, 500))
        self.phone_number_input = TextInput(hint_text='Phone Number', size_hint=(.8, .07), pos_hint={'x': .1, 'y': .6})
        self.amount_input = TextInput(hint_text='Amount to Add', size_hint=(.8, .07), pos_hint={'x': .1, 'y': .5})
        charge_account_btn = Button(text='Charge Account', size_hint=(.8, .1), pos_hint={'x': .1, 'y': .25})
        charge_account_btn.bind(on_press=self.charge_account)

        check_account_btn = Button(text='Check Account', size_hint=(.8, .1), pos_hint={'x': .1, 'y': .1})
        check_account_btn.bind(on_press=self.check_account)
        layout.add_widget(check_account_btn)


        # Add widgets to the layout
        layout.add_widget(self.phone_number_input)
        layout.add_widget(self.amount_input)
        layout.add_widget(charge_account_btn)

        # Add layout on top of the background
        self.add_widget(layout)

    def check_account(self, instance):
        phone_number = self.phone_number_input.text
        try:
            response = requests.post('http://localhost:5000/check_account', json={'phone_number': phone_number})
            if response.ok:
                total_amount = response.json().get('amount', 0)
                popup = Popup(title='Account Balance',
                              content=Label(text=f'Balance: {total_amount}'),
                              size_hint=(None, None), size=(200, 200))
                popup.open()
            else:
                print('Failed to check account')
        except requests.RequestException as e:
            print(f'Request failed: {e}')

    def on_start(self):
        charge_account_btn = self.ids['charge_account_btn']  # Ensure you have an id for your button in the kv language
        charge_account_btn.bind(on_press=self.charge_account)

    def charge_account(self, instance):
        phone_number = self.phone_number_input.text
        amount = self.amount_input.text
        # Send this data to your Flask server
        try:
            response = requests.post('http://localhost:5000/charge_account', json={'phone_number': phone_number, 'amount': amount})
            if response.ok:
                # Display a popup for successful charge
                self.show_popup('Success', 'Account charged successfully!')
            else:
                # If the server returns an error, show it in the popup
                self.show_popup('Error', 'Failed to charge account')
        except requests.RequestException as e:
            # If the request fails, show the error in the popup
            self.show_popup('Error', f'Request failed: {e}')

    def show_popup(self, title, message):
        popup_content = Label(text=message)
        popup = Popup(title=title,
                      content=popup_content,
                      size_hint=(None, None), size=(300, 200))
        popup.open()


class MyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        sm = ScreenManager()
        sm.add_widget(CustomScreen(name='first'))
        # Add more screens as needed
        return sm
        
if __name__ == '__main__':
    MyApp().run()
