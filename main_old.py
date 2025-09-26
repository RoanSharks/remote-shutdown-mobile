# Modern Mobile Remote Shutdown Controller - Complete UI Redesign
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse, Canvas
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.effects.scroll import ScrollEffect
import requests
import urllib3
import threading
import time

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
TARGET_URL = "https://your-cloudflare-url.trycloudflare.com/shutdown"
ADMIN_TOKEN = "admin-shutdown-2024-token-secure"

# Modern Design System - Material You inspired
class DesignTokens:
    # Color Palette - Dark theme with high contrast
    COLORS = {
        'primary': [0.2, 0.7, 0.9, 1.0],           # Bright Blue
        'primary_variant': [0.1, 0.5, 0.8, 1.0],   # Dark Blue
        'secondary': [0.9, 0.3, 0.5, 1.0],         # Pink Accent
        'secondary_variant': [0.7, 0.2, 0.4, 1.0], # Dark Pink
        
        'background': [0.05, 0.05, 0.05, 1.0],     # Almost Black
        'surface': [0.1, 0.1, 0.1, 1.0],           # Dark Gray
        'surface_variant': [0.15, 0.15, 0.15, 1.0], # Lighter Dark Gray
        'outline': [0.3, 0.3, 0.3, 1.0],           # Border Gray
        
        'on_primary': [0.05, 0.05, 0.05, 1.0],     # Dark text on primary
        'on_secondary': [1.0, 1.0, 1.0, 1.0],      # White text on secondary
        'on_background': [0.95, 0.95, 0.95, 1.0],  # Light text
        'on_surface': [0.9, 0.9, 0.9, 1.0],        # Surface text
        'on_surface_variant': [0.7, 0.7, 0.7, 1.0], # Muted text
        
        'success': [0.2, 0.8, 0.4, 1.0],           # Green
        'warning': [1.0, 0.6, 0.0, 1.0],           # Orange
        'error': [0.9, 0.2, 0.2, 1.0],             # Red
        'info': [0.3, 0.7, 1.0, 1.0],              # Light Blue
    }
    
    # Typography Scale
    TYPOGRAPHY = {
        'display_large': sp(57),
        'display_medium': sp(45),
        'display_small': sp(36),
        'headline_large': sp(32),
        'headline_medium': sp(28),
        'headline_small': sp(24),
        'title_large': sp(22),
        'title_medium': sp(16),
        'title_small': sp(14),
        'body_large': sp(16),
        'body_medium': sp(14),
        'body_small': sp(12),
        'label_large': sp(14),
        'label_medium': sp(12),
        'label_small': sp(11),
    }
    
    # Spacing Scale
    SPACING = {
        'xs': dp(4),
        'sm': dp(8),
        'md': dp(16),
        'lg': dp(24),
        'xl': dp(32),
        'xxl': dp(48),
    }
    
    # Component Sizes
    COMPONENTS = {
        'button_height': dp(56),
        'input_height': dp(56),
        'card_radius': dp(16),
        'button_radius': dp(28),
        'chip_radius': dp(20),
    }

