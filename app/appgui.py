import customtkinter as ctk
import CTkMessagebox as mBox
import threading
import webbrowser
from tkinter import ttk
from PIL import Image
import app.dbManager as db
from app.dataScraper import create_item_struct as dataScraper
from app.dataScraper import get_current_price as checkNow

ctk.set_default_color_theme("dark-blue")
ctk.set_appearance_mode("dark")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("The Scrapy One")
        self.geometry("1024x640")
        self.iconbitmap("assets/icon.ico")
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        
        self.grid_rowconfigure((1), weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.scrape_frame = ScrapeFrame(self)
        self.scrape_frame.grid(row=0, column=0,  padx=10, pady=(10, 0), sticky="new", columnspan=2)

        self.button_frame = ButtonFrame(self)
        self.button_frame.grid(row=1, column=0, padx=(10, 0), pady=10, sticky="nsw")   

        style = ttk.Style()
        style.theme_use('alt')
        style.configure(
            "Treeview", 
            background="#292828",
            foreground="#D6D6D6",
            fieldbackground="#292828",
            rowheight=20
        )
        self.bind("<Control-F>", lambda event: search_item(self))
        self.bind("<Control-f>", lambda event: search_item(self))
        self.bind("<Control-G>", lambda event: filter_profit(self))
        self.bind("<Control-g>", lambda event: filter_profit(self))
        self.bind("<Control-H>", lambda event: filter_price(self))
        self.bind("<Control-h>", lambda event: filter_price(self))

class ButtonFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_rowconfigure((6, 7), weight=1)

        self.bufftoskinpBtn = ctk.CTkButton(self, text="Buff >> Skinport", command=lambda: self.show_frame(master, B2SFrame, self.bufftoskinpBtn))
        self.bufftoskinpBtn.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.skinptobuffBtn = ctk.CTkButton(self, text="Skinport >> Buff", command=lambda: self.show_frame(master, S2BFrame, self.skinptobuffBtn))
        self.skinptobuffBtn.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.boughtBtn = ctk.CTkButton(self, text="Bought History", command=lambda: self.show_frame(master, BoughtFrame, self.boughtBtn))
        self.boughtBtn.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.soldBtn = ctk.CTkButton(self, text="Sold History", command=lambda: self.show_frame(master, SoldFrame, self.soldBtn))
        self.soldBtn.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.investmentsBtn = ctk.CTkButton(self, text="Investments", command=lambda: self.show_frame(master, InvestFrame, self.investmentsBtn))
        self.investmentsBtn.grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.descBtn = ctk.CTkButton(self, text="Description", command=lambda: self.show_frame(master, DescFrame, self.descBtn))
        self.descBtn.grid(row=5, column=0, padx=10, pady=10, sticky="w")
        self.exitBtn = ctk.CTkButton(self, text="Exit", command=master.destroy)
        self.exitBtn.grid(row=8, column=0, padx=10, pady=10, sticky="w")

        self.active_btn = None
        self.show_frame(master, DescFrame, self.descBtn)

    # Displays selected Frame 
    def show_frame(self, cont, frame_name:object, btn:ctk): 
        if hasattr(self, "active_frame"):
            self.active_frame.grid_forget()
            self.active_frame.destroy()

        if self.active_btn is not None:
            self.active_btn.configure(state="normal")

        self.active_btn = btn
        btn.configure(state="disabled")

        self.active_frame = frame_name(cont)
        self.active_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

class ScrapeFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master) 
        self.grid_columnconfigure((0,1), weight=1)

        self.start_btn = ctk.CTkButton(self, text="Start Scraping", command=self.start_scrape)
        self.start_btn.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.textSwitch = ctk.CTkLabel(self, text="Scraping OFF", text_color="red", font=("Arial", 15, "bold"))
        self.textSwitch.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        self.textInfo = ctk.CTkLabel(self, text="")
        self.textInfo.grid(row=0, column=2, padx=10, pady=10, sticky="w")

        self.scraping = False

    # Start the scraping process(Btn)
    def start_scrape(self):
        self.scrape_thread = threading.Thread(target=self.get_data, daemon=True)
        if self.scraping:
            mBox.CTkMessagebox(title="Info", message="Already Scraping, please wait!", justify="center")
        else:
            self.scraping = True
            self.textSwitch.configure(text="Scraping ON:", text_color="green")
            self.start_btn.configure(state='disabled')
            self.scrape_thread.start()

    def get_data(self):
        try:
            self.textInfo.configure(text="Scraping data...")
            scraped_data = dataScraper()
            self.textInfo.configure(text="Saving items...")
            db.insert_data(scraped_data)
            self.scraping = False
            self.textInfo.configure(text="Finished with success")
            self.start_btn.configure(state='normal')
            self.textSwitch.configure(text="Scraping OFF: ", text_color="red")
        except Exception as e:
            self.scraping = False
            self.textSwitch.configure(text="Scraping OFF: ", text_color="red")
            self.textInfo.configure(text=f"Finished with error")
            self.start_btn.configure(state='normal')
            mBox.CTkMessagebox(title="Error", message=f"{e}", icon="cancel", justify="center")

