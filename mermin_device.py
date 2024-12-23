import tkinter as tk
import cirq
import math

def run_function():
    global d1, d2, history
    a = d1.get()/3
    b = d2.get()/3

    q_A = cirq.NamedQubit('A')
    q_B = cirq.NamedQubit('B')

    crt = cirq.Circuit()
    crt.append(cirq.X(q_A))
    crt.append(cirq.H(q_A))
    crt.append(cirq.CNOT(q_A, q_B))
    crt.append(cirq.X(q_A)**a)
    crt.append(cirq.X(q_B)**b)
    crt.append(cirq.measure(q_A, key='A'))
    crt.append(cirq.measure(q_B, key='B'))

    #print(f"Circuit:\n{crt}")

    sim = cirq.Simulator()
    result = sim.run(crt)

    A = result.measurements['A'][0][0]
    B = result.measurements['B'][0][0]

    d1.indicator['bg'] = d1.colors[A]
    d2.indicator['bg'] = d2.colors[B]

    history.insert(tk.END, f'{d1.get()}, {d2.get()}, {d1.colors[A]}, {d1.colors[B]}')

history_visible=False
def history_func():
    global history_button, history_visible, history
    if (history_visible):
        history.pack_forget()
        scroll.pack_forget()
        history_button['text']='History >>'
    else:
        history.pack(side=tk.LEFT)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        history_button['text'] = 'History <<'
    history_visible = not history_visible



tk_root=tk.Tk()
tk_root.title("Mermin's Device")

class Detector:
    def __init__(self, main_frame, name):
        self.colors = ('red', 'green')
        self.frame=tk.LabelFrame(main_frame, text=name)
        self.indicator=tk.Label(self.frame,width=10, height=8,borderwidth=2, relief="groove")
        self.indicator.pack()
        self.dir=tk.IntVar()
        self.dir.set(0)
        [tk.Radiobutton(self.frame, text=f'{i}', variable=self.dir, value=i).pack(anchor=tk.W) for i in range(1,4)]

    def get(self):
        return self.dir.get()


main_frame=tk.Frame()
main_frame.pack(side=tk.LEFT)

upper_frame=tk.Frame(main_frame)
upper_frame.pack(side=tk.TOP)

d1=Detector(upper_frame, 'Detector 1')
d1.frame.pack(side=tk.LEFT)

c_size=200
sq_size=c_size//10
canvas=tk.Canvas(upper_frame, width=c_size, height=c_size)
canvas.pack(side=tk.LEFT)
canvas.create_rectangle(c_size//2-sq_size,c_size//2-sq_size,c_size//2+sq_size,c_size//2+sq_size)
canvas.create_line(c_size//2-sq_size,c_size//2-sq_size,c_size//2+sq_size,c_size//2+sq_size)
canvas.create_line(c_size//2-sq_size,c_size//2+sq_size,c_size//2+sq_size,c_size//2-sq_size)
canvas.create_line(0,c_size//2,c_size//2-sq_size,c_size//2)
canvas.create_line(c_size//2+sq_size,c_size//2,c_size, c_size//2)


d2=Detector(upper_frame, 'Detector 2')
d2.frame.pack(side=tk.RIGHT)

lower_frame=tk.Frame(main_frame)
lower_frame.pack(side=tk.BOTTOM)

tk.Label(lower_frame, width=8).pack(side=tk.LEFT)
run_button=tk.Button(lower_frame, text='Run', width=7, command=run_function)
run_button.pack(side=tk.LEFT)
tk.Label(lower_frame, width=8).pack(side=tk.LEFT)
history_button=tk.Button(lower_frame, text='History >>', command=history_func)
history_button.pack(side=tk.RIGHT)

history=tk.Listbox(selectmode=tk.EXTENDED, width=24)
scroll = tk.Scrollbar(command=history.yview)
history.config(yscrollcommand=scroll.set)

tk_root.mainloop()
