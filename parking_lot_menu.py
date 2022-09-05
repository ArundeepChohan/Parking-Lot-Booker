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

    def delete_rows(self):
        for i in range(self.size):
           self.textbox[i].grid_remove()

    """   This should limit the number of boxes to self.edges """
    def press(self):
        print('Pressed')
        self.delete_rows()
        self.textbox = list()
        size = self.edges.get()
        self.size = int(size)
        print(int(size))
        for i in range(int(size)):
            self.textbox.append(Text(self.root, height = 1, width = 57, wrap = None ))
            self.textbox[i].grid(row=1+i+1,column=0)
        
        global values
        values=[x.get(1.0, END) for x in self.textbox]

def main():
    root = Tk()
    app = Menu(root)
    root.mainloop()
    print(values)

if __name__ == '__main__':
    main()