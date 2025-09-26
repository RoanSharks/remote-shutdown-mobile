# mobile_controller.py - Mobile version of Cloudflare Remote Shutdown Controller
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.metrics import dp
import requests
import urllib3
import threading

# Disable SSL warnings when using verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# CONFIG - Update this URL when you get a new Cloudflare tunnel URL
TARGET_URL = "https://your-cloudflare-url.trycloudflare.com/shutdown"
ADMIN_TOKEN = "admin-shutdown-2024-token-secure"

class MobileShutdownController(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
            text=TARGET_URL,
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
                "1. Run start_cloudflare.bat on the target machine\n\n"
                "2. Copy the Cloudflare URL from the terminal output\n\n"
                "3. Paste it above and add '/shutdown' to the end\n\n"
                "4. Click 'Test Connection' to verify connectivity\n\n"
                "5. Click 'SHUTDOWN TARGET' to send shutdown command\n\n"
                "Note: Make sure the tunnel is running before attempting connection."
            ),
            text_size=(None, None),
            halign='left',
            valign='top',
            font_size=dp(14)
        )
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
            if not url or url == TARGET_URL:
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
            if not url or url == TARGET_URL:
                self.update_status("Please update the URL first!", (1, 0, 0, 1))
                Clock.schedule_once(lambda dt: self.show_popup("Error", "Please update the tunnel URL first!"))
                return
            
            headers = {
                "Authorization": f"Bearer {ADMIN_TOKEN}",
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
            self.update_status("❌ Error occurred", (1, 0, 0, 1))
            Clock.schedule_once(lambda dt: self.show_popup("Error", str(e)))
    
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


class MobileShutdownApp(App):
    def build(self):
        self.title = 'Remote Shutdown Controller'
        return MobileShutdownController()


if __name__ == '__main__':
    MobileShutdownApp().run()