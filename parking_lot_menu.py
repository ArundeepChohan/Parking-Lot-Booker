from tkinter import *
values=[]
class Menu():
    def __init__(self, root):
        self.root = root
        self.root.title("Parking Lot Edge Selector")
        self.root.geometry("600x600")
        self.edges = Entry(self.root) 
        self.edges.grid(row=0,column=0)
        self.button = Button(self.root, text="Press me", command=self.press)
        self.button.grid(row=1,column=0)
        self.textbox = list()
        self.size = 0
        self.values = []
        self.submitBoxes = list()
    def delete_rows(self):
        for i in reversed(range(self.size*2)):
           self.textbox[i].grid_remove()
        for j in reversed(range(len(self.submitBoxes))):
            self.submitBoxes[j].grid_remove()

    def submit(self):
        print('Submitted')
        global values
        self.values=[x.get() for x in self.textbox]
        values = self.values
    def get_values(self):
        print('Return list')
        return self.values

    """   This should limit the number of boxes to self.edges """
    def press(self):
        print('Pressed')
        self.delete_rows()
        self.textbox = list()
        self.submitBoxes = list()
        self.size = int(self.edges.get())
        self.values=[]
        for i in range(self.size):
            for j in range(2):
                self.values.append(StringVar(None))
                col0 = Entry(self.root,textvariable=self.values[-1]) 
                col0.insert(END, '0')
                self.textbox.append(col0)
                self.textbox[-1].grid(row=i+2,column=j)

        self.submitBoxes.append(Button(self.root, text="Submit values", command=self.submit))
        self.submitBoxes[-1].grid(row=(i+1*2)+3,column=0)

def main():
    root = Tk()
    app = Menu(root)
    root.mainloop()

if __name__ == '__main__':
    main()