import tkinter as tk
from tkinter import messagebox

class Calculator(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Grade Calculator")
        self.main_container = tk.Frame(self, bg="light blue")
        self.main_container.pack(side="top",fill="both", expand=True)
        self.main_container.grid_rowconfigure(0, weight=0)
        self.main_container.grid_columnconfigure(0, weight=1)

        tk.Label(self.main_container, text="Grade (in %)                Weight").grid(sticky="new")
        self.grades_n_weights = []
        self.lower_bar_init()

        self.geometry("400x500")
        
    def addRow(self,category,weight):
        frame = tk.Frame(self.main_container)
        frame.grid(sticky="new")
        tk.Label(frame, text=category).pack(side="left")

        grade = tk.Entry(frame)
        grade.pack(side="left", fill="x", expand=True)
        grade_weight = tk.Entry(frame)
        grade_weight.pack(side="left", fill="x", expand=True)
        grade_weight.insert(0, weight)
        
        grade_n_weight = (grade,grade_weight)
        self.grades_n_weights.append(grade_n_weight)

        delbt = tk.Button(frame, text = "Del", command = lambda : self.removeBox(frame, grade_n_weight))
        delbt.pack(side="left")
    
    def removeBox(self,frame, grade_n_weight):
        self.grades_n_weights.remove(grade_n_weight)
        frame.destroy()

    def lower_bar_init(self):
        frame = tk.Frame(self, height=50)
        frame.pack(side="bottom")
        addbt = tk.Button(frame, text = "Add row", command = lambda: self.addRow(len(self.grades_n_weights)+1, 0))
        addbt.pack(side="left")
        calcbt = tk.Button(frame, text = "Calculate", command = self.calculate_grade)
        calcbt.pack(side="left")
        self.overall = tk.Entry(frame)
        self.overall.pack(side="right")

    def calculate_grade(self):
        res = 0
        try:
            for grade, weight in self.grades_n_weights:
                    res += float(grade.get()) * float(weight.get())
        except ValueError:
            messagebox.showinfo("Error Message", "Missing Grade/Weight")
            return
        res /= 10000
        self.overall.delete(0,tk.END)
        self.overall.insert(0, str(res))

def main():
  app = Calculator()
  app.addRow("Test","50")
  app.addRow("HW","30")
  app.addRow("Lab", "20")
  app.mainloop()

if __name__ == "__main__":
  main()