class MaterialCard(RelativeLayout):
    """Material Design 3 Card Component"""
    def __init__(self, elevation=1, filled=True, **kwargs):
        super().__init__(**kwargs)
        self.elevation = elevation
        self.filled = filled
        
        with self.canvas.before:
            # Shadow layers for elevation
            if elevation > 0:
                for i in range(elevation):
                    shadow_offset = dp(2 + i)
                    shadow_alpha = 0.1 / (i + 1)
                    Color(0, 0, 0, shadow_alpha)
                    shadow_rect = RoundedRectangle(
                        pos=(self.x + shadow_offset, self.y - shadow_offset),
                        size=self.size,
                        radius=[DesignTokens.COMPONENTS['card_radius']]
                    )
                    setattr(self, f'shadow_{i}', shadow_rect)
            
            # Main card background
            bg_color = DesignTokens.COLORS['surface'] if filled else DesignTokens.COLORS['surface_variant']
            Color(*bg_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[DesignTokens.COMPONENTS['card_radius']]
            )
            
            # Subtle border
            Color(*DesignTokens.COLORS['outline'], 0.2)
            self.border = Line(
                rounded_rectangle=(
                    self.x, self.y, self.width, self.height, 
                    DesignTokens.COMPONENTS['card_radius']
                ),
                width=1
            )
        
        self.bind(pos=self.update_graphics, size=self.update_graphics)
    
    def update_graphics(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border.rounded_rectangle = (
            self.x, self.y, self.width, self.height,
            DesignTokens.COMPONENTS['card_radius']
        )
        
        # Update shadow positions
        for i in range(self.elevation):
            shadow_offset = dp(2 + i)
            shadow_rect = getattr(self, f'shadow_{i}', None)
            if shadow_rect:
                shadow_rect.pos = (self.x + shadow_offset, self.y - shadow_offset)
                shadow_rect.size = self.size

class ModernCard(RelativeLayout):
    def __init__(self, elevated=False, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.elevated = elevated
        
        with self.canvas.before:
            # Shadow effect for elevated cards
            if elevated:
                Color(0, 0, 0, 0.1)
                self.shadow = RoundedRectangle(
                    pos=(self.x + dp(2), self.y - dp(2)),
                    size=self.size,
                    radius=[dp(15)]
                )
            
            # Main card background
            color = COLORS['surface_elevated'] if elevated else COLORS['surface']
            Color(*color)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(15)]
            )
            
            # Subtle border
            Color(*COLORS['text_disabled'], 0.1)
            self.border = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(15)),
                width=1
            )
        
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        if hasattr(self, 'shadow'):
            self.shadow.pos = (self.x + dp(2), self.y - dp(2))
            self.shadow.size = self.size
        if hasattr(self, 'border'):
            self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(15))

class ModernButton(Button):
    def __init__(self, bg_color=None, icon=None, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.bg_color = bg_color or COLORS['primary']
        self.original_bg_color = self.bg_color[:]
        self.color = COLORS['text_primary']
        self.font_size = sp(16)
        self.bold = True
        self.icon = icon
        
        # Add ripple effect circle
        with self.canvas.before:
            self.color_instruction = Color(*self.bg_color)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(25)]
            )
            
            # Ripple effect (initially invisible)
            self.ripple_color = Color(1, 1, 1, 0)
            self.ripple = Ellipse(pos=self.center, size=(0, 0))
        
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        
        # Update text with icon if provided
        if self.icon:
            self.text = f"{self.icon} {self.text}"
    
    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def on_press(self):
        # Darken background
        darker_color = [c * 0.85 for c in self.original_bg_color[:3]] + [self.original_bg_color[3]]
        self.color_instruction.rgba = darker_color
        
        # Animate ripple effect
        self.ripple.pos = (self.center_x - dp(25), self.center_y - dp(25))
        self.ripple.size = (dp(50), dp(50))
        self.ripple_color.a = 0.2
        
        ripple_anim = Animation(size=(self.width * 1.5, self.height * 1.5), duration=0.3)
        fade_anim = Animation(a=0, duration=0.3)
        ripple_anim.start(self.ripple)
        fade_anim.start(self.ripple_color)
    
    def on_release(self):
        self.color_instruction.rgba = self.original_bg_color
        
        # Scale animation for feedback
        scale_down = Animation(size=(self.width * 0.95, self.height * 0.95), duration=0.05)
        scale_up = Animation(size=(self.width, self.height), duration=0.1)
        scale_down.bind(on_complete=lambda *args: scale_up.start(self))
        scale_down.start(self)

