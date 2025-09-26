# mobile_controller.py - Mobile version of Cloudflare Remote Shutdown Controller
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.properties import StringProperty
import requests
import urllib3
import threading

# Set the app to portrait mode
Window.orientation = 'portrait'

# Disable SSL warnings when using verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# CONFIG - Default values
DEFAULT_TARGET_URL = "https://your-cloudflare-url.trycloudflare.com/shutdown"
DEFAULT_ADMIN_TOKEN = "admin-shutdown-2024-token-secure"

class SettingsPanel(BoxLayout):
    title = StringProperty("Settings")
    
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app_instance = app_instance
        self.orientation = 'vertical'
        self.spacing = dp(15)
        self.padding = dp(20)
        
        # Title
        title = Label(
            text='Settings',
            font_size=dp(24),
            size_hint_y=None,
            height=dp(50),
            bold=True
        )
        self.add_widget(title)
        
        # Admin Token section
        token_section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(140))
        token_section.add_widget(Label(
            text='Admin Token:',
            font_size=dp(16),
            size_hint_y=None,
            height=dp(40),
            bold=True,
            halign='left',
            text_size=(None, None)
        ))
        
        self.token_input = TextInput(
            text=DEFAULT_ADMIN_TOKEN,
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            font_size=dp(14),
            password=True
        )
        token_section.add_widget(self.token_input)
        
        # Toggle password visibility
        toggle_btn = Button(
            text='Show/Hide Token',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.6, 0.6, 0.6, 1)
        )
        toggle_btn.bind(on_press=self.toggle_password_visibility)
        token_section.add_widget(toggle_btn)
        
        save_token_btn = Button(
            text='Save Token',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.2, 0.8, 0.2, 1)
        )
        save_token_btn.bind(on_press=self.save_token)
        token_section.add_widget(save_token_btn)
        
        self.add_widget(token_section)
        
        # Reset to defaults
        reset_section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))
        reset_section.add_widget(Label(
            text='Reset Settings:',
            font_size=dp(16),
            size_hint_y=None,
            height=dp(40),
            bold=True
        ))
        
        reset_btn = Button(
            text='Reset to Defaults',
            size_hint_y=None,
            height=dp(50),
            background_color=(1, 0.5, 0, 1)
        )
        reset_btn.bind(on_press=self.reset_defaults)
        reset_section.add_widget(reset_btn)
        
        self.add_widget(reset_section)
        
        # Status/Info section
        self.settings_status = Label(
            text='Settings ready',
            font_size=dp(14),
            color=(0, 1, 0, 1),
            size_hint_y=None,
            height=dp(40)
        )
        self.add_widget(self.settings_status)
        
        # Instructions
        instructions_scroll = ScrollView()
        instructions_text = Label(
            text=(
                "Token Configuration:\n\n"
                "• The admin token is used to authenticate shutdown commands\n\n"
                "• Make sure this matches the token configured on the target machine\n\n"
                "• Token is hidden by default for security\n\n"
                "• Click 'Show/Hide Token' to toggle visibility\n\n"
                "• Don't forget to save after making changes\n\n"
                "Security Note:\n"
                "Keep your admin token secure and don't share it with unauthorized users."
            ),
            text_size=(dp(300), None),
            halign='left',
            valign='top',
            font_size=dp(13),
            size_hint_y=None
        )
        instructions_text.bind(texture_size=instructions_text.setter('size'))
        instructions_scroll.add_widget(instructions_text)
        self.add_widget(instructions_scroll)
    
    def toggle_password_visibility(self, instance):
        """Toggle password visibility for the token input"""
        self.token_input.password = not self.token_input.password
        
    def save_token(self, instance):
        """Save the token and update the main controller"""
        new_token = self.token_input.text.strip()
        if new_token:
            self.app_instance.admin_token = new_token
            self.settings_status.text = "✅ Token saved successfully!"
            self.settings_status.color = (0, 1, 0, 1)
        else:
            self.settings_status.text = "❌ Token cannot be empty!"
            self.settings_status.color = (1, 0, 0, 1)
    
    def reset_defaults(self, instance):
        """Reset all settings to default values"""
        self.token_input.text = DEFAULT_ADMIN_TOKEN
        self.app_instance.admin_token = DEFAULT_ADMIN_TOKEN
        self.settings_status.text = "🔄 Settings reset to defaults"
        self.settings_status.color = (0, 0, 1, 1)


