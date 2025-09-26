# controller_cloudflare.py
import tkinter as tk
from tkinter import messagebox, simpledialog
import requests
import urllib3
import threading
import time

# Disable SSL warnings when using verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# CONFIG - Update this URL when you get a new Cloudflare tunnel URL
TARGET_URL = "https://your-cloudflare-url.trycloudflare.com/shutdown"
ADMIN_TOKEN = "admin-shutdown-2024-token-secure"

class ShutdownController:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Remote Shutdown Controller (Cloudflare)")
        self.root.geometry("450x200")
        
        # URL input frame
        url_frame = tk.Frame(self.root)
        url_frame.pack(pady=10)
        
        tk.Label(url_frame, text="Target URL:", font=("Arial", 10, "bold")).pack()
        
        self.url_var = tk.StringVar(value=TARGET_URL)
        self.url_entry = tk.Entry(url_frame, textvariable=self.url_var, width=60)
        self.url_entry.pack(pady=5)
        
        tk.Button(url_frame, text="Update URL", command=self.update_url, bg="blue", fg="white").pack(pady=5)
        
        # Status frame
        status_frame = tk.Frame(self.root)
        status_frame.pack(pady=10)
        
        self.status_label = tk.Label(status_frame, text="Ready", fg="green", font=("Arial", 9))
        self.status_label.pack()
        
        # Button frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Test Connection", command=self.test_connection, 
                 bg="orange", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="SHUTDOWN TARGET", command=self.shutdown_remote, 
                 bg="red", fg="white", width=20, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Instructions
        instructions = tk.Text(self.root, height=4, width=55, wrap=tk.WORD)
        instructions.pack(pady=10)
        instructions.insert("1.0", 
            "Instructions:\n"
            "1. Run start_cloudflare.bat on the target machine\n"
            "2. Copy the Cloudflare URL from the terminal output\n"
            "3. Paste it above and add '/shutdown' to the end\n"
            "4. Click 'Test Connection' to verify, then 'SHUTDOWN TARGET'"
        )
        instructions.config(state=tk.DISABLED)
    
    def update_status(self, message, color="black"):
        self.status_label.config(text=message, fg=color)
        self.root.update()
    
    def update_url(self):
        new_url = simpledialog.askstring("Update URL", "Enter the new Cloudflare tunnel URL:", 
                                        initialvalue=self.url_var.get())
        if new_url:
            if not new_url.endswith('/shutdown'):
                if not new_url.endswith('/'):
                    new_url += '/shutdown'
                else:
                    new_url += 'shutdown'
            self.url_var.set(new_url)
            self.update_status("URL updated", "blue")
    
    def test_connection(self):
        self.update_status("Testing connection...", "orange")
        threading.Thread(target=self._test_connection_thread, daemon=True).start()
    
    def _test_connection_thread(self):
        try:
            url = self.url_var.get()
            if not url or url == TARGET_URL:
                self.update_status("Please update the URL first!", "red")
                return
            
            # Test basic connection to root
            base_url = url.replace('/shutdown', '/')
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            
            print(f"Testing connection to: {base_url}")
            response = requests.get(base_url, headers=headers, verify=False, timeout=10)
            
            if response.status_code == 200:
                self.update_status("✅ Connection successful! Ready to shutdown.", "green")
                print(f"Connection test passed: {response.status_code}")
                print(f"Response: {response.text[:100]}")
            else:
                self.update_status(f"⚠️ Got response code {response.status_code}", "orange")
                print(f"Response: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            self.update_status("❌ Connection failed - check URL/tunnel", "red")
            print("Connection error - tunnel may not be running")
        except Exception as e:
            self.update_status(f"❌ Error: {str(e)[:30]}...", "red")
            print(f"Test error: {e}")
    
    def shutdown_remote(self):
        result = messagebox.askyesno("Confirm Shutdown", 
                                   "Are you sure you want to shutdown the target machine?",
                                   icon="warning")
        if not result:
            return
        
        self.update_status("Sending shutdown command...", "orange")
        threading.Thread(target=self._shutdown_thread, daemon=True).start()
    
    def _shutdown_thread(self):
        try:
            url = self.url_var.get()
            if not url or url == TARGET_URL:
                self.update_status("Please update the URL first!", "red")
                messagebox.showerror("Error", "Please update the tunnel URL first!")
                return
            
            headers = {
                "Authorization": f"Bearer {ADMIN_TOKEN}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Content-Type": "application/json"
            }
            
            print(f"Sending shutdown command to: {url}")
            print(f"Headers: {headers}")
            
            response = requests.post(url, headers=headers, verify=False, timeout=10)
            
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")
            
            if response.status_code == 200:
                self.update_status("✅ Shutdown command sent successfully!", "green")
                messagebox.showinfo("Success", "Shutdown command accepted!")
            elif response.status_code == 401:
                self.update_status("❌ Unauthorized - wrong token", "red")
                messagebox.showerror("Unauthorized", "Invalid token.")
            else:
                self.update_status(f"❌ Error {response.status_code}", "red")
                messagebox.showerror("Failed", f"Error {response.status_code}: {response.text[:100]}")
                
        except requests.exceptions.ConnectionError:
            self.update_status("❌ Connection failed", "red")
            messagebox.showerror("Connection Error", "Could not connect to target. Check if tunnel is running.")
        except Exception as e:
            self.update_status("❌ Error occurred", "red")
            messagebox.showerror("Error", str(e))
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ShutdownController()
    app.run()