class ModernTextInput(TextInput):
    def __init__(self, validation_type=None, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_active = ''
        self.foreground_color = COLORS['text_primary']
        self.cursor_color = COLORS['primary']
        self.selection_color = COLORS['primary'][:3] + [0.3]  # Fix: Only use RGB + alpha
        self.font_size = sp(14)
        self.padding = [dp(15), dp(12)]
        self.validation_type = validation_type
        self.is_valid = True
        
        with self.canvas.before:
            # Background with subtle elevation
            Color(*COLORS['surface_elevated'])
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(10)]
            )
            
            # Border with animation support
            self.border_color = Color(*COLORS['text_disabled'], 0.5)
            self.border_line = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(10)),
                width=dp(2)
            )
            
            # Focus indicator (bottom line)
            self.focus_color = Color(*COLORS['primary'], 0)
            self.focus_line = Line(
                points=[self.x + dp(10), self.y + dp(2), self.right - dp(10), self.y + dp(2)],
                width=dp(3)
            )
        
        self.bind(pos=self.update_graphics, size=self.update_graphics, focus=self.on_focus, text=self.validate_text)
    
    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(10))
        self.focus_line.points = [self.x + dp(10), self.y + dp(2), self.right - dp(10), self.y + dp(2)]
    
    def on_focus(self, instance, value):
        if value:  # Focused
            # Animate border and focus line
            self.border_color.rgba = COLORS['primary'][:3] + [0.8]  # Fix color concatenation
            focus_anim = Animation(a=1, duration=0.2)
            focus_anim.start(self.focus_color)
        else:  # Unfocused
            color = COLORS['error'] if not self.is_valid else COLORS['text_disabled']
            self.border_color.rgba = color[:3] + [0.5]  # Fix color concatenation
            focus_anim = Animation(a=0, duration=0.2)
            focus_anim.start(self.focus_color)
    
    def validate_text(self, instance, text):
        if self.validation_type == 'url' and text:
            self.is_valid = text.startswith(('http://', 'https://'))
            if not self.focus:
                color = COLORS['error'] if not self.is_valid else COLORS['text_disabled']
                self.border_color.rgba = color[:3] + [0.5]  # Fix color concatenation