class B2SFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master) 
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((1), weight=1)

        self.page_title = ctk.CTkLabel(self, text="Buff To Skinport Data", font=("Arial", 20, "bold"))
        self.page_title.grid(row=0, column=0, pady=10, sticky="n")

        self.scroll_frame = ctk.CTkFrame(self)
        self.scroll_frame.grid(row=1, column=0, padx=10, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        self.scroll_frame.grid_rowconfigure(0, weight=1)

        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=4, column=0, pady=10, sticky="s")
        self.start_btn = ctk.CTkButton(self.btn_frame, text="Open Links", command=self.open_links)
        self.start_btn.grid(row=0, column=0,padx=(0,10))
        self.cancel_btn = ctk.CTkButton(self.btn_frame, text="Add To Bought", command=self.item_bought) 
        self.cancel_btn.grid(row=0, column=1, padx=10)

        columns=("name", "buff_price", "skinp_price", "skinp_qnt", "b2s_profit")
        self.data_table = ttk.Treeview(self.scroll_frame, columns=columns, show='headings')
        self.data_table.grid(row=0, column=0, sticky="nsew")

        scrollBar = ctk.CTkScrollbar(self.scroll_frame, command=self.data_table.yview, button_color="#1e538c", hover=False)
        scrollBar.grid(row=0, column=1, sticky="ns")
        self.data_table.configure(yscrollcommand=scrollBar.set)

        self.data_table.heading('name', text='Item Name', command=lambda: self.sort_by_column(0))
        self.data_table.heading('buff_price', text='Buff Price', command=lambda: self.sort_by_column(1))
        self.data_table.heading('skinp_price', text='Skinport Price', command=lambda: self.sort_by_column(2))
        self.data_table.heading('skinp_qnt', text='Selling Quantity', command=lambda: self.sort_by_column(3))
        self.data_table.heading('b2s_profit', text='Profit (%))', command=lambda: self.sort_by_column(4))

        self.data_table.column('name', minwidth=350, stretch=True)
        self.data_table.column('buff_price', width=100, anchor="center", stretch=False)
        self.data_table.column('skinp_price', width=100, anchor="center", stretch=False)
        self.data_table.column('skinp_qnt', width=100, anchor="center", stretch=False)
        self.data_table.column('b2s_profit', width=100, anchor="center", stretch=False)

        self.item_data = db.get_b2s_data()
        B2SFrame.frame = self
        self.populate_table(self.item_data)

    def populate_table(self, data):
        for item in self.data_table.get_children():
            self.data_table.delete(item)

        for item in data:
            self.data_table.insert('', 'end', values=item)

    def sort_by_column(self, column):
        items = list(self.data_table.get_children(''))
        if column == 0:
            items.sort(key=lambda item: self.data_table.set(item, column))
        else:
            items.sort(key=lambda item: float(self.data_table.set(item, column)), reverse=True)

        for i, item in enumerate(items):
            self.data_table.move(item, '', i)

    def open_links(self):
        item = self.data_table.focus()
        if item == "":
            mBox.CTkMessagebox(title="Info", message="Please select an item!", justify="center")
            return
        else:
            buff_link = self.data_table.item(item)["values"][5]
            skinp_link = self.data_table.item(item)["values"][6]

        webbrowser.open(buff_link)
        webbrowser.open(skinp_link)
    
    def item_bought(self):
        item = self.data_table.focus()
        if item == "":
            mBox.CTkMessagebox(title="Info", message="Please select an item!", justify="center")
            return
        else:
            item_name = self.data_table.item(item)["values"][0]
            paid_price = ctk.CTkInputDialog(text=f"Price paid for [{item_name}] in CNY", title="Price Input")
            paid = paid_price.get_input()
            if paid is None:
                return
            try:
                paid = float(paid)
                minim_sell = round(((paid * 0.12) + paid), 2)
                item_data = [item_name, paid, 0, minim_sell]
                db.insert_bought_item(item_data)
            except ValueError:
                mBox.CTkMessagebox(title="Error", message="Price should be a float value! (use [.] for decimal separation)!", icon="cancel", justify="center")

