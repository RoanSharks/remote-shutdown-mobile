#!/usr/bin/env python3
"""
Simple controller to test tunnel restart functionality via Cloudflare tunnel
"""
import tkinter as tk
from tkinter import messagebox, simpledialog
import requests
import urllib3
import threading

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN = "admin-shutdown-2024-token-secure"

class TunnelTestController:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tunnel Restart Test Controller")
        self.root.geometry("500x400")
        
        # URL input frame
        url_frame = tk.Frame(self.root)
        url_frame.pack(pady=10)
        
        tk.Label(url_frame, text="Cloudflare Tunnel URL:", font=("Arial", 10, "bold")).pack()
        
        self.url_var = tk.StringVar(value="https://your-tunnel-url.trycloudflare.com")
        self.url_entry = tk.Entry(url_frame, textvariable=self.url_var, width=60)
        self.url_entry.pack(pady=5)
        
        # Status frame
        status_frame = tk.Frame(self.root)
        status_frame.pack(pady=10)
        
        self.status_label = tk.Label(status_frame, text="Ready to test", fg="blue", font=("Arial", 9))
        self.status_label.pack()
        
        # Test buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        # Row 1
        row1 = tk.Frame(button_frame)
        row1.pack(pady=5)
        
        tk.Button(row1, text="Test Connection", command=self.test_connection, 
                 bg="blue", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(row1, text="Restart Tunnel", command=self.restart_tunnel, 
                 bg="orange", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        
        # Row 2
        row2 = tk.Frame(button_frame)
        row2.pack(pady=5)
        
        tk.Button(row2, text="Test 'reboot'", command=lambda: self.test_command("reboot"), 
                 bg="green", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(row2, text="Test 'status'", command=lambda: self.test_command("status"), 
                 bg="green", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        
        # Row 3
        row3 = tk.Frame(button_frame)
        row3.pack(pady=5)
        
        tk.Button(row3, text="Custom Command", command=self.custom_command, 
                 bg="purple", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(row3, text="SHUTDOWN (BE CAREFUL!)", command=self.test_shutdown, 
                 bg="red", fg="white", width=20, font=("Arial", 8, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Instructions
        instructions = tk.Text(self.root, height=8, width=65, wrap=tk.WORD)
        instructions.pack(pady=10)
        instructions.insert("1.0", 
            "Instructions:\n"
            "1. Make sure your Flask agent is running with the new tunnel restart code\n"
            "2. Update the Cloudflare tunnel URL above\n"
            "3. Click 'Test Connection' to verify the tunnel is working\n"
            "4. Try 'Restart Tunnel' to explicitly restart the tunnel\n"
            "5. Try other commands like 'reboot' or 'status' - these should also restart the tunnel\n"
            "6. Use 'Custom Command' to test any endpoint you want\n\n"
            "⚠️ The SHUTDOWN button will actually shut down the target PC!\n"
            "📋 All commands except 'shutdown' will restart the tunnel"
        )
        instructions.config(state=tk.DISABLED)
    
    def update_status(self, message, color="black"):
        self.status_label.config(text=message, fg=color)
        self.root.update()
    
    def make_request(self, endpoint, description):
        """Make a request to the specified endpoint"""
        base_url = self.url_var.get().rstrip('/')
        url = f"{base_url}/{endpoint}" if endpoint else base_url
        
        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        }
        
        self.update_status(f"Testing {description}...", "orange")
        
        try:
            if endpoint == "":
                response = requests.get(url, headers=headers, verify=False, timeout=10)
            else:
                response = requests.post(url, headers=headers, verify=False, timeout=10)
            
            if response.status_code == 200:
                self.update_status(f"✅ {description} successful!", "green")
                messagebox.showinfo("Success", f"{description} successful!\n\nResponse: {response.json().get('message', 'No message')}")
            else:
                self.update_status(f"❌ {description} failed: {response.status_code}", "red")
                messagebox.showerror("Error", f"{description} failed!\n\nStatus: {response.status_code}\nResponse: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            self.update_status("❌ Connection failed", "red")
            messagebox.showerror("Connection Error", "Could not connect to tunnel. Check the URL.")
        except Exception as e:
            self.update_status("❌ Error occurred", "red")
            messagebox.showerror("Error", str(e))
    
    def test_connection(self):
        threading.Thread(target=lambda: self.make_request("", "Connection test"), daemon=True).start()
    
    def restart_tunnel(self):
        threading.Thread(target=lambda: self.make_request("restart-tunnel", "Tunnel restart"), daemon=True).start()
    
    def test_command(self, command):
        threading.Thread(target=lambda: self.make_request(command, f"Command '{command}' (should restart tunnel)"), daemon=True).start()
    
    def custom_command(self):
        command = simpledialog.askstring("Custom Command", "Enter command to test:")
        if command:
            threading.Thread(target=lambda: self.make_request(command, f"Custom command '{command}'"), daemon=True).start()
    
    def test_shutdown(self):
        result = messagebox.askyesno("⚠️ DANGER ⚠️", 
                                   "This will ACTUALLY SHUTDOWN the target PC!\n\n"
                                   "Are you absolutely sure you want to proceed?",
                                   icon="warning")
        if result:
            result2 = messagebox.askyesno("⚠️ FINAL WARNING ⚠️", 
                                         "This is your LAST CHANCE!\n\n"
                                         "The target PC will shutdown immediately!\n"
                                         "Click YES only if you're sure!",
                                         icon="warning")
            if result2:
                threading.Thread(target=lambda: self.make_request("shutdown", "SHUTDOWN"), daemon=True).start()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TunnelTestController()
    app.run()