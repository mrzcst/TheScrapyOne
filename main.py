"""Main script"""
from app import App, StartDB

if __name__ == '__main__':
    StartDB()
    tso = App()
    tso.mainloop()

