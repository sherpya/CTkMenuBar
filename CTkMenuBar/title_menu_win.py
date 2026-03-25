"""
Menu Bar in Title Bar of customtkinter window
Author: Akash Bora
"""

import customtkinter
import sys
import tkinter as tk

class CTkTitleMenu(customtkinter.CTkToplevel):
    """
    A custom title bar menu widget for Windows CustomTkinter applications.
    
    This class creates a transparent overlay window that displays a menu bar
    in the title bar area of the parent window. It only works on Windows platform
    and provides a modern, integrated menu experience.
    
    The menu automatically adjusts its position and size based on the parent window,
    and can modify the Windows title bar color for a cohesive appearance.
    
    Attributes:
        master: The parent window (must be root or toplevel)
        menu (list): List of associated dropdown menus
        caption_color: Color of the Windows title bar
        transparent_color: Color used for transparency
        x_offset (int): Horizontal offset from window edge
        y_offset (int): Vertical offset from window top
        width (int): Width of menu buttons
        padding (int): Padding between menu buttons
        num (int): Counter for menu items added
    
    Raises:
        OSError: If not running on Windows platform
        TypeError: If master is not a root window or toplevel
    """
        
    def __init__(
        self,
        master,
        title_bar_color = "default",
        padx: int = 10,
        width: int = 10,
        x_offset: int = None,
        y_offset: int = None):
        """
        Initialize a CTkTitleMenu instance.
        
        Creates a transparent overlay window that positions a menu bar in the
        title bar area of the parent window. Only works on Windows platform.
        
        Args:
            master: The parent window (must be root window or toplevel)
            title_bar_color: Color for the Windows title bar. Can be "default" 
                           for automatic theme-based color, or a hex color value
            padx (int): Horizontal padding between menu buttons. Defaults to 10
            width (int): Width of individual menu buttons. Defaults to 10
            x_offset (int, optional): Horizontal offset from window edge. 
                                    Auto-calculated based on title if None
            y_offset (int, optional): Vertical offset from window top. 
                                    Defaults to 6 if None
                                    
        Raises:
            OSError: If not running on Windows platform
            TypeError: If master is not a root window or toplevel
        """
        
        super().__init__()

        if not sys.platform.startswith("win"):
            raise OSError("This title menu works only in windows platform, not supported on your system! \nTry the CTkMenuBar instead...")
        
        self.after(10)
        self.master = master
        self._master_bind_ids = {}
        master_type = self.master.winfo_name()
        
        if master_type=="tk":
            pass
        elif master_type.startswith("!ctktoplevel"):
            pass
        elif master_type.startswith("!toplevel"):
            pass 
        elif isinstance(self.master, customtkinter.CTkToplevel):
            pass        
        elif isinstance(self.master, tk.Toplevel):
            pass       
        else:
            raise TypeError("Only root windows/toplevels can be passed as the master!")
        
        self.master.minsize(200,100)
        self.after(100, lambda: self.overrideredirect(True))
        
        if title_bar_color=="default":
            if customtkinter.get_appearance_mode()=="Light":
                title_bar_color = 0xFFFFFF # RGB order: 0xrrggbb             
            else:
                title_bar_color = 0x303030 # RGB order: 0xrrggbb
                
        self.transparent_color = self._apply_appearance_mode(self._fg_color)
        self.attributes("-transparentcolor", self.transparent_color)
        self.resizable(True, True)
        self.transient(self.master)
        self.menu = []

        self.config(background=self.transparent_color)
        self.caption_color = title_bar_color
        self.change_header_color(self.caption_color)
        self.x_offset = 40 if x_offset is None else x_offset
        self.y_offset = 6 if y_offset is None else y_offset
        self.width = width
        if x_offset is None:
            title = self.master.title()
            if len(title)>=1:
                for i in title:
                    if i.islower():
                        self.x_offset += 9
                    else:
                        self.x_offset += 7
            
        self.padding = padx

        self._master_bind_ids["<Configure>"] = self.master.bind("<Configure>", self._on_master_configure, add="+")
        self._master_bind_ids["<Destroy>"] = self.master.bind("<Destroy>", self._on_master_destroy, add="+")
        self.num = 0
        self._master_bind_ids["<Map>"] = self.master.bind("<Map>", self._on_master_map, add="+")
        self._master_bind_ids["<Unmap>"] = self.master.bind("<Unmap>", self._on_master_unmap, add="+")

    def _on_master_configure(self, _event=None):
        if _event is not None and _event.widget is not self.master:
            return
        self.change_dimension()

    def _on_master_destroy(self, _event=None):
        if _event is not None and _event.widget is not self.master:
            return
        try:
            if not self.master.winfo_viewable():
                self.destroy_window()
        except tk.TclError:
            self.destroy_window()

    def _on_master_map(self, _event=None):
        if _event is not None and _event.widget is not self.master:
            return
        try:
            self.deiconify()
            self.change_dimension()
        except tk.TclError:
            pass

    def _on_master_unmap(self, _event=None):
        if _event is not None and _event.widget is not self.master:
            return
        try:
            self.withdraw()
        except tk.TclError:
            pass

    def _unbind_master_events(self):
        for sequence, bind_id in self._master_bind_ids.items():
            try:
                self.master.unbind(sequence, bind_id)
            except (tk.TclError, AttributeError):
                pass
        self._master_bind_ids.clear()

    def destroy_window(self):
        """
        Destroy the title menu window.
        """
        self._unbind_master_events()
        if not self.winfo_exists():
            return
        super().destroy()

    def destroy(self):
        self._unbind_master_events()
        if self.winfo_exists():
            super().destroy()

    def _set_appearance_mode(self, mode_string):
        """
        Update the title bar color based on the current appearance mode.
        
        This method is called when the appearance mode changes between light and dark themes.
        It automatically adjusts the Windows title bar color to match the current theme.
        
        Args:
            mode_string (str): The appearance mode string (not currently used in implementation)
        """
        if customtkinter.get_appearance_mode()=="Light":
            self.caption_color = 0xFFFFFF # RGB order: 0xrrggbb             
        else:
            self.caption_color = 0x303030 # RGB order: 0xrrggbb

        self.change_header_color(self.caption_color)
        
    def add_cascade(self, text=None, postcommand=None, **kwargs):
        """
        Add a menu button to the title bar menu.
        
        Creates and adds a new menu button to the title bar with customizable
        appearance and behavior. The button is automatically positioned in
        the next available column within the title bar area.
        
        Args:
            text (str, optional): The text label for the menu button.
                                If None, defaults to "Tab {number}"
            postcommand (callable, optional): Callback function to execute
                                            when the button is clicked
            **kwargs: Additional configuration options for the button including:
                - fg_color: Foreground/background color of the button
                - text_color: Color of the button text
                - Other CTkButton configuration options
                
        Returns:
            customtkinter.CTkButton: The created menu button widget
        """
    
        if not "fg_color" in kwargs:
            fg_color = customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"]
        else:
            fg_color = kwargs.pop("fg_color")
        if not "text_color" in kwargs:
            text_color = customtkinter.ThemeManager.theme["CTkLabel"]["text_color"]
        else:
            text_color = kwargs.pop("text_color")
            
        if text is None:
            text = f"Tab {self.num+1}"
    
        self.menu_button = customtkinter.CTkButton(self, text=text, fg_color=fg_color,
                                                   text_color=text_color, width=self.width, height=10, **kwargs)
        self.menu_button.grid(row=0, column=self.num, padx=(0, self.padding))
        self.num += 1

        if postcommand:
            self.menu_button.bind("<Button-1>", lambda event: postcommand(), add="+")
            
        return self.menu_button
    
    def change_dimension(self):
        """
        Update the menu's position and size to match the parent window.
        
        This method is called whenever the parent window is resized, moved, or its state changes.
        It automatically adjusts the overlay window's geometry to stay aligned with the title bar
        and hides the menu when the window is minimized or too small.
        
        The method handles different window states:
        - Normal: Standard positioning
        - Maximized ("zoomed"): Adjusted positioning for maximized windows
        - Minimized ("iconic"): Hides the menu
        - Too small: Hides the menu if width becomes negative
        """
        try:
            if not self.winfo_exists() or not self.master.winfo_exists():
                return
        except tk.TclError:
            return

        width = self.master.winfo_width()-130-self.x_offset
        if width<0:
            self.withdraw()
            return
        if self.master.state()=="iconic":
            self.withdraw()
            return
        height = self.master.winfo_height()
        x = self.master.winfo_x()+self.x_offset
        y = self.master.winfo_y()+self.y_offset
        if self.master.state()=="zoomed":
            y += 4
            x -= 7
        try:
            self.geometry(f"{width}x{height}+{x}+{y}")
            self.deiconify()
        except tk.TclError:
            return
 
    def change_header_color(self, caption_color):
        """
        Change the Windows title bar color using Windows API.
        
        This method uses Windows DWM (Desktop Window Manager) API to modify
        the title bar color of the parent window. This provides a native
        integration with the Windows window styling system.
        
        Args:
            caption_color (int): The color value in hexadecimal format (0xRRGGBB)
                               for the title bar background
                               
        Note:
            This method silently fails on non-Windows platforms or if the
            required Windows API is not available. The try-except block
            ensures the application continues to work even if the API call fails.
        """
        try:
            from ctypes import windll, byref, sizeof, c_int
            # optional feature to change the header in windows 11
            HWND = windll.user32.GetParent(self.master.winfo_id())
            DWMWA_CAPTION_COLOR = 35
            windll.dwmapi.DwmSetWindowAttribute(HWND, DWMWA_CAPTION_COLOR, byref(c_int(caption_color)), sizeof(c_int))
        except: None
