import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.animation import Animation
import requests
import threading
import json
import time

# Modern Material Design 3 Theme
THEME = {
    'bg': [0.03, 0.03, 0.03, 1.0],        # Almost black background
    'surface': [0.08, 0.08, 0.08, 1.0],   # Dark surface
    'primary': [0.2, 0.7, 0.9, 1.0],      # Blue primary
    'secondary': [0.9, 0.3, 0.5, 1.0],    # Pink accent
    'success': [0.2, 0.8, 0.4, 1.0],      # Green success
    'warning': [1.0, 0.7, 0.0, 1.0],      # Orange warning
    'error': [0.9, 0.2, 0.2, 1.0],        # Red error
    'text': [0.95, 0.95, 0.95, 1.0],      # Light text
    'text_secondary': [0.7, 0.7, 0.7, 1.0] # Secondary text
}

class ModernCard(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*THEME['surface'])
            self.rect = RoundedRectangle(
                pos=self.pos, 
                size=self.size, 
                radius=[dp(12)]
            )
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class ModernButton(Button):
    def __init__(self, style='primary', **kwargs):
        super().__init__(**kwargs)
        self.background_color = [0, 0, 0, 0]  # Transparent default
        self.style = style
        self.font_size = sp(16)
        self.bold = True
        
        with self.canvas.before:
            Color(*THEME[style])
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8)]
            )
        
        self.bind(pos=self.update_bg, size=self.update_bg)
        self.bind(on_press=self.animate_press)
        self.bind(on_release=self.animate_release)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def animate_press(self, *args):
        anim = Animation(opacity=0.7, duration=0.1)
        anim.start(self)

    def animate_release(self, *args):
        anim = Animation(opacity=1.0, duration=0.1)
        anim.start(self)

class ModernInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = [0, 0, 0, 0]
        self.foreground_color = THEME['text']
        self.cursor_color = THEME['primary']
        self.font_size = sp(16)
        self.multiline = False
        self.padding = [dp(16), dp(12)]
        
        with self.canvas.before:
            Color(*THEME['surface'])
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8)]
            )
            Color(*THEME['primary'])
            self.border = Line(
                rounded_rectangle=(
                    self.pos[0], self.pos[1], 
                    self.size[0], self.size[1], 
                    dp(8)
                ),
                width=dp(1)
            )
        
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border.rounded_rectangle = (
            self.pos[0], self.pos[1], 
            self.size[0], self.size[1], 
            dp(8)
        )

class StatusWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(50)
        self.spacing = dp(10)
        
        # Status indicator
        self.status_indicator = Widget()
        self.status_indicator.size_hint = (None, None)
        self.status_indicator.size = (dp(12), dp(12))
        
        with self.status_indicator.canvas:
            Color(*THEME['warning'])
            self.indicator_circle = RoundedRectangle(
                pos=self.status_indicator.pos,
                size=self.status_indicator.size,
                radius=[dp(6)]
            )
        
        # Status text
        self.status_label = Label(
            text='Disconnected',
            color=THEME['text_secondary'],
            font_size=sp(14),
            text_size=(None, None)
        )
        
        self.add_widget(self.status_indicator)
        self.add_widget(self.status_label)
        
        self.status_indicator.bind(pos=self.update_indicator)

    def update_indicator(self, *args):
        self.indicator_circle.pos = self.status_indicator.pos

    def update_status(self, status, color):
        self.status_label.text = status
        with self.status_indicator.canvas:
            Color(*THEME[color])
            self.indicator_circle = RoundedRectangle(
                pos=self.status_indicator.pos,
                size=self.status_indicator.size,
                radius=[dp(6)]
            )

class MainApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.target_url = ""
        self.admin_token = ""
        self.connection_status = "disconnected"
        
        # Load config if exists
        self.load_config()

    def build(self):
        # Main container
        main_layout = BoxLayout(
            orientation='vertical',
            padding=[dp(20), dp(40), dp(20), dp(20)],
            spacing=dp(20)
        )
        
        # Set background
        with main_layout.canvas.before:
            Color(*THEME['bg'])
            self.bg_rect = RoundedRectangle(
                pos=main_layout.pos,
                size=main_layout.size
            )
        main_layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Title
        title = Label(
            text='Remote Shutdown Controller',
            font_size=sp(28),
            color=THEME['text'],
            bold=True,
            size_hint_y=None,
            height=dp(50),
            text_size=(None, None)
        )
        
        # Status widget
        self.status_widget = StatusWidget()
        
        # Configuration card
        config_card = ModernCard()
        config_card.size_hint_y = None
        config_card.height = dp(200)
        
        config_layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15)
        )
        
        # URL Input
        url_label = Label(
            text='Target URL:',
            color=THEME['text'],
            font_size=sp(16),
            size_hint_y=None,
            height=dp(30),
            text_size=(None, None),
            halign='left'
        )
        
        self.url_input = ModernInput(
            text=self.target_url,
            hint_text='https://your-tunnel-url.com',
            size_hint_y=None,
            height=dp(50)
        )
        
        # Token Input
        token_label = Label(
            text='Admin Token:',
            color=THEME['text'],
            font_size=sp(16),
            size_hint_y=None,
            height=dp(30),
            text_size=(None, None),
            halign='left'
        )
        
        self.token_input = ModernInput(
            text=self.admin_token,
            hint_text='Your admin token',
            password=True,
            size_hint_y=None,
            height=dp(50)
        )
        
        config_layout.add_widget(url_label)
        config_layout.add_widget(self.url_input)
        config_layout.add_widget(token_label)
        config_layout.add_widget(self.token_input)
        
        config_card.add_widget(config_layout)
        
        # Control buttons
        button_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(15),
            size_hint_y=None,
            height=dp(60)
        )
        
        test_btn = ModernButton(
            text='Test Connection',
            style='secondary',
            size_hint=(0.5, 1)
        )
        test_btn.bind(on_press=self.test_connection)
        
        shutdown_btn = ModernButton(
            text='Shutdown PC',
            style='error',
            size_hint=(0.5, 1)
        )
        shutdown_btn.bind(on_press=self.confirm_shutdown)
        
        button_layout.add_widget(test_btn)
        button_layout.add_widget(shutdown_btn)
        
        # Activity log card
        log_card = ModernCard()
        
        log_layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10)
        )
        
        log_title = Label(
            text='Activity Log',
            color=THEME['text'],
            font_size=sp(18),
            bold=True,
            size_hint_y=None,
            height=dp(40),
            text_size=(None, None),
            halign='left'
        )
        
        # Scrollable log
        scroll = ScrollView()
        self.log_label = Label(
            text='Application started\n',
            color=THEME['text_secondary'],
            font_size=sp(14),
            text_size=(None, None),
            halign='left',
            valign='top'
        )
        
        scroll.add_widget(self.log_label)
        
        log_layout.add_widget(log_title)
        log_layout.add_widget(scroll)
        
        log_card.add_widget(log_layout)
        
        # Add all widgets to main layout
        main_layout.add_widget(title)
        main_layout.add_widget(self.status_widget)
        main_layout.add_widget(config_card)
        main_layout.add_widget(button_layout)
        main_layout.add_widget(log_card)
        
        # Auto-test connection if config exists
        if self.target_url and self.admin_token:
            Clock.schedule_once(lambda dt: self.test_connection(), 1)
        
        return main_layout

    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                self.target_url = config.get('target_url', '')
                self.admin_token = config.get('admin_token', '')
        except:
            pass

    def save_config(self):
        config = {
            'target_url': self.target_url,
            'admin_token': self.admin_token
        }
        try:
            with open('config.json', 'w') as f:
                json.dump(config, f)
        except Exception as e:
            self.add_log(f"Failed to save config: {str(e)}")

    def add_log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_label.text += f"[{timestamp}] {message}\n"

    def test_connection(self, *args):
        # Get current values
        self.target_url = self.url_input.text.strip()
        self.admin_token = self.token_input.text.strip()
        
        if not self.target_url or not self.admin_token:
            self.add_log("Please enter both URL and token")
            return
        
        # Save config
        self.save_config()
        
        # Update status
        self.status_widget.update_status("Testing...", "warning")
        self.add_log("Testing connection...")
        
        # Test in background thread
        threading.Thread(target=self._test_connection_thread, daemon=True).start()

    def _test_connection_thread(self):
        try:
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            response = requests.get(
                f"{self.target_url}/status",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                Clock.schedule_once(lambda dt: self._connection_success(), 0)
            else:
                Clock.schedule_once(lambda dt: self._connection_failed(f"HTTP {response.status_code}"), 0)
                
        except requests.exceptions.Timeout:
            Clock.schedule_once(lambda dt: self._connection_failed("Connection timeout"), 0)
        except requests.exceptions.ConnectionError:
            Clock.schedule_once(lambda dt: self._connection_failed("Connection refused"), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self._connection_failed(str(e)), 0)

    def _connection_success(self):
        self.connection_status = "connected"
        self.status_widget.update_status("Connected", "success")
        self.add_log("Connection successful!")

    def _connection_failed(self, error):
        self.connection_status = "disconnected"
        self.status_widget.update_status("Connection Failed", "error")
        self.add_log(f"Connection failed: {error}")

    def confirm_shutdown(self, *args):
        if self.connection_status != "connected":
            self.add_log("Please test connection first")
            return
        
        # Create confirmation popup
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(20)
        )
        
        warning_label = Label(
            text='Are you sure you want to shutdown the remote PC?\n\nThis action cannot be undone.',
            color=THEME['text'],
            font_size=sp(16),
            halign='center'
        )
        
        button_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(15),
            size_hint_y=None,
            height=dp(50)
        )
        
        cancel_btn = ModernButton(
            text='Cancel',
            style='secondary',
            size_hint=(0.5, 1)
        )
        
        confirm_btn = ModernButton(
            text='Shutdown',
            style='error',
            size_hint=(0.5, 1)
        )
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(confirm_btn)
        
        content.add_widget(warning_label)
        content.add_widget(button_layout)
        
        popup = Popup(
            title='Confirm Shutdown',
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=False
        )
        
        cancel_btn.bind(on_press=popup.dismiss)
        confirm_btn.bind(on_press=lambda x: (popup.dismiss(), self.execute_shutdown()))
        
        popup.open()

    def execute_shutdown(self):
        self.add_log("Initiating shutdown...")
        threading.Thread(target=self._shutdown_thread, daemon=True).start()

    def _shutdown_thread(self):
        try:
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            response = requests.post(
                f"{self.target_url}/shutdown",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                Clock.schedule_once(lambda dt: self.add_log("Shutdown command sent successfully!"), 0)
            else:
                Clock.schedule_once(lambda dt: self.add_log(f"Shutdown failed: HTTP {response.status_code}"), 0)
                
        except Exception as e:
            Clock.schedule_once(lambda dt: self.add_log(f"Shutdown error: {str(e)}"), 0)

if __name__ == '__main__':
    MainApp().run()