class S2BFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master) 
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((1), weight=1)

        self.page_title = ctk.CTkLabel(self, text="Skinport To Buff Data", font=("Arial", 20, "bold"))
        self.page_title.grid(row=0, column=0, pady=10, sticky="n")

        self.scroll_frame = ctk.CTkFrame(self)
        self.scroll_frame.grid(row=1, column=0, padx=10, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        self.scroll_frame.grid_rowconfigure(0, weight=1)

        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=4, column=0, pady=10, sticky="s")
        self.start_btn = ctk.CTkButton(self.btn_frame, text="Open Links", command=self.open_links)
        self.start_btn.grid(row=0, column=0,padx=(0,10))
        self.cancel_btn = ctk.CTkButton(self.btn_frame, text="Add To Bought", command=self.item_bought) 
        self.cancel_btn.grid(row=0, column=1, padx=10)

        columns=("name", "skinp_price", "buff_price", "buff_qnt", "s2b_profit")
        self.data_table = ttk.Treeview(self.scroll_frame, columns=columns, show='headings')
        self.data_table.grid(row=0, column=0, sticky="nsew")
        
        scrollBar = ctk.CTkScrollbar(self.scroll_frame, command=self.data_table.yview, button_color="#1e538c", hover=False)
        scrollBar.grid(row=0, column=1, sticky="ns")
        self.data_table.configure(yscrollcommand=scrollBar.set)

        self.data_table.heading('name', text='Item Name', command=lambda: self.sort_by_column(0))
        self.data_table.heading('skinp_price', text='Skinport Price', command=lambda: self.sort_by_column(1))
        self.data_table.heading('buff_price', text='Buff Price', command=lambda: self.sort_by_column(2))
        self.data_table.heading('buff_qnt', text='Selling Quantity', command=lambda: self.sort_by_column(3))
        self.data_table.heading('s2b_profit', text='Profit (%)', command=lambda: self.sort_by_column(4))

        self.data_table.column('name', minwidth=350, stretch=True)
        self.data_table.column('skinp_price', width=100, anchor="center", stretch=False)
        self.data_table.column('buff_price', width=100, anchor="center", stretch=False)
        self.data_table.column('buff_qnt', width=100, anchor="center", stretch=False)
        self.data_table.column('s2b_profit', width=100, anchor="center", stretch=False)

        item_data = db.get_s2b_data()
        S2BFrame.frame = self
        self.populate_table(item_data)

    def populate_table(self, data):
        for item in self.data_table.get_children():
            self.data_table.delete(item)

        for item in data:
            self.data_table.insert('', 'end', values=item)
        
    def sort_by_column(self, column):
        items = list(self.data_table.get_children(''))
        if column == 0:
            items.sort(key=lambda item: self.data_table.set(item, column))
        else:
            items.sort(key=lambda item: float(self.data_table.set(item, column)), reverse=True)

        for i, item in enumerate(items):
            self.data_table.move(item, '', i)

    def open_links(self):
        item = self.data_table.focus()
        if item == "":
            mBox.CTkMessagebox(title="Info", message="Please select an item!", justify="center")
            return
        else:
            buff_link = self.data_table.item(item)["values"][5]
            skinp_link = self.data_table.item(item)["values"][6]

        webbrowser.open(skinp_link)
        webbrowser.open(buff_link)
    
    def item_bought(self):
        item = self.data_table.focus()
        if item == "":
            mBox.CTkMessagebox(title="Info", message="Please select an item!", justify="center")
            return
        else:
            item_name = self.data_table.item(item)["values"][0]
            paid_price = ctk.CTkInputDialog(text=f"Price paid for [{item_name}] in CNY", title="Price Input")
            paid = paid_price.get_input()
            if paid is None:
                return
            else:
                trade_ban = ctk.CTkInputDialog(text=f"Trade ban on Skinport: ", title="Trade Ban") 
                locked = trade_ban.get_input()
                if locked is None:
                    return  
            try:
                locked = int(locked)
                paid = float(paid)
                minim_sell = (paid * 0.025) + paid
                item_data = [item_name, paid, locked, round(minim_sell, 2)]
                db.insert_bought_item(item_data)
            except ValueError and TypeError:
                mBox.CTkMessagebox(title="Error", message="Price should be a float value and trade days an integer! (use [.] for decimal separation)!", icon="cancel", justify="center")

class BoughtFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master) 
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((1), weight=1)

        self.page_title = ctk.CTkLabel(self, text="Bought Items", font=("Arial", 20, "bold"))
        self.page_title.grid(row=0, column=0, pady=10, sticky="n")

        self.scroll_frame = ctk.CTkFrame(self)
        self.scroll_frame.grid(row=1, column=0, padx=10, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        self.scroll_frame.grid_rowconfigure(0, weight=1)

        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=4, column=0, pady=10, sticky="s")
        self.start_btn = ctk.CTkButton(self.btn_frame, text="Item Sold", command=self.item_sold)
        self.start_btn.grid(row=0, column=0,padx=(0,10))
        self.cancel_btn = ctk.CTkButton(self.btn_frame, text="Remove Item", command=self.remove_item) 
        self.cancel_btn.grid(row=0, column=1, padx=(10,0))

        columns=("name", "paid_price", "bought_date", "tradeble_on", "minim_sell")
        self.data_table = ttk.Treeview(self.scroll_frame, columns=columns, show='headings')
        self.data_table.grid(row=0, column=0, sticky="nsew")
        
        scrollBar = ctk.CTkScrollbar(self.scroll_frame, command=self.data_table.yview, button_color="#1e538c", hover=False)
        scrollBar.grid(row=0, column=1, sticky="ns")
        self.data_table.configure(yscrollcommand=scrollBar.set)

        self.data_table.heading('name', text='Item Name', command=lambda: self.sort_by_column(0))
        self.data_table.heading('paid_price', text='Paid Price', command=lambda: self.sort_by_column(1))
        self.data_table.heading('bought_date', text='Buy Date', command=lambda: self.sort_by_column(2))
        self.data_table.heading('tradeble_on', text='Tradeble On', command=lambda: self.sort_by_column(3))
        self.data_table.heading('minim_sell', text='Minim Sell', command=lambda: self.sort_by_column(4))

        self.data_table.column('name', minwidth=350, stretch=True)
        self.data_table.column('paid_price', width=100, anchor="center", stretch=False)
        self.data_table.column('bought_date', width=100, anchor="center", stretch=False)
        self.data_table.column('tradeble_on', width=100, anchor="center", stretch=False)
        self.data_table.column('minim_sell', width=100, anchor="center", stretch=False)

        item_data = db.get_bought_items()
        for item in item_data:
            self.data_table.insert('', 'end', values=item)

    def sort_by_column(self, column):
        items = list(self.data_table.get_children(''))
        if column == 0 or column == 2 or column == 3:
            items.sort(key=lambda item: self.data_table.set(item, column))
        else:
            items.sort(key=lambda item: float(self.data_table.set(item, column)), reverse=True)

        for i, item in enumerate(items):
            self.data_table.move(item, '', i)
    
    def remove_item(self):
        item = self.data_table.focus()
        if item == "":
            mBox.CTkMessagebox(title="Info", message="Please select an item!", justify="center")
            return
        else:
            item_id = self.data_table.item(item)["values"][5]
            self.data_table.delete(item)
            db.delete_bought_item(str(item_id))

    def item_sold(self):
        item = self.data_table.focus()
        if item == "":
            mBox.CTkMessagebox(title="Info", message="Please select an item!", justify="center")
            return
        else:
            item_name = self.data_table.item(item)["values"][0]
            sold_price = ctk.CTkInputDialog(text=f"How much did [{item_name}] sold for in CNY", title="Price Input")
            sold = sold_price.get_input()
            if sold is None:
                return
            else:
                traded_on = ctk.CTkInputDialog(text=f"Where did you sold the item(Skinport/Buff)", title="Sold On") 
                site = traded_on.get_input()
                if site is not None:
                    accepted_skinp_str = ['skinport', 'skinp', 'skin', 'skport', 'sknport']
                    accepted_buff_str = ['buff', 'buf']
                    site_str = str(site).lower()
                    if site_str in accepted_skinp_str:
                        site_str = "Skinport"
                        tax = 0.12
                    elif site_str in accepted_buff_str:
                        site_str = "Buff"
                        tax = 0.025
                    else:   
                        return
                else:
                    return 
            try:
                sold = float(sold)
                paid = float(self.data_table.item(item)["values"][1])
                profit = sold - paid - (sold * tax)
                item_data = [item_name, paid, sold, site_str, round(profit, 2)]
                db.insert_sold_item(item_data)
                self.remove_item()
            except ValueError and TypeError:
                mBox.CTkMessagebox(title="Error", message="Incorect values! [Price -> Float, Site ->(Skinport, Buff)] (use [.] for decimal separation)!", icon="cancel", justify="center")

class SoldFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master) 
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((1), weight=1)

        self.page_title = ctk.CTkLabel(self, text="Sold Items", font=("Arial", 20, "bold"))
        self.page_title.grid(row=0, column=0, pady=10, sticky="n")

        self.scroll_frame = ctk.CTkFrame(self)
        self.scroll_frame.grid(row=1, column=0, padx=10, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        self.scroll_frame.grid_rowconfigure(0, weight=1)

        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.stats_frame.grid_columnconfigure((0,1), weight=1)
        self.stats_frame.grid_rowconfigure((0,1,2), weight=1)

        data = db.get_extra_data()

        self.items_sold = ctk.CTkLabel(self.stats_frame, text=f"Items sold: {data['items_sold']}", font=("Arial", 15, "bold"))
        self.items_sold.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nw")
        self.items_sold_buff = ctk.CTkLabel(self.stats_frame, text=f"Items sold on Buff: {data['buff_sold']}", font=("Arial", 15, "bold"))
        self.items_sold_buff.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nw")
        self.items_sold_skinp = ctk.CTkLabel(self.stats_frame, text=f"Items sold on Skinport: {data['skinp_sold']}", font=("Arial", 15, "bold"))
        self.items_sold_skinp.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="nw")
        self.profit = ctk.CTkLabel(self.stats_frame, text=f"Profit (CNY): {data['profit']} ", font=("Arial", 15, "bold"))
        self.profit.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="nw")
        self.invested = ctk.CTkLabel(self.stats_frame, text=f"Invested (EUR): {data['investment']}", font=("Arial", 15, "bold"), text_color="gray")
        self.invested.grid(row=1, column=1, padx=10, pady=(10, 0), sticky="nw")

        columns=("name", "paid_price", "sold_price", "sold_site", "sold_date", "profit")
        self.data_table = ttk.Treeview(self.scroll_frame, columns=columns, show='headings')
        self.data_table.grid(row=0, column=0, sticky="nsew")
        
        scrollBar = ctk.CTkScrollbar(self.scroll_frame, command=self.data_table.yview, button_color="#1e538c", hover=False)
        scrollBar.grid(row=0, column=1, sticky="ns")
        self.data_table.configure(yscrollcommand=scrollBar.set)

        self.data_table.heading('name', text='Item Name', command=lambda: self.sort_by_column(0))
        self.data_table.heading('paid_price', text='Paid Price', command=lambda: self.sort_by_column(1))
        self.data_table.heading('sold_price', text='Sold Price', command=lambda: self.sort_by_column(2))
        self.data_table.heading('sold_site', text='Sold Site', command=lambda: self.sort_by_column(3))
        self.data_table.heading('sold_date', text='Sold Date', command=lambda: self.sort_by_column(4))
        self.data_table.heading('profit', text='Profit (CNY)', command=lambda: self.sort_by_column(5))

        self.data_table.column('name', minwidth=350, stretch=True)
        self.data_table.column('paid_price', width=90, anchor="center", stretch=False)
        self.data_table.column('sold_price', width=90, anchor="center", stretch=False)
        self.data_table.column('sold_site', width=90, anchor="center", stretch=False)
        self.data_table.column('sold_date', width=90, anchor="center", stretch=False)
        self.data_table.column('profit', width=90, anchor="center", stretch=False)

        item_data = db.get_sold_items()
        for item in item_data:
            self.data_table.insert('', 'end', values=item)

    def sort_by_column(self, column):
        items = list(self.data_table.get_children(''))
        if column == 0 or column == 3 or column == 4:
            items.sort(key=lambda item: self.data_table.set(item, column))
        else:
            items.sort(key=lambda item: float(self.data_table.set(item, column)), reverse=True)

        for i, item in enumerate(items):
            self.data_table.move(item, '', i)
    
class InvestFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master) 
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((1), weight=1)

        self.page_title = ctk.CTkLabel(self, text="Investments", font=("Arial", 20, "bold"))
        self.page_title.grid(row=0, column=0, pady=10, sticky="n")

        self.scroll_frame = ctk.CTkFrame(self)
        self.scroll_frame.grid(row=1, column=0, padx=10, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        self.scroll_frame.grid_rowconfigure(0, weight=1)

        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=4, column=0, pady=10, sticky="s")
        self.cancel_btn = ctk.CTkButton(self.btn_frame, text="Add Item", command=self.get_invest) 
        self.cancel_btn.grid(row=0, column=0, padx=(0,10))
        self.start_btn = ctk.CTkButton(self.btn_frame, text="Check Prices", command=self.refresh_price)
        self.start_btn.grid(row=0, column=1,)
        self.cancel_btn = ctk.CTkButton(self.btn_frame, text="Remove Item", command=self.remove_item) 
        self.cancel_btn.grid(row=0, column=2, padx=(10,0))

        columns=("name", "quantity", "added_date", "total_price", "price_per_item", "price_now", "profit")
        self.data_table = ttk.Treeview(self.scroll_frame, columns=columns, show='headings')
        self.data_table.grid(row=0, column=0, sticky="nsew")
        
        scrollBar = ctk.CTkScrollbar(self.scroll_frame, command=self.data_table.yview, button_color="#1e538c", hover=False)
        scrollBar.grid(row=0, column=1, sticky="ns")
        self.data_table.configure(yscrollcommand=scrollBar.set)

        self.data_table.heading('name', text='Item Name', command=lambda: self.sort_by_column(0))
        self.data_table.heading('quantity', text='Quantity', command=lambda: self.sort_by_column(1))
        self.data_table.heading('added_date', text='Date', command=lambda: self.sort_by_column(2))
        self.data_table.heading('total_price', text='Total Price', command=lambda: self.sort_by_column(3))
        self.data_table.heading('price_per_item', text='Price/Item', command=lambda: self.sort_by_column(4))
        self.data_table.heading('price_now', text='Price/Item Now', command=lambda: self.sort_by_column(5))
        self.data_table.heading('profit', text='Profit (CNY)', command=lambda: self.sort_by_column(6))

        self.data_table.column('name', minwidth=250, stretch=True)
        self.data_table.column('quantity', width=70, anchor="center", stretch=False)
        self.data_table.column('added_date', width=100, anchor="center", stretch=False)
        self.data_table.column('total_price', width=90, anchor="center", stretch=False)
        self.data_table.column('price_per_item', width=100, anchor="center", stretch=False)
        self.data_table.column('price_now', width=100, anchor="center", stretch=False)
        self.data_table.column('profit', width=90, anchor="center", stretch=False)

        item_data = db.get_investments()
        self.populate_table(item_data)

    def populate_table(self, data):
        for item in self.data_table.get_children():
            self.data_table.delete(item)

        for item in data:
            self.data_table.insert('', 'end', values=item)

    def get_invest(self):
        self.popup = ctk.CTkToplevel()
        self.popup.title("Add Investment")
        self.popup.geometry("300x150")
        self.popup.resizable(0, 0)
        self.popup.attributes('-topmost', 'true')

        self.popup.grid_rowconfigure((0), weight=1)
        self.popup.grid_columnconfigure((0, 1), weight=1)

        frame = ctk.CTkFrame(self.popup)
        frame.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="nsew", columnspan=2)
        frame.grid_columnconfigure((0, 1), weight=1)

        frame_title = ctk.CTkLabel(frame, text="Add item to Investments")
        frame_title.grid(row=0, column=0, columnspan=2)
        self.item_link = ctk.CTkEntry(frame, placeholder_text="Enter Buff link")
        self.item_link.grid(row=1, column=0, pady=5, padx=5, sticky="ew", columnspan=2)
        self.price_paid = ctk.CTkEntry(frame, placeholder_text="Price paid (Total)")
        self.price_paid.grid(row=2, column=0, pady=5, padx=5, sticky="ew")
        self.quantity = ctk.CTkEntry(frame, placeholder_text="Item Quantity")
        self.quantity.grid(row=2, column=1, pady=5, padx=5, sticky="ew")

        add_btn = ctk.CTkButton(self.popup, text="Add Item", command=self.add_item)
        add_btn.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        cancel_btn = ctk.CTkButton(self.popup, text="Cancel", command=self.popup.destroy) 
        cancel_btn.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.popup.mainloop()

    def add_item(self):
        try:
            link = str(self.item_link.get())
            paid = float(self.price_paid.get())
            qnt = int(self.quantity.get())
        except ValueError as ve:
            mBox.CTkMessagebox(title="Error", message=f"ValueError: {ve}! Retry", icon="cancel", justify="center")
        except TypeError as te:
            mBox.CTkMessagebox(title="Error", message=f"TypeError: {te}! Retry", icon="cancel", justify="center")

        item_id = link.split("/")[-1]

        try:
            current_data = checkNow(item_id)
        except Exception as e:
            mBox.CTkMessagebox(title="Error", message=f"Error: {e}!", icon="cancel", justify="center")
            
        paid_per_item = round((paid / qnt), 2)  
        on_sell = (current_data[1] * qnt) - paid
        profit = round(on_sell - (on_sell * 0.025), 2)

        item = [current_data[0], qnt, paid, paid_per_item, current_data[1], profit, item_id]
        db.insert_investment(item)
        self.popup.destroy()

        item_data = db.get_investments()
        self.populate_table(item_data)

    def refresh_price(self):
        item = self.data_table.focus()
        if item == "":
            mBox.CTkMessagebox(title="Info", message="Please select an item!", justify="center")
            return
        else:
            unique_id = self.data_table.item(item)["values"][8]
            paid = float(self.data_table.item(item)["values"][3])
            qnt = int(self.data_table.item(item)["values"][1])
            item_id = self.data_table.item(item)["values"][7]
            current_price = float(checkNow(str(item_id))[1]) 
            profit = (paid - (qnt*current_price)) - ((paid - (qnt*current_price))*0.025)
            updated_data = [current_price, round(profit, 2)]
            db.update_investment_price(unique_id, updated_data)

    def remove_item(self):
        item = self.data_table.focus()
        if item == "":
            mBox.CTkMessagebox(title="Info", message="Please select an item!", justify="center")
            return
        else:
            item_id = self.data_table.item(item)["values"][8]
            self.data_table.delete(item)
            db.delete_investment(str(item_id))

class DescFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master) 
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        photo = ctk.CTkImage(dark_image=Image.open("assets/logo.png"), size=(300, 150))

        logo = ctk.CTkLabel(self, image=photo, text="")
        logo.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        desc_text = ctk.CTkTextbox(self, font=("", 17), fg_color="transparent")
        desc_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        desc_text.tag_config("center", justify="center")
        desc_text.tag_config("left", justify="left")

        desc_text.insert("end", "\nThe Scrapy One is a small project that I started to make scraping and finding good\nitems to trade in CS-GO (CS2) easier and also to keep track of the progress. It still need a lot of work\nto make it good but for now is working and good enough for me to call it a 1.0.0 version.\n", "center")
        desc_text.insert("end", "\nScraping for items on Buff is not really time efficient as it requires at least a 5 sec\ncooldown for every page (if its is lower account will get banned, from my experience) and there\nis no other method to scrape without and account. So the total process will take around 30 minutes:(. ", "center")
        desc_text.insert("end", "\n\nNow here are some shortcuts as I wanted to keep the design clean:\n[CTRL + F] - To find an item in a table\n[CTRL + G] - To filter by profit\n[CTRL + H] - To filter by buy price", "center")
        desc_text.configure(state="disabled")

        copyr_text = ctk.CTkLabel(self, text="v1.0.0 | © 2023 Morozan Constantin. All rights reserved.", font=("Gill Sans", 11))
        copyr_text.grid(row=2, column=0, padx=10, pady=5)

