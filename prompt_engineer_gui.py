import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import json
import os
import sys
import threading
from prompt_engineer import PromptEngineer

class PromptEngineerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("智能提示工程师")
        self.root.geometry("900x700")
        self.root.configure(padx=20, pady=20)
        
        # Initialize variables before setup
        self.api_key_var = tk.StringVar()
        self.provider_var = tk.StringVar(value="deepseek")
        self.model_var = tk.StringVar(value="deepseek-chat")
        self.format_var = tk.StringVar(value="standard")
        
        self.setup_styles()
        self.load_config()
        self.create_widgets()
        
        # Default values
        self.examples = []
    
    def setup_styles(self):
        """Set up styles for the application"""
        self.root.tk.call("source", "azure.tcl") if os.path.exists("azure.tcl") else None
        self.root.tk.call("set_theme", "light") if os.path.exists("azure.tcl") else None
        
        # Configure style
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 11))
        style.configure("TButton", font=("Helvetica", 11))
        style.configure("TRadiobutton", font=("Helvetica", 11))
        style.configure("TEntry", font=("Helvetica", 11))
        style.configure("TCombobox", font=("Helvetica", 11))
    
    def load_config(self):
        """Load configuration from config.json if available"""
        config_file = "config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                # Set variables from config
                if "api_key" in config:
                    self.api_key_var.set(config["api_key"])
                
                if "api_provider" in config:
                    self.provider_var.set(config["api_provider"])
                
                if "model" in config:
                    self.model_var.set(config["model"])
                
                if "default_format" in config:
                    self.format_var.set(config["default_format"])
                
                # Log successful config load
                print(f"配置已从 {config_file} 加载")
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                # If config can't be loaded, try environment variable
                self.load_api_key_from_env()
        else:
            # If no config file, try environment variable
            self.load_api_key_from_env()
    
    def load_api_key_from_env(self):
        """Load API key from environment variable if available"""
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if api_key:
            self.api_key_var.set(api_key)
    
    def save_config(self):
        """Save current configuration to config.json"""
        config = {
            "api_key": self.api_key_var.get(),
            "api_provider": self.provider_var.get(),
            "model": self.model_var.get(),
            "default_format": self.format_var.get()
        }
        
        try:
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            self.status_var.set("配置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def create_widgets(self):
        """Create all the widgets for the application"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel (inputs)
        input_frame = ttk.LabelFrame(main_frame, text="输入设置")
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Right panel (output)
        output_frame = ttk.LabelFrame(main_frame, text="生成的提示")
        output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create input widgets
        self.create_input_widgets(input_frame)
        
        # Create output widgets
        self.create_output_widgets(output_frame)
    
    def create_input_widgets(self, parent):
        """Create input widgets"""
        # Requirement input
        ttk.Label(parent, text="需求:").pack(anchor=tk.W, pady=(10, 5))
        self.requirement_text = scrolledtext.ScrolledText(parent, height=6, width=40, wrap=tk.WORD)
        self.requirement_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Format selection
        ttk.Label(parent, text="格式:").pack(anchor=tk.W, pady=(10, 5))
        formats = {
            "标准": "standard",
            "专家讨论": "expert-panel",
            "带示例": "examples"
        }
        
        format_frame = ttk.Frame(parent)
        format_frame.pack(fill=tk.X, pady=(0, 10))
        
        for i, (text, value) in enumerate(formats.items()):
            ttk.Radiobutton(
                format_frame, 
                text=text, 
                value=value, 
                variable=self.format_var, 
                command=self.toggle_examples_frame
            ).pack(side=tk.LEFT, padx=(0 if i == 0 else 10, 0))
        
        # Examples frame (initially hidden)
        self.examples_frame = ttk.Frame(parent)
        self.examples_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            self.examples_frame, 
            text="加载示例文件", 
            command=self.load_examples
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.examples_label = ttk.Label(self.examples_frame, text="未加载示例")
        self.examples_label.pack(side=tk.LEFT)
        
        # Hide examples frame if not selected
        if self.format_var.get() != "examples":
            self.examples_frame.pack_forget()
        
        # API settings
        api_frame = ttk.LabelFrame(parent, text="API设置")
        api_frame.pack(fill=tk.X, pady=(10, 10))
        
        # API Provider
        provider_frame = ttk.Frame(api_frame)
        provider_frame.pack(fill=tk.X, pady=(5, 5))
        
        ttk.Label(provider_frame, text="API提供商:").pack(side=tk.LEFT)
        ttk.Combobox(
            provider_frame, 
            textvariable=self.provider_var, 
            values=["openai", "deepseek"], 
            state="readonly", 
            width=15
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # API Model
        model_frame = ttk.Frame(api_frame)
        model_frame.pack(fill=tk.X, pady=(5, 5))
        
        ttk.Label(model_frame, text="模型:").pack(side=tk.LEFT)
        
        models = {
            "openai": ["gpt-3.5-turbo", "gpt-4"],
            "deepseek": ["deepseek-chat", "deepseek-coder"]
        }
        
        self.model_combo = ttk.Combobox(
            model_frame, 
            textvariable=self.model_var, 
            values=models.get(self.provider_var.get(), ["deepseek-chat"]), 
            state="readonly", 
            width=20
        )
        self.model_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Update model options when provider changes
        self.provider_var.trace("w", lambda *args: self.update_model_options())
        
        # API Key
        key_frame = ttk.Frame(api_frame)
        key_frame.pack(fill=tk.X, pady=(5, 5))
        
        ttk.Label(key_frame, text="API密钥:").pack(side=tk.LEFT)
        self.api_key_entry = ttk.Entry(key_frame, textvariable=self.api_key_var, width=40, show="*")
        self.api_key_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # Show/hide password
        self.show_key_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            key_frame, 
            text="显示", 
            variable=self.show_key_var, 
            command=self.toggle_key_visibility
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Save configuration button
        ttk.Button(
            api_frame,
            text="保存配置",
            command=self.save_config
        ).pack(anchor=tk.E, pady=(5, 0))
        
        # Generate button
        ttk.Button(
            parent, 
            text="生成提示", 
            command=self.generate_prompt, 
            style="Accent.TButton"
        ).pack(fill=tk.X, pady=(20, 0))
        
        # Status label
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(parent, textvariable=self.status_var).pack(anchor=tk.W, pady=(10, 0))
    
    def create_output_widgets(self, parent):
        """Create output widgets"""
        # Output text
        self.output_text = scrolledtext.ScrolledText(parent, height=25, width=50, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=(10, 10))
        
        # Buttons frame
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame, 
            text="复制到剪贴板", 
            command=self.copy_to_clipboard
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            button_frame, 
            text="保存到文件", 
            command=self.save_to_file
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(
            button_frame, 
            text="清除", 
            command=self.clear_output
        ).pack(side=tk.LEFT, padx=(10, 0))
    
    def toggle_examples_frame(self):
        """Show or hide the examples frame based on format selection"""
        if self.format_var.get() == "examples":
            self.examples_frame.pack(fill=tk.X, pady=(0, 10))
        else:
            self.examples_frame.pack_forget()
    
    def update_model_options(self):
        """Update model options based on the selected provider"""
        provider = self.provider_var.get()
        models = {
            "openai": ["gpt-3.5-turbo", "gpt-4"],
            "deepseek": ["deepseek-chat", "deepseek-coder"]
        }
        self.model_combo["values"] = models.get(provider, [])
        if self.model_var.get() not in models.get(provider, []):
            self.model_var.set(models.get(provider, [""])[0])
    
    def toggle_key_visibility(self):
        """Toggle API key visibility"""
        self.api_key_entry["show"] = "" if self.show_key_var.get() else "*"
    
    def load_examples(self):
        """Load examples from a JSON file"""
        file_path = filedialog.askopenfilename(
            title="选择示例文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.examples = json.load(f)
            
            self.examples_label["text"] = f"已加载 {len(self.examples)} 个示例"
        except Exception as e:
            messagebox.showerror("错误", f"加载示例文件失败: {e}")
    
    def generate_prompt(self):
        """Generate a prompt based on user inputs"""
        requirement = self.requirement_text.get("1.0", tk.END).strip()
        
        if not requirement:
            messagebox.showwarning("警告", "请输入需求")
            return
        
        api_key = self.api_key_var.get()
        if not api_key:
            messagebox.showwarning("警告", "请输入API密钥")
            return
        
        self.status_var.set("正在生成提示...")
        self.root.update_idletasks()
        
        # Run in a separate thread to avoid freezing the UI
        threading.Thread(target=self._generate_prompt_thread, args=(requirement, api_key), daemon=True).start()
    
    def _generate_prompt_thread(self, requirement, api_key):
        """Thread function to generate prompt"""
        try:
            prompt_format = self.format_var.get()
            provider = self.provider_var.get()
            model = self.model_var.get()
            
            # Initialize the prompt engineer
            prompt_engineer = PromptEngineer(
                api_key=api_key,
                model_name=model,
                api_provider=provider
            )
            
            # Generate prompt based on selected format
            if prompt_format == "standard":
                prompt = prompt_engineer.generate_formatted_prompt(requirement)
            elif prompt_format == "expert-panel":
                prompt = prompt_engineer.generate_expert_panel_prompt(requirement)
            elif prompt_format == "examples":
                if not self.examples:
                    # Use default examples if none loaded
                    self.examples = [
                        {"input": "写一首关于自然的诗", "output": "树木轻轻摇曳..."},
                        {"input": "解释量子物理", "output": "量子物理是研究..."}
                    ]
                prompt = prompt_engineer.generate_prompt_with_examples(requirement, self.examples)
            
            # Update UI in the main thread
            self.root.after(0, self._update_output, prompt)
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
    
    def _update_output(self, prompt):
        """Update the output text area with the generated prompt"""
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, prompt)
        self.status_var.set("提示生成完成")
    
    def _show_error(self, error_msg):
        """Show error message"""
        messagebox.showerror("错误", f"生成提示时出错: {error_msg}")
        self.status_var.set("出错")
    
    def copy_to_clipboard(self):
        """Copy the output to clipboard"""
        output = self.output_text.get("1.0", tk.END).strip()
        if output:
            self.root.clipboard_clear()
            self.root.clipboard_append(output)
            self.status_var.set("已复制到剪贴板")
        else:
            messagebox.showinfo("信息", "没有内容可复制")
    
    def save_to_file(self):
        """Save the output to a file"""
        output = self.output_text.get("1.0", tk.END).strip()
        if not output:
            messagebox.showinfo("信息", "没有内容可保存")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存提示",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(output)
            self.status_var.set(f"已保存到 {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("错误", f"保存文件失败: {e}")
    
    def clear_output(self):
        """Clear the output text"""
        self.output_text.delete("1.0", tk.END)
        self.status_var.set("已清除输出")


def main():
    # Create the root window
    root = tk.Tk()
    app = PromptEngineerGUI(root)
    
    # Set default API key from command line if provided
    if len(sys.argv) > 1:
        app.api_key_var.set(sys.argv[1])
    
    # Start the main loop
    root.mainloop()


if __name__ == "__main__":
    main() 