import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedTk
from PyPDF2 import PdfMerger


class PDFCombinerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Combinador de PDFs con ttkthemes")
        self.root.geometry("600x450")
        self.pdf_files = []

        # Usamos el ThemedStyle para aplicar el tema
        self.style = ttk.Style(self.root)
        # El tema ya fue aplicado en ThemedTk al iniciar la ventana
        # Puedes verificar el tema activo con:
        # print(self.style.theme_use())

        # Marco principal
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill="both", expand=True)

        # Etiqueta título
        title_label = ttk.Label(main_frame, text="Lista de PDFs a combinar:")
        title_label.pack(pady=(0, 10))

        # Listbox con scroll
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(
            list_frame,
            selectmode=tk.SINGLE,
            font=("Consolas", 11),
            height=12,
            bd=2,
            relief="ridge",
        )
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.listbox.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Frame botones
        btn_frame = ttk.Frame(main_frame, padding=(0, 10, 0, 0))
        btn_frame.pack()

        ttk.Button(btn_frame, text="Agregar PDFs", command=self.agregar_pdfs).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(
            btn_frame, text="Eliminar Seleccionado", command=self.eliminar_seleccionado
        ).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Subir", command=self.mover_arriba).grid(
            row=0, column=2, padx=5
        )
        ttk.Button(btn_frame, text="Bajar", command=self.mover_abajo).grid(
            row=0, column=3, padx=5
        )
        ttk.Button(btn_frame, text="Combinar PDFs", command=self.combinar_pdfs).grid(
            row=0, column=4, padx=5
        )

    def agregar_pdfs(self):
        archivos = filedialog.askopenfilenames(
            title="Selecciona archivos PDF", filetypes=[("Archivos PDF", "*.pdf")]
        )
        for archivo in archivos:
            if archivo not in self.pdf_files:
                self.pdf_files.append(archivo)
                self.listbox.insert(tk.END, archivo)

    def eliminar_seleccionado(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning(
                "Advertencia", "Debes seleccionar un archivo para eliminar."
            )
            return
        idx = sel[0]
        self.pdf_files.pop(idx)
        self.listbox.delete(idx)

    def mover_arriba(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == 0:
            return
        idx = sel[0]
        self.pdf_files[idx - 1], self.pdf_files[idx] = (
            self.pdf_files[idx],
            self.pdf_files[idx - 1],
        )
        self.refrescar_lista()
        self.listbox.select_set(idx - 1)

    def mover_abajo(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == len(self.pdf_files) - 1:
            return
        idx = sel[0]
        self.pdf_files[idx + 1], self.pdf_files[idx] = (
            self.pdf_files[idx],
            self.pdf_files[idx + 1],
        )
        self.refrescar_lista()
        self.listbox.select_set(idx + 1)

    def refrescar_lista(self):
        self.listbox.delete(0, tk.END)
        for archivo in self.pdf_files:
            self.listbox.insert(tk.END, archivo)

    def combinar_pdfs(self):
        if len(self.pdf_files) < 2:
            messagebox.showwarning(
                "Advertencia", "Debes agregar al menos dos PDFs para combinar."
            )
            return
        output_file = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")],
            title="Guardar PDF combinado como",
        )
        if not output_file:
            return
        merger = PdfMerger()
        try:
            for pdf in self.pdf_files:
                with open(pdf, "rb") as f:
                    merger.append(f)
            merger.write(output_file)
            merger.close()
            messagebox.showinfo(
                "Éxito", f"PDFs combinados exitosamente en:\n{output_file}"
            )
        except Exception as e:
            messagebox.showerror(
                "Error", f"Ocurrió un error al combinar los PDFs:\n{e}"
            )


if __name__ == "__main__":
    root = ThemedTk(
        theme="arc"
    )  # Puedes probar otros temas como 'breeze', 'plastik', 'equilux', 'winxpblue', etc.
    app = PDFCombinerApp(root)
    root.mainloop()
