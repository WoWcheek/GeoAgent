from LLM import *
import tkinter as tk
from tkinter import messagebox, simpledialog

class ModelSelectorDialog(simpledialog.Dialog):
    def body(self, master):
        self.var_gemini = tk.IntVar()
        self.var_openai = tk.IntVar()
        self.var_anthropic = tk.IntVar()
        self.selected_models = []

        tk.Label(master, text="Select LLM models:").grid(row=0, column=0, columnspan=2, pady=10)

        tk.Checkbutton(master, text=f"Gemini ({GEMINI_MODEL_NAME})", variable=self.var_gemini).grid(row=1, sticky="w")
        tk.Checkbutton(master, text=f"OpenAI ({OPENAI_MODEL_NAME})", variable=self.var_openai).grid(row=2, sticky="w")
        tk.Checkbutton(master, text=f"Anthropic ({ANTHROPIC_MODEL_NAME})", variable=self.var_anthropic).grid(row=3, sticky="w")

        return master

    def validate(self):
        if not (self.var_gemini.get() or self.var_openai.get() or self.var_anthropic.get()):
            messagebox.showerror("Error", "Please select at least one model.")
            return 0
        return 1

    def apply(self):
        if self.var_gemini.get():
            self.selected_models.append(LlmWrapper(Gemini, GEMINI_MODEL_NAME, GEMINI_PROMPT_FILE))
        if self.var_openai.get():
            self.selected_models.append(LlmWrapper(OpenAI, OPENAI_MODEL_NAME, OPEN_AI_PROMPT_FILE))
        if self.var_anthropic.get():
            self.selected_models.append(LlmWrapper(Anthropic, ANTHROPIC_MODEL_NAME, ANTHROPIC_PROMPT_FILE))