class MobileShutdownController(BoxLayout):
    title = StringProperty("Controller")
    
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app_instance = app_instance
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(20)
        
        # Title
        title = Label(
            text='Remote Shutdown Controller',
            font_size=dp(20),
            size_hint_y=None,
            height=dp(50),
            bold=True
        )
        self.add_widget(title)
        
        # URL input section
        url_section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120))
        url_section.add_widget(Label(
            text='Cloudflare Tunnel URL:',
            font_size=dp(16),
            size_hint_y=None,
            height=dp(40),
            bold=True
        ))
        
        self.url_input = TextInput(
            text=DEFAULT_TARGET_URL,
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            font_size=dp(14)
        )
        url_section.add_widget(self.url_input)
        
        update_url_btn = Button(
            text='Update URL',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.2, 0.6, 1, 1)
        )
        update_url_btn.bind(on_press=self.update_url)
        url_section.add_widget(update_url_btn)
        
        self.add_widget(url_section)
        
        # Status section
        self.status_label = Label(
            text='Ready',
            font_size=dp(16),
            color=(0, 1, 0, 1),
            size_hint_y=None,
            height=dp(40)
        )
        self.add_widget(self.status_label)
        
        # Control buttons
        button_section = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, height=dp(120))
        
        test_btn = Button(
            text='Test Connection',
            size_hint_y=None,
            height=dp(50),
            background_color=(1, 0.6, 0, 1),
            font_size=dp(16)
        )
        test_btn.bind(on_press=self.test_connection)
        button_section.add_widget(test_btn)
        
        shutdown_btn = Button(
            text='SHUTDOWN TARGET',
            size_hint_y=None,
            height=dp(60),
            background_color=(1, 0.2, 0.2, 1),
            font_size=dp(18),
            bold=True
        )
        shutdown_btn.bind(on_press=self.confirm_shutdown)
        button_section.add_widget(shutdown_btn)
        
        self.add_widget(button_section)
        
        # Instructions
        instructions_scroll = ScrollView()
        instructions_text = Label(
            text=(
                "Instructions:\n\n"
                "1. Configure your admin token in the Settings tab\n\n"
                "2. Run start_cloudflare.bat on the target machine\n\n"
                "3. Copy the Cloudflare URL from the terminal output\n\n"
                "4. Paste it above and add '/shutdown' to the end\n\n"
                "5. Click 'Test Connection' to verify connectivity\n\n"
                "6. Click 'SHUTDOWN TARGET' to send shutdown command\n\n"
                "Note: Make sure the tunnel is running before attempting connection."
            ),
            text_size=(dp(300), None),
            halign='left',
            valign='top',
            font_size=dp(14),
            size_hint_y=None
        )
        instructions_text.bind(texture_size=instructions_text.setter('size'))
        instructions_scroll.add_widget(instructions_text)
        self.add_widget(instructions_scroll)
    
    def update_status(self, message, color=(0, 0, 0, 1)):
        """Update status label with message and color"""
        def update_ui():
            self.status_label.text = message
            self.status_label.color = color
        
        Clock.schedule_once(lambda dt: update_ui())
    
    def update_url(self, instance):
        """Update URL with /shutdown endpoint if needed"""
        current_url = self.url_input.text.strip()
        if current_url:
            if not current_url.endswith('/shutdown'):
                if not current_url.endswith('/'):
                    current_url += '/shutdown'
                else:
                    current_url += 'shutdown'
                self.url_input.text = current_url
            self.update_status("URL updated", (0, 0, 1, 1))
        else:
            self.show_popup("Error", "Please enter a URL first!")
    
    def test_connection(self, instance):
        """Test connection to the target URL"""
        self.update_status("Testing connection...", (1, 0.6, 0, 1))
        threading.Thread(target=self._test_connection_thread, daemon=True).start()
    
    def _test_connection_thread(self):
        """Background thread for testing connection"""
        try:
            url = self.url_input.text.strip()
            if not url or url == DEFAULT_TARGET_URL:
                self.update_status("Please update the URL first!", (1, 0, 0, 1))
                return
            
            # Test basic connection to root
            base_url = url.replace('/shutdown', '/')
            headers = {"User-Agent": "Mozilla/5.0 (Android) Mobile Controller"}
            
            print(f"Testing connection to: {base_url}")
            response = requests.get(base_url, headers=headers, verify=False, timeout=10)
            
            if response.status_code == 200:
                self.update_status("✅ Connection successful! Ready to shutdown.", (0, 1, 0, 1))
                print(f"Connection test passed: {response.status_code}")
            else:
                self.update_status(f"⚠️ Got response code {response.status_code}", (1, 0.6, 0, 1))
                print(f"Response: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            self.update_status("❌ Connection failed - check URL/tunnel", (1, 0, 0, 1))
            print("Connection error - tunnel may not be running")
        except Exception as e:
            self.update_status(f"❌ Error: {str(e)[:30]}...", (1, 0, 0, 1))
            print(f"Test error: {e}")
    
    def confirm_shutdown(self, instance):
        """Show confirmation popup before shutdown"""
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        content.add_widget(Label(
            text='Are you sure you want to shutdown the target machine?',
            text_size=(dp(280), None),
            halign='center',
            font_size=dp(16)
        ))
        
        buttons = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        
        yes_btn = Button(text='YES', background_color=(1, 0.2, 0.2, 1))
        no_btn = Button(text='NO', background_color=(0.5, 0.5, 0.5, 1))
        
        buttons.add_widget(yes_btn)
        buttons.add_widget(no_btn)
        content.add_widget(buttons)
        
        popup = Popup(
            title='Confirm Shutdown',
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        
        yes_btn.bind(on_press=lambda x: self.execute_shutdown(popup))
        no_btn.bind(on_press=popup.dismiss)
        
        popup.open()
    
    def execute_shutdown(self, popup):
        """Execute the shutdown command"""
        popup.dismiss()
        self.update_status("Sending shutdown command...", (1, 0.6, 0, 1))
        threading.Thread(target=self._shutdown_thread, daemon=True).start()
    
    def _shutdown_thread(self):
        """Background thread for shutdown operation"""
        try:
            url = self.url_input.text.strip()
            if not url or url == DEFAULT_TARGET_URL:
                self.update_status("Please update the URL first!", (1, 0, 0, 1))
                Clock.schedule_once(lambda dt: self.show_popup("Error", "Please update the tunnel URL first!"))
                return
            
            headers = {
                "Authorization": f"Bearer {self.app_instance.admin_token}",
                "User-Agent": "Mozilla/5.0 (Android) Mobile Controller",
                "Content-Type": "application/json"
            }
            
            print(f"Sending shutdown command to: {url}")
            response = requests.post(url, headers=headers, verify=False, timeout=10)
            
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")
            
            if response.status_code == 200:
                self.update_status("✅ Shutdown command sent successfully!", (0, 1, 0, 1))
                Clock.schedule_once(lambda dt: self.show_popup("Success", "Shutdown command accepted!"))
            elif response.status_code == 401:
                self.update_status("❌ Unauthorized - wrong token", (1, 0, 0, 1))
                Clock.schedule_once(lambda dt: self.show_popup("Unauthorized", "Invalid token."))
            else:
                self.update_status(f"❌ Error {response.status_code}", (1, 0, 0, 1))
                Clock.schedule_once(lambda dt: self.show_popup("Failed", f"Error {response.status_code}: {response.text[:100]}"))
                
        except requests.exceptions.ConnectionError:
            self.update_status("❌ Connection failed", (1, 0, 0, 1))
            Clock.schedule_once(lambda dt: self.show_popup("Connection Error", "Could not connect to target. Check if tunnel is running."))
        except Exception as e:
            error_msg = str(e)
            self.update_status("❌ Error occurred", (1, 0, 0, 1))
            Clock.schedule_once(lambda dt: self.show_popup("Error", error_msg))
    
    def show_popup(self, title, message):
        """Show a popup message"""
        content = Label(
            text=message,
            text_size=(dp(280), None),
            halign='center',
            font_size=dp(14)
        )
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.3)
        )
        popup.open()


class MainTabbedPanel(TabbedPanel):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app_instance = app_instance
        self.do_default_tab = False
        
        # Controller tab
        controller_tab = TabbedPanelItem(text='Controller')
        controller_tab.content = MobileShutdownController(app_instance)
        self.add_widget(controller_tab)
        
        # Settings tab
        settings_tab = TabbedPanelItem(text='Settings')
        settings_tab.content = SettingsPanel(app_instance)
        self.add_widget(settings_tab)
        
        # Set default tab to controller
        self.switch_to(controller_tab)


class MobileShutdownApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.admin_token = DEFAULT_ADMIN_TOKEN
    
    def build(self):
        self.title = 'Remote Shutdown Controller'
        return MainTabbedPanel(self)


if __name__ == '__main__':
    MobileShutdownApp().run()