# mobile_controller.py - Modern Mobile version of Cloudflare Remote Shutdown Controller
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
import requests
import urllib3
import threading

# Disable SSL warnings when using verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# CONFIG - Update this URL when you get a new Cloudflare tunnel URL
TARGET_URL = "https://your-cloudflare-url.trycloudflare.com/shutdown"
ADMIN_TOKEN = "admin-shutdown-2024-token-secure"

# Modern Color Scheme - Dark theme with vibrant accents
COLORS = {
    'primary': get_color_from_hex('#FF6B35'),      # Orange accent
    'secondary': get_color_from_hex('#4ECDC4'),    # Teal
    'background': get_color_from_hex('#1A1A1A'),   # Dark background
    'surface': get_color_from_hex('#2D2D2D'),      # Card background
    'text_primary': get_color_from_hex('#FFFFFF'), # White text
    'text_secondary': get_color_from_hex('#B0B0B0'), # Gray text
    'success': get_color_from_hex('#4CAF50'),      # Green
    'warning': get_color_from_hex('#FF9800'),      # Orange
    'error': get_color_from_hex('#F44336'),        # Red
}

class ModernCard(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        with self.canvas.before:
            Color(*COLORS['surface'])
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(15)]
            )
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class ModernButton(Button):
    def __init__(self, bg_color=None, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.bg_color = bg_color or COLORS['primary']
        self.color = COLORS['text_primary']
        self.font_size = dp(16)
        self.bold = True
        
        with self.canvas.before:
            self.color_instruction = Color(*self.bg_color)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(25)]
            )
        self.bind(pos=self.update_graphics, size=self.update_graphics)
    
    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def on_press(self):
        darker_color = [c * 0.8 for c in self.bg_color[:3]] + [self.bg_color[3]]
        self.color_instruction.rgba = darker_color
    
    def on_release(self):
        self.color_instruction.rgba = self.bg_color

class ModernTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_active = ''
        self.foreground_color = COLORS['text_primary']
        self.cursor_color = COLORS['primary']
        self.font_size = dp(14)
        self.padding = [dp(15), dp(10)]
        
        with self.canvas.before:
            Color(*COLORS['surface'])
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(10)]
            )
            Color(*COLORS['text_secondary'])
            self.border = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(10)),
                width=1
            )
        self.bind(pos=self.update_graphics, size=self.update_graphics, focus=self.on_focus)
    
    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(10))
    
    def on_focus(self, instance, value):
        if value:
            self.canvas.before.children[-1].rgba = COLORS['primary']
        else:
            self.canvas.before.children[-1].rgba = COLORS['text_secondary']

class MobileShutdownController(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Background
        with self.canvas.before:
            Color(*COLORS['background'])
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(size=self.update_bg, pos=self.update_bg)
        
        # Main container
        main_container = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=[dp(25), dp(40), dp(25), dp(25)],
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Header
        header = self.create_header()
        main_container.add_widget(header)
        
        # URL input card
        url_card = self.create_url_card()
        main_container.add_widget(url_card)
        
        # Status card
        status_card = self.create_status_card()
        main_container.add_widget(status_card)
        
        # Action buttons
        buttons_section = self.create_buttons_section()
        main_container.add_widget(buttons_section)
        
        # Instructions card
        instructions_card = self.create_instructions_card()
        main_container.add_widget(instructions_card)
        
        self.add_widget(main_container)
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def create_header(self):
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100), spacing=dp(5))
        
        icon = Label(text='🔌', font_size=dp(40), size_hint_y=None, height=dp(50))
        header.add_widget(icon)
        
        title = Label(
            text='Remote Shutdown Controller',
            font_size=dp(22), size_hint_y=None, height=dp(35),
            bold=True, color=COLORS['text_primary']
        )
        header.add_widget(title)
        
        subtitle = Label(
            text='Secure remote computer control',
            font_size=dp(14), size_hint_y=None, height=dp(20),
            color=COLORS['text_secondary']
        )
        header.add_widget(subtitle)
        
        return header
    
    def create_url_card(self):
        card = ModernCard(height=dp(140))
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        label = Label(
            text='🌐 Cloudflare Tunnel URL',
            font_size=dp(16), size_hint_y=None, height=dp(30),
            color=COLORS['text_primary'], halign='left', bold=True
        )
        label.bind(texture_size=label.setter('text_size'))
        content.add_widget(label)
        
        self.url_input = ModernTextInput(
            text=TARGET_URL, multiline=False, size_hint_y=None, height=dp(45),
            hint_text='Enter your Cloudflare tunnel URL...'
        )
        content.add_widget(self.url_input)
        
        update_btn = ModernButton(
            text='📝 Update URL', size_hint_y=None, height=dp(35),
            bg_color=COLORS['secondary']
        )
        update_btn.bind(on_press=self.update_url)
        content.add_widget(update_btn)
        
        card.add_widget(content)
        return card
    
    def create_status_card(self):
        card = ModernCard(height=dp(60))
        
        content = BoxLayout(orientation='horizontal', padding=dp(20), spacing=dp(10))
        
        self.status_indicator = Label(
            text='●', font_size=dp(20), size_hint_x=None, width=dp(30),
            color=COLORS['success']
        )
        content.add_widget(self.status_indicator)
        
        self.status_label = Label(
            text='Ready to connect', font_size=dp(16),
            color=COLORS['text_primary'], halign='left'
        )
        self.status_label.bind(texture_size=self.status_label.setter('text_size'))
        content.add_widget(self.status_label)
        
        card.add_widget(content)
        return card
    
    def create_buttons_section(self):
        section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(130), spacing=dp(15))
        
        test_btn = ModernButton(
            text='🔍 Test Connection', size_hint_y=None, height=dp(55),
            bg_color=COLORS['warning']
        )
        test_btn.bind(on_press=self.test_connection)
        section.add_widget(test_btn)
        
        shutdown_btn = ModernButton(
            text='⚡ SHUTDOWN TARGET', size_hint_y=None, height=dp(60),
            bg_color=COLORS['error'], font_size=dp(18)
        )
        shutdown_btn.bind(on_press=self.confirm_shutdown)
        section.add_widget(shutdown_btn)
        
        return section
    
    def create_instructions_card(self):
        card = ModernCard(height=dp(180))
        
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        title = Label(
            text='📋 Quick Setup Guide',
            font_size=dp(16), size_hint_y=None, height=dp(30),
            color=COLORS['text_primary'], bold=True, halign='left'
        )
        title.bind(texture_size=title.setter('text_size'))
        content.add_widget(title)
        
        instructions_scroll = ScrollView()
        instructions_text = Label(
            text=(
                "1. 🖥️ Run start_cloudflare.bat on target computer\n\n"
                "2. 📋 Copy the Cloudflare URL from terminal\n\n" 
                "3. 📝 Paste URL above and add '/shutdown'\n\n"
                "4. 🔍 Test connection to verify tunnel\n\n"
                "5. ⚡ Use shutdown button when ready\n\n"
                "⚠️ Ensure tunnel is running before connecting!"
            ),
            text_size=(None, None), halign='left', valign='top',
            font_size=dp(12), color=COLORS['text_secondary']
        )
        instructions_scroll.add_widget(instructions_text)
        content.add_widget(instructions_scroll)
        
        card.add_widget(content)
        return card
    
    def update_status(self, message, status_type='info'):
        """Update status with modern styling"""
        def update_ui():
            self.status_label.text = message
            if status_type == 'success':
                self.status_indicator.color = COLORS['success']
                self.status_indicator.text = '✓'
            elif status_type == 'warning':
                self.status_indicator.color = COLORS['warning']
                self.status_indicator.text = '⚠'
            elif status_type == 'error':
                self.status_indicator.color = COLORS['error']
                self.status_indicator.text = '✗'
            else:
                self.status_indicator.color = COLORS['secondary']
                self.status_indicator.text = '●'
        
        Clock.schedule_once(lambda dt: update_ui())
    
    def update_url(self, instance):
        current_url = self.url_input.text.strip()
        if current_url:
            if not current_url.endswith('/shutdown'):
                if not current_url.endswith('/'):
                    current_url += '/shutdown'
                else:
                    current_url += 'shutdown'
                self.url_input.text = current_url
            self.update_status("URL updated successfully", "success")
        else:
            self.show_modern_popup("Error", "Please enter a URL first!", "error")
    
    def test_connection(self, instance):
        self.update_status("Testing connection...", "warning")
        threading.Thread(target=self._test_connection_thread, daemon=True).start()
    
    def _test_connection_thread(self):
        try:
            url = self.url_input.text.strip()
            if not url or url == TARGET_URL:
                self.update_status("Please update the URL first!", "error")
                return
            
            base_url = url.replace('/shutdown', '/')
            headers = {"User-Agent": "Mozilla/5.0 (Android) Mobile Controller"}
            
            response = requests.get(base_url, headers=headers, verify=False, timeout=10)
            
            if response.status_code == 200:
                self.update_status("Connection successful! Ready to shutdown", "success")
            else:
                self.update_status(f"Response code {response.status_code} received", "warning")
                
        except requests.exceptions.ConnectionError:
            self.update_status("Connection failed - check URL/tunnel", "error")
        except Exception as e:
            self.update_status(f"Error: {str(e)[:25]}...", "error")
    
    def confirm_shutdown(self, instance):
        self.show_confirm_popup()
    
    def show_confirm_popup(self):
        content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        # Warning section
        warning_box = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint_y=None, height=dp(60))
        
        icon = Label(text='⚠️', font_size=dp(40), size_hint_x=None, width=dp(50))
        warning_box.add_widget(icon)
        
        message = Label(
            text='Are you sure you want to shutdown the target machine?',
            text_size=(dp(250), None), halign='center', valign='middle',
            font_size=dp(16), color=COLORS['text_primary']
        )
        warning_box.add_widget(message)
        content.add_widget(warning_box)
        
        # Buttons
        buttons = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint_y=None, height=dp(50))
        
        cancel_btn = ModernButton(text='Cancel', bg_color=COLORS['text_secondary'], size_hint_x=0.4)
        confirm_btn = ModernButton(text='Shutdown', bg_color=COLORS['error'], size_hint_x=0.6)
        
        buttons.add_widget(cancel_btn)
        buttons.add_widget(confirm_btn)
        content.add_widget(buttons)
        
        popup = Popup(
            title='⚠️ Confirm Shutdown', content=content, size_hint=(0.85, 0.4),
            auto_dismiss=False, title_color=COLORS['text_primary'],
            separator_color=COLORS['primary']
        )
        
        cancel_btn.bind(on_press=popup.dismiss)
        confirm_btn.bind(on_press=lambda x: self.execute_shutdown(popup))
        
        popup.open()
    
    def execute_shutdown(self, popup):
        popup.dismiss()
        self.update_status("Sending shutdown command...", "warning")
        threading.Thread(target=self._shutdown_thread, daemon=True).start()
    
    def _shutdown_thread(self):
        try:
            url = self.url_input.text.strip()
            if not url or url == TARGET_URL:
                self.update_status("Please update the URL first!", "error")
                return
            
            headers = {
                "Authorization": f"Bearer {ADMIN_TOKEN}",
                "User-Agent": "Mozilla/5.0 (Android) Mobile Controller",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, headers=headers, verify=False, timeout=10)
            
            if response.status_code == 200:
                self.update_status("Shutdown command sent successfully!", "success")
                Clock.schedule_once(lambda dt: self.show_modern_popup(
                    "Success", "Shutdown command accepted!", "success"
                ))
            elif response.status_code == 401:
                self.update_status("Unauthorized - wrong token", "error")
                Clock.schedule_once(lambda dt: self.show_modern_popup(
                    "Unauthorized", "Invalid authentication token.", "error"
                ))
            else:
                self.update_status(f"Error {response.status_code}", "error")
                
        except requests.exceptions.ConnectionError:
            self.update_status("Connection failed", "error")
        except Exception as e:
            self.update_status("Error occurred", "error")
    
    def show_modern_popup(self, title, message, popup_type="info"):
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        
        icons = {'success': '✅', 'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}
        icon_colors = {
            'success': COLORS['success'], 'error': COLORS['error'],
            'warning': COLORS['warning'], 'info': COLORS['secondary']
        }
        
        icon = Label(
            text=icons.get(popup_type, 'ℹ️'), font_size=dp(40),
            size_hint_y=None, height=dp(50),
            color=icon_colors.get(popup_type, COLORS['secondary'])
        )
        content.add_widget(icon)
        
        msg_label = Label(
            text=message, text_size=(dp(250), None), halign='center',
            font_size=dp(14), color=COLORS['text_primary']
        )
        content.add_widget(msg_label)
        
        ok_btn = ModernButton(
            text='OK', size_hint_y=None, height=dp(40),
            bg_color=icon_colors.get(popup_type, COLORS['secondary'])
        )
        content.add_widget(ok_btn)
        
        popup = Popup(
            title=f"{icons.get(popup_type, 'ℹ️')} {title}",
            content=content, size_hint=(0.8, 0.35),
            title_color=COLORS['text_primary'],
            separator_color=icon_colors.get(popup_type, COLORS['secondary'])
        )
        
        ok_btn.bind(on_press=popup.dismiss)
        popup.open()


class MobileShutdownApp(App):
    def build(self):
        self.title = 'Remote Shutdown Controller'
        return MobileShutdownController()


if __name__ == '__main__':
    MobileShutdownApp().run()