def search_item(master):
    if master.winfo_children()[2].__class__ == B2SFrame:
        input = ctk.CTkInputDialog(text="Search for item in Buff To Skinport table: ", title="Search").get_input()

        if input is None or input == "":
            return
        
        output = db.search_items("b2s", input)
        B2SFrame.populate_table(B2SFrame.frame, data=output)

    elif master.winfo_children()[2].__class__ == S2BFrame:
        input = ctk.CTkInputDialog(text="Search for item in Skinport to Buff table: ", title="Search").get_input()

        if input is None or input == "":
            return
        
        output = db.search_items("s2b", input)
        S2BFrame.populate_table(S2BFrame.frame, data=output)

    else:
        return

def filter_profit(master):
    if master.winfo_children()[2].__class__ == B2SFrame:
        getIn = ctk.CTkInputDialog(text="Set profit range in CNY (MIN , MAX): ", title="Search").get_input()

        if getIn is None or getIn == "":
            return
        
        profit = getIn.replace(" ", "").split(",")
        try:
            profit_min, profit_max = int(profit[0]), int(profit[1])
        except ValueError:
            mBox.CTkMessagebox(title="Error", message="Invalid Value!", icon="cancel", justify="center")
            return
        
        output =  db.filter_by_profit("b2s", profit_min, profit_max)
        B2SFrame.populate_table(B2SFrame.frame, data=output)

    elif master.winfo_children()[2].__class__ == S2BFrame:
        getIn = ctk.CTkInputDialog(text="Set profit range in CNY (MIN , MAX): ", title="Search").get_input()

        if getIn is None or getIn == "":
            return
        
        profit = getIn.replace(" ", "").split(",")
        try:
            profit_min, profit_max = int(profit[0]), int(profit[1])
        except ValueError:
            mBox.CTkMessagebox(title="Error", message="Invalid Value!", icon="cancel", justify="center")
            return
        
        output = db.filter_by_profit("s2b", profit_min, profit_max)
        S2BFrame.populate_table(S2BFrame.frame, data=output)

    else:
        return

def filter_price(master):
    if master.winfo_children()[2].__class__ == B2SFrame:
        getIn = ctk.CTkInputDialog(text="Set buy price range in CNY (MIN , MAX): ", title="Search").get_input()
        
        if getIn is None or getIn == "":
            return
        
        profit = getIn.replace(" ", "").split(",")
        try:
            price_min, price_max = float(profit[0]), float(profit[1])
        except ValueError:
            mBox.CTkMessagebox(title="Error", message="Invalid Value!", icon="cancel", justify="center")
            return
        
        output =  db.filter_by_price("b2s", price_min, price_max)
        B2SFrame.populate_table(B2SFrame.frame, data=output)

    elif master.winfo_children()[2].__class__ == S2BFrame:
        getIn = ctk.CTkInputDialog(text="Set buy price range in CNY (MIN , MAX): ", title="Search").get_input()

        if getIn is None or getIn == "":
            return
        
        profit = getIn.replace(" ", "").split(",")
        try:
            price_min, price_max = float(profit[0]), float(profit[1])
        except ValueError:
            mBox.CTkMessagebox(title="Error", message="Invalid Value!", icon="cancel", justify="center")
            return
        
        output = db.filter_by_price("s2b", price_min, price_max)
        S2BFrame.populate_table(S2BFrame.frame, data=output)
        
    else:
        return
    