class MobileShutdownController(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set window background color
        Window.clearcolor = COLORS['background']
        
        # Responsive padding based on window size
        padding_x = max(dp(20), Window.width * 0.05)
        padding_y = max(dp(25), Window.height * 0.03)
        
        # Background with subtle gradient effect
        with self.canvas.before:
            Color(*COLORS['background'])
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size)
            
            # Subtle overlay pattern
            Color(*COLORS['surface'], 0.02)
            self.overlay = RoundedRectangle(pos=self.pos, size=self.size)
        
        self.bind(size=self.update_bg, pos=self.update_bg)
        
        # Main container with responsive design
        main_container = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=[padding_x, padding_y, padding_x, dp(20)],
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Add scroll view for better mobile experience
        scroll = ScrollView()
        scroll_content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None,
            height=dp(800)  # Adjust based on content
        )
        
        # Header with animation
        header = self.create_header()
        scroll_content.add_widget(header)
        
        # URL input card
        url_card = self.create_url_card()
        scroll_content.add_widget(url_card)
        
        # Status card
        status_card = self.create_status_card()
        scroll_content.add_widget(status_card)
        
        # Action buttons
        buttons_section = self.create_buttons_section()
        scroll_content.add_widget(buttons_section)
        
        # Instructions card
        instructions_card = self.create_instructions_card()
        scroll_content.add_widget(instructions_card)
        
        scroll.add_widget(scroll_content)
        main_container.add_widget(scroll)
        self.add_widget(main_container)
        
        # Animate entrance
        self.opacity = 0
        entrance_anim = Animation(opacity=1, duration=0.5)
        Clock.schedule_once(lambda dt: entrance_anim.start(self), 0.1)
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        if hasattr(self, 'overlay'):
            self.overlay.pos = self.pos
            self.overlay.size = self.size
    
    def create_header(self):
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120), spacing=dp(8))
        
        # Animated icon with glow effect
        icon_container = RelativeLayout(size_hint_y=None, height=dp(50))
        icon = Label(
            text='🔌', font_size=dp(42), 
            size_hint_y=None, height=dp(50),
            color=COLORS['primary']
        )
        icon_container.add_widget(icon)
        header.add_widget(icon_container)
        
        # Main title with better typography
        title = Label(
            text='Remote Shutdown Controller',
            font_size=sp(24), size_hint_y=None, height=dp(40),
            bold=True, color=COLORS['text_primary'],
            halign='center'
        )
        title.bind(texture_size=title.setter('text_size'))
        header.add_widget(title)
        
        # Subtitle with accent color
        subtitle = Label(
            text='🛡️ Secure remote computer control',
            font_size=sp(14), size_hint_y=None, height=dp(25),
            color=COLORS['accent'], halign='center'
        )
        subtitle.bind(texture_size=subtitle.setter('text_size'))
        header.add_widget(subtitle)
        
        # Subtle pulse animation for icon
        def animate_icon(*args):
            pulse = Animation(font_size=dp(46), duration=1) + Animation(font_size=dp(42), duration=1)
            pulse.repeat = True
            pulse.start(icon)
        
        Clock.schedule_once(animate_icon, 1)
        
        return header
    
    def create_url_card(self):
        card = ModernCard(height=dp(160), elevated=True)
        
        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(20))
        
        # Header with icon and title
        header_box = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(30))
        
        icon_label = Label(
            text='🌐', font_size=dp(20), size_hint_x=None, width=dp(30),
            color=COLORS['secondary']
        )
        header_box.add_widget(icon_label)
        
        title_label = Label(
            text='Cloudflare Tunnel URL',
            font_size=sp(16), color=COLORS['text_primary'], 
            halign='left', bold=True
        )
        title_label.bind(texture_size=title_label.setter('text_size'))
        header_box.add_widget(title_label)
        
        content.add_widget(header_box)
        
        # URL input with validation
        self.url_input = ModernTextInput(
            text=TARGET_URL, multiline=False, 
            size_hint_y=None, height=dp(50),
            hint_text='Enter your Cloudflare tunnel URL...',
            validation_type='url'
        )
        content.add_widget(self.url_input)
        
        # Button row with icons
        button_box = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))
        
        update_btn = ModernButton(
            text='Update URL', size_hint_x=0.6,
            bg_color=COLORS['secondary'], icon='📝'
        )
        update_btn.bind(on_press=self.update_url)
        button_box.add_widget(update_btn)
        
        clear_btn = ModernButton(
            text='Clear', size_hint_x=0.4,
            bg_color=COLORS['text_disabled'], icon='🗑️'
        )
        clear_btn.bind(on_press=self.clear_url)
        button_box.add_widget(clear_btn)
        
        content.add_widget(button_box)
        
        card.add_widget(content)
        return card
    
    def create_status_card(self):
        card = ModernCard(height=dp(80), elevated=True)
        
        content = BoxLayout(orientation='horizontal', padding=dp(20), spacing=dp(15))
        
        # Status indicator container with pulse animation
        indicator_container = RelativeLayout(size_hint_x=None, width=dp(40))
        
        self.status_indicator = Label(
            text='●', font_size=dp(24), 
            color=COLORS['success'], pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        indicator_container.add_widget(self.status_indicator)
        content.add_widget(indicator_container)
        
        # Status text with better typography
        status_container = BoxLayout(orientation='vertical', spacing=dp(2))
        
        self.status_label = Label(
            text='Ready to connect', font_size=sp(16),
            color=COLORS['text_primary'], halign='left', bold=True
        )
        self.status_label.bind(texture_size=self.status_label.setter('text_size'))
        status_container.add_widget(self.status_label)
        
        self.status_detail = Label(
            text='Waiting for configuration...', font_size=sp(12),
            color=COLORS['text_secondary'], halign='left'
        )
        self.status_detail.bind(texture_size=self.status_detail.setter('text_size'))
        status_container.add_widget(self.status_detail)
        
        content.add_widget(status_container)
        
        # Connection strength indicator (optional)
        strength_container = BoxLayout(
            orientation='horizontal', size_hint_x=None, width=dp(60),
            spacing=dp(2), pos_hint={'center_y': 0.5}
        )
        
        self.signal_bars = []
        for i in range(4):
            bar = Label(
                text='▮', font_size=dp(12 + i * 2), 
                color=COLORS['text_disabled'], opacity=0.3,
                size_hint_x=None, width=dp(8)
            )
            self.signal_bars.append(bar)
            strength_container.add_widget(bar)
        
        content.add_widget(strength_container)
        
        card.add_widget(content)
        return card
    
    def create_buttons_section(self):
        section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(160), spacing=dp(15))
        
        # Test connection button with enhanced styling
        test_btn = ModernButton(
            text='Test Connection', size_hint_y=None, height=dp(60),
            bg_color=COLORS['warning'], icon='🔍', font_size=sp(16)
        )
        test_btn.bind(on_press=self.test_connection)
        section.add_widget(test_btn)
        
        # Shutdown button container with warning styling
        shutdown_container = RelativeLayout(size_hint_y=None, height=dp(70))
        
        # Pulsing background for shutdown button
        with shutdown_container.canvas.before:
            Color(*COLORS['error'], 0.1)
            self.shutdown_bg = RoundedRectangle(
                pos=shutdown_container.pos, size=shutdown_container.size,
                radius=[dp(15)]
            )
        shutdown_container.bind(pos=self.update_shutdown_bg, size=self.update_shutdown_bg)
        
        self.shutdown_btn = ModernButton(
            text='SHUTDOWN TARGET', 
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(0.95, 0.85),
            bg_color=COLORS['error'], icon='⚡', font_size=sp(18)
        )
        self.shutdown_btn.bind(on_press=self.confirm_shutdown)
        shutdown_container.add_widget(self.shutdown_btn)
        
        section.add_widget(shutdown_container)
        
        # Add subtle pulsing animation to shutdown button
        def animate_shutdown(*args):
            if hasattr(self, 'shutdown_bg'):
                pulse = Animation(opacity=0.2, duration=1.5) + Animation(opacity=0.1, duration=1.5)
                pulse.repeat = True
                # Note: This would need canvas color animation which is complex in Kivy
        
        return section
        
    def update_shutdown_bg(self, instance, *args):
        if hasattr(self, 'shutdown_bg'):
            self.shutdown_bg.pos = instance.pos
            self.shutdown_bg.size = instance.size
    
    def create_instructions_card(self):
        card = ModernCard(height=dp(220), elevated=True)
        
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        
        # Header with collapsible functionality
        header_box = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(30))
        
        icon = Label(
            text='📋', font_size=dp(18), size_hint_x=None, width=dp(30),
            color=COLORS['accent']
        )
        header_box.add_widget(icon)
        
        title = Label(
            text='Quick Setup Guide',
            font_size=sp(16), color=COLORS['text_primary'], 
            bold=True, halign='left'
        )
        title.bind(texture_size=title.setter('text_size'))
        header_box.add_widget(title)
        
        # Expand/collapse button
        self.expand_btn = Label(
            text='▼', font_size=dp(12), size_hint_x=None, width=dp(20),
            color=COLORS['text_secondary']
        )
        header_box.add_widget(self.expand_btn)
        
        content.add_widget(header_box)
        
        # Instructions content
        self.instructions_scroll = ScrollView()
        
        # Create step-by-step instructions with icons
        steps_layout = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        steps_layout.bind(minimum_height=steps_layout.setter('height'))
        
        steps = [
            ('🖥️', 'Run start_cloudflare.bat on target computer'),
            ('📋', 'Copy the Cloudflare URL from terminal'),
            ('📝', "Paste URL above and add '/shutdown'"),
            ('🔍', 'Test connection to verify tunnel'),
            ('⚡', 'Use shutdown button when ready'),
            ('⚠️', 'Ensure tunnel is running before connecting!')
        ]
        
        for i, (icon, text) in enumerate(steps):
            step_box = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(25))
            
            # Step number and icon
            step_icon = Label(
                text=f'{i+1}. {icon}', font_size=sp(12), 
                size_hint_x=None, width=dp(40),
                color=COLORS['secondary'], bold=True
            )
            step_box.add_widget(step_icon)
            
            # Step text
            step_text = Label(
                text=text, font_size=sp(11),
                color=COLORS['text_secondary'], 
                halign='left', text_size=(None, None)
            )
            step_text.bind(texture_size=step_text.setter('text_size'))
            step_box.add_widget(step_text)
            
            steps_layout.add_widget(step_box)
        
        self.instructions_scroll.add_widget(steps_layout)
        content.add_widget(self.instructions_scroll)
        
        # Quick action buttons
        action_box = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(35))
        
        help_btn = ModernButton(
            text='Need Help?', size_hint_x=0.5,
            bg_color=COLORS['accent'], icon='❓'
        )
        help_btn.bind(on_press=self.show_help)
        action_box.add_widget(help_btn)
        
        docs_btn = ModernButton(
            text='View Docs', size_hint_x=0.5,
            bg_color=COLORS['secondary'], icon='📚'
        )
        docs_btn.bind(on_press=self.show_documentation)
        action_box.add_widget(docs_btn)
        
        content.add_widget(action_box)
        
        card.add_widget(content)
        return card
    
    def clear_url(self, instance):
        self.url_input.text = ''
        self.update_status('URL cleared', 'info')
        
        # Animate clear action
        clear_anim = Animation(opacity=0.5, duration=0.1) + Animation(opacity=1, duration=0.1)
        clear_anim.start(self.url_input)
    
    def show_help(self, instance):
        """Show detailed help popup"""
        help_text = (
            "🔧 Troubleshooting Tips:\n\n"
            "• Ensure Cloudflare tunnel is running\n"
            "• Check firewall settings on target PC\n"
            "• Verify URL format includes '/shutdown'\n"
            "• Test connection before attempting shutdown\n\n"
            "🌐 URL Format Example:\n"
            "https://abc-def-ghi.trycloudflare.com/shutdown\n\n"
            "⚠️ Security Note:\n"
            "Only use on computers you own or have permission to control."
        )
        self.show_modern_popup("Help & Troubleshooting", help_text, "info")
    
    def show_documentation(self, instance):
        """Show documentation popup"""
        docs_text = (
            "📖 Documentation Overview:\n\n"
            "This app connects to a Cloudflare tunnel running\n"
            "on your target computer to send shutdown commands.\n\n"
            "🔐 Security Features:\n"
            "• Token-based authentication\n"
            "• HTTPS encrypted communication\n"
            "• Confirmation dialogs\n\n"
            "📱 Mobile Optimized:\n"
            "• Touch-friendly interface\n"
            "• Responsive design\n"
            "• Real-time status updates"
        )
        self.show_modern_popup("Documentation", docs_text, "info")
    
    def update_status(self, message, status_type='info', detail=None):
        """Update status with modern styling and animations"""
        def update_ui():
            self.status_label.text = message
            if detail and hasattr(self, 'status_detail'):
                self.status_detail.text = detail
            
            # Animate status indicator
            if status_type == 'success':
                self.status_indicator.color = COLORS['success']
                self.status_indicator.text = '✓'
                # Update signal bars for successful connection
                if hasattr(self, 'signal_bars'):
                    for i, bar in enumerate(self.signal_bars):
                        Clock.schedule_once(lambda dt, b=bar: setattr(b, 'opacity', 1), i * 0.1)
                        bar.color = COLORS['success']
            elif status_type == 'warning':
                self.status_indicator.color = COLORS['warning']
                self.status_indicator.text = '⚠'
                if hasattr(self, 'signal_bars'):
                    for bar in self.signal_bars[:2]:
                        bar.opacity = 1
                        bar.color = COLORS['warning']
                    for bar in self.signal_bars[2:]:
                        bar.opacity = 0.3
            elif status_type == 'error':
                self.status_indicator.color = COLORS['error']
                self.status_indicator.text = '✗'
                if hasattr(self, 'signal_bars'):
                    for bar in self.signal_bars:
                        bar.opacity = 0.3
                        bar.color = COLORS['text_disabled']
            else:
                self.status_indicator.color = COLORS['secondary']
                self.status_indicator.text = '●'
            
            # Pulse animation for status indicator
            pulse = Animation(font_size=dp(28), duration=0.2) + Animation(font_size=dp(24), duration=0.2)
            pulse.start(self.status_indicator)
        
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
        # Create modern confirmation dialog
        content = BoxLayout(orientation='vertical', spacing=dp(25), padding=dp(25))
        
        # Warning icon with animation
        icon_container = RelativeLayout(size_hint_y=None, height=dp(80))
        warning_icon = Label(
            text='⚠️', font_size=dp(60), 
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            color=COLORS['warning']
        )
        icon_container.add_widget(warning_icon)
        content.add_widget(icon_container)
        
        # Warning message with emphasis
        message_box = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(80))
        
        main_message = Label(
            text='Confirm Remote Shutdown',
            font_size=sp(18), color=COLORS['text_primary'],
            bold=True, halign='center'
        )
        main_message.bind(texture_size=main_message.setter('text_size'))
        message_box.add_widget(main_message)
        
        detail_message = Label(
            text='This will immediately shutdown the target computer.\nMake sure all work is saved.',
            font_size=sp(14), color=COLORS['text_secondary'],
            halign='center', text_size=(dp(280), None)
        )
        message_box.add_widget(detail_message)
        
        content.add_widget(message_box)
        
        # Enhanced button layout
        buttons = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint_y=None, height=dp(55))
        
        cancel_btn = ModernButton(
            text='Cancel', size_hint_x=0.45,
            bg_color=COLORS['text_disabled'], icon='✖'
        )
        
        confirm_btn = ModernButton(
            text='Shutdown Now', size_hint_x=0.55,
            bg_color=COLORS['error'], icon='⚡'
        )
        
        buttons.add_widget(cancel_btn)
        buttons.add_widget(confirm_btn)
        content.add_widget(buttons)
        
        # Create popup with custom styling
        popup = Popup(
            title='⚠️ Confirm Action', content=content, 
            size_hint=(0.9, 0.55), auto_dismiss=False,
            title_color=COLORS['warning'],
            separator_color=COLORS['warning'],
            background_color=COLORS['surface']
        )
        
        # Add entrance animation
        content.opacity = 0
        popup.bind(on_open=lambda x: Animation(opacity=1, duration=0.3).start(content))
        
        # Animate warning icon
        def animate_warning(*args):
            pulse = Animation(font_size=dp(65), duration=0.5) + Animation(font_size=dp(60), duration=0.5)
            pulse.repeat = True
            pulse.start(warning_icon)
        Clock.schedule_once(animate_warning, 0.5)
        
        cancel_btn.bind(on_press=lambda x: self.close_popup_with_animation(popup, content))
        confirm_btn.bind(on_press=lambda x: self.execute_shutdown_with_animation(popup, content))
        
        popup.open()
    
    def close_popup_with_animation(self, popup, content):
        """Close popup with fade animation"""
        fade_out = Animation(opacity=0, duration=0.2)
        fade_out.bind(on_complete=lambda *args: popup.dismiss())
        fade_out.start(content)
    
    def execute_shutdown_with_animation(self, popup, content):
        """Execute shutdown with animation"""
        self.close_popup_with_animation(popup, content)
        Clock.schedule_once(lambda dt: self.execute_shutdown_real(), 0.3)
    
    def execute_shutdown_real(self):
        """Execute the actual shutdown (renamed from execute_shutdown)"""
        self.update_status("Sending shutdown command...", "warning", "Please wait...")
        threading.Thread(target=self._shutdown_thread, daemon=True).start()
    
    def close_popup_with_animation(self, popup, content):
        """Close popup with fade animation"""
        fade_out = Animation(opacity=0, duration=0.2)
        fade_out.bind(on_complete=lambda *args: popup.dismiss())
        fade_out.start(content)
    
    def execute_shutdown_with_animation(self, popup, content):
        """Execute shutdown with animation"""
        self.close_popup_with_animation(popup, content)
        Clock.schedule_once(lambda dt: self.execute_shutdown_real(), 0.3)
    
    def execute_shutdown_real(self):
        """Execute the actual shutdown (renamed from execute_shutdown)"""
        self.update_status("Sending shutdown command...", "warning", "Please wait...")
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
        """Enhanced popup with better styling and animations"""
        content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(25))
        
        # Icon mapping with better emojis
        icons = {
            'success': '✅', 'error': '❌', 'warning': '⚠️', 
            'info': 'ℹ️', 'loading': '⏳'
        }
        icon_colors = {
            'success': COLORS['success'], 'error': COLORS['error'],
            'warning': COLORS['warning'], 'info': COLORS['secondary'],
            'loading': COLORS['accent']
        }
        
        # Animated icon container
        icon_container = RelativeLayout(size_hint_y=None, height=dp(70))
        icon_widget = Label(
            text=icons.get(popup_type, 'ℹ️'), font_size=dp(45),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            color=icon_colors.get(popup_type, COLORS['secondary'])
        )
        icon_container.add_widget(icon_widget)
        content.add_widget(icon_container)
        
        # Scrollable message area for longer text
        message_scroll = ScrollView(size_hint_y=None, height=dp(120))
        msg_label = Label(
            text=message, 
            text_size=(dp(280), None), halign='center',
            font_size=sp(14), color=COLORS['text_primary'],
            valign='top'
        )
        msg_label.bind(texture_size=msg_label.setter('text_size'))
        message_scroll.add_widget(msg_label)
        content.add_widget(message_scroll)
        
        # Enhanced OK button
        ok_btn = ModernButton(
            text='Got it!', size_hint_y=None, height=dp(50),
            bg_color=icon_colors.get(popup_type, COLORS['secondary']),
            icon='👍'
        )
        content.add_widget(ok_btn)
        
        # Create popup with modern styling
        popup = Popup(
            title=f"{icons.get(popup_type, 'ℹ️')} {title}",
            content=content, size_hint=(0.85, 0.6),
            title_color=icon_colors.get(popup_type, COLORS['secondary']),
            separator_color=icon_colors.get(popup_type, COLORS['secondary']),
            background_color=COLORS['surface']
        )
        
        # Entrance animation
        content.opacity = 0
        popup.bind(on_open=lambda x: Animation(opacity=1, duration=0.4).start(content))
        
        # Icon animation based on type
        if popup_type == 'loading':
            # Spinning animation for loading
            spin_anim = Animation(font_size=dp(50), duration=0.5) + Animation(font_size=dp(45), duration=0.5)
            spin_anim.repeat = True
            spin_anim.start(icon_widget)
        elif popup_type in ['success', 'error']:
            # Bounce animation for success/error
            bounce = Animation(font_size=dp(55), duration=0.3) + Animation(font_size=dp(45), duration=0.2)
            Clock.schedule_once(lambda dt: bounce.start(icon_widget), 0.2)
        
        ok_btn.bind(on_press=lambda x: self.close_popup_with_animation(popup, content))
        popup.open()


class MobileShutdownApp(App):
    def build(self):
        self.title = 'Remote Shutdown Controller'
        return MobileShutdownController()


if __name__ == '__main__':
    MobileShutdownApp().run()