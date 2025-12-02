import tkinter as tk
from tkinter import ttk
from datetime import datetime
import json

total_label = None  



TRANSACTIONS_FILE = "transactions.json"
PRODUCTS_FILE = "products.json"


def load_transactions():
    try:
        with open(TRANSACTIONS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_transactions(transactions):
    with open(TRANSACTIONS_FILE, "w") as file:
        json.dump(transactions, file, indent=2)


def load_products():
    try:
        with open(PRODUCTS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_products(products):
    with open(PRODUCTS_FILE, "w") as file:
        json.dump(products, file, indent=2)


def add_product(product_name, price):
    if product_name and price:
        product_name = product_name.strip()
        price = float(price)
        if product_name not in products:
            product_id = len(products) + 1  
            products[product_name] = {"id": product_id, "price": price}
            save_products(products)
            show_manage_products_page()
            update_dropdown_teller()





temp_transactions = []
permanent_transactions = load_transactions()
tran_id_counter = max([transaction['tran_id'] for transaction in permanent_transactions], default=0) + 1


products = load_products()


item_dropdown = None

def scan_and_add(barcode):
    # Fetch product details from the database using the barcode (replace this with your own logic)
    product_id = barcode
    no_of_items = 1
    amount = products.get(product_id, {'price': 0})['price']  # Use product price as amount

    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if the product is already in temp_transactions, update the quantity if so
    for transaction in temp_transactions:
        if transaction['product_id'] == product_id:
            transaction['no_of_items'] += no_of_items
            transaction['amount'] += amount
            break
    else:
        # If the product is not in temp_transactions, insert a new entry
        temp_transactions.append({
            'tran_id': None,  # Assign None for now, will be updated during takeout
            'date_time': date_time,
            'product_id': product_id,
            'no_of_items': no_of_items,
            'amount': amount
        })

    update_display()
    # Update the dropdown in the Teller Page
    update_dropdown_teller()

def update_dropdown_teller():
    global item_dropdown, selected_product_teller  # Declare both variables as global
    items = list(products.keys())
    item_dropdown['values'] = items
    selected_product_teller.set(item_dropdown.get())  # Set the selected value in the variable


def remove_item(index):
    if index < len(temp_transactions):
        # Decrement the quantity by 1, remove the item if the quantity becomes 0
        if temp_transactions[index]['no_of_items'] > 1:
            temp_transactions[index]['no_of_items'] -= 1
            temp_transactions[index]['amount'] -= temp_transactions[index]['amount'] / (temp_transactions[index]['no_of_items'] + 1)
        else:
            total_items = temp_transactions[index]['no_of_items']
            total_amount = temp_transactions[index]['amount']
            del temp_transactions[index]

            # Update total items and total amount
            total_items -= 1
            total_amount -= total_amount / (total_items + 1)

        update_display()

def add_product_from_dropdown():
    selected_product = selected_product_teller.get()
    if selected_product:
        scan_and_add(selected_product)

        # Create or update the total label
        update_total_label()


def update_total_label():
    global total_label
    total_transaction_amount = sum(transaction['amount'] for transaction in temp_transactions)

    # Update the text of total_label if it already exists
    if total_label:
        total_label.config(text=f"Total: R{total_transaction_amount:.2f}")
    else:
        # Create a Label widget for the total and place it to the right of the page
        total_label = tk.Label(teller_frame, text=f"Total: R{total_transaction_amount:.2f}", font=('Helvetica', 16), bd=10, relief="groove")
        total_label.grid(row=0, column=2, rowspan=6, padx=10, pady=10, sticky="nsew")


def cancel_session():
    global total_label
    temp_transactions.clear()
    update_display()
    update_total_label()


def takeout_items():
    global tran_id_counter, total_label

    for transaction in temp_transactions:
        transaction['tran_id'] = tran_id_counter

    permanent_transactions.extend(temp_transactions)
    temp_transactions.clear()
    tran_id_counter += 1  # Increment the transaction ID counter
    update_display()
    save_transactions(permanent_transactions)  # Save permanent transactions
    update_total_label()

def update_display():
    global total_label
    # Declare total_length as a local variable within the function
    total_length = 60  

    # Clear items_text before updating
    items_text.delete(1.0, tk.END)

    # Display items with a remove button in the Teller Page
    item_counts = {}  # Dictionary to store the count of each selected item
    for i, transaction in enumerate(temp_transactions):
        item_id = transaction['product_id']
        count = transaction['no_of_items']
        amount = transaction['amount']
        item_text = f'{item_id} - {count} items   R{amount:.2f}\n'

        if item_id not in item_counts:
            item_counts[item_id] = i  # Use the index of the first occurrence of the item
            items_text.insert(tk.END, item_text)

            # Create a remove button
            remove_button = tk.Button(teller_frame, text='✖', command=lambda i=i: remove_item(i))
            items_text.window_create(tk.END, window=remove_button)
            items_text.insert(tk.END, '\n')

    # Display the total amount for items in temp_transactions (outside the loop)
    total_temp_amount = sum(transaction['amount'] for transaction in temp_transactions)
    total_text_temp = f"Total (Temporary): R{total_temp_amount:.2f}\n\n"
    items_text.insert(tk.END, total_text_temp)

    # Display transactions in the View Transactions Page
    transactions_text.delete(1.0, tk.END)
    current_tran_id = None
    total_transaction_amount = 0

    for i, transaction in enumerate(temp_transactions + permanent_transactions):
        if current_tran_id is not None and transaction['tran_id'] != current_tran_id:
            # Calculate the number of dashes needed on each side of "Total" to center it
            total_length = 60  # Total length of the line
            total_text = f"Total: R{total_transaction_amount:.2f}"
            dashes_needed = (total_length - len(total_text)) // 2

            # Draw a line with "Total" centered
            transactions_text.insert(tk.END, '-'*dashes_needed + total_text + '-'*dashes_needed + '\n\n')
            total_transaction_amount = 0  # Reset total amount for the next transaction

        transactions_text.insert(tk.END, "{} - {} - {} - {} items   R{:.2f}\n".format(
            transaction['tran_id'],
            transaction['date_time'],
            transaction['product_id'],
            transaction['no_of_items'],
            transaction['amount']
        ))

        # Update total amount for the current transaction
        total_transaction_amount += transaction['amount']

        # Update current transaction ID
        current_tran_id = transaction['tran_id']

    # Draw a line after the last transaction
    total_text = f"Total: R{total_transaction_amount:.2f}"
    dashes_needed = (total_length - len(total_text)) // 2
    transactions_text.insert(tk.END, '-'*dashes_needed + total_text + '-'*dashes_needed + '\n')

    # Update the text of total_label if it already exists
    if total_label:
        total_label.config(text=f"Total: R{total_transaction_amount:.2f}")
    else:
        # Create a Label widget for the total and place it to the right of the page
        total_label = tk.Label(teller_frame, text=f"Total: R{total_transaction_amount:.2f}", font=('Helvetica', 16), bd=10, relief="groove")
        total_label.grid(row=0, column=2, rowspan=6, padx=10, pady=10, sticky="nsew")

# Function to switch to a specific notebook page
def show_page(page_index):
    notebook.select(page_index)
    if page_index == 0:  # If switching to Teller Page, update the display and initialize the variable
        update_display()
        update_dropdown_teller()
        update_total_label()
# Function to show the Manage Products Page
def show_manage_products_page():
    products_listbox.delete(0, tk.END)
    for product_name, product_details in products.items():
        products_listbox.insert(tk.END, f"{product_name} - {product_details['id']} - R{product_details['price']:.2f}")
    show_page(2)

# Function to show the Add Product Page
def show_add_product_page():
    add_product_window = tk.Toplevel(root)
    add_product_window.title("Add Product")

    # GUI elements for adding a product (you can customize this based on your needs)
    product_name_label = tk.Label(add_product_window, text="Product Name:")
    product_name_label.pack()

    product_name_entry = tk.Entry(add_product_window)
    product_name_entry.pack()

    price_label = tk.Label(add_product_window, text="Price:")
    price_label.pack()

    price_entry = tk.Entry(add_product_window)
    price_entry.pack()

    add_button = ttk.Button(add_product_window, text="Add", command=lambda: add_product(product_name_entry.get(), price_entry.get()))
    add_button.pack()


# Function to update a product
def update_product(old_product_name, new_product_name, price, modify_product_window):
    products[new_product_name] = {"id": products[old_product_name]["id"], "price": float(price)}
    if old_product_name != new_product_name:
        del products[old_product_name]  # Remove the old product entry if the name is changed
    save_products(products)
    modify_product_window.destroy()
    show_manage_products_page()
    update_dropdown_teller()

# Function to remove a product
def remove_product():
    selected_product = products_listbox.get(tk.ACTIVE).split(" - ")[0]
    if selected_product in products:
        del products[selected_product]
        save_products(products)
        update_display()
        show_manage_products_page()
        update_dropdown_teller()

# Function to show the Modify Product Page
def show_modify_product_page():
    selected_product = products_listbox.get(tk.ACTIVE).split(" - ")[0]
    if selected_product in products:
        product = products[selected_product]

        modify_product_window = tk.Toplevel(root)
        modify_product_window.title(f"Modify Product - {selected_product}")

        # GUI elements for modifying a product (you can customize this based on your needs)
        product_name_label = tk.Label(modify_product_window, text="Product Name:")
        product_name_label.pack()

        product_name_entry = tk.Entry(modify_product_window)
        product_name_entry.insert(tk.END, selected_product)
        product_name_entry.pack()

        price_label = tk.Label(modify_product_window, text="Price:")
        price_label.pack()

        price_entry = tk.Entry(modify_product_window)
        price_entry.insert(tk.END, product["price"])
        price_entry.pack()

        update_button = ttk.Button(modify_product_window, text="Update", command=lambda: update_product(selected_product, product_name_entry.get(), price_entry.get(), modify_product_window))
        update_button.pack()

# Main GUI setup function
def setup_gui():
    global root, notebook, teller_frame, items_text, transactions_text, products_listbox, selected_product_teller
    
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.title('Point of Sale System')
    
    # Style configuration
    style = ttk.Style()
    style.configure('TButton', padding=10, font=('Helvetica', 12))

    notebook = ttk.Notebook(root)

    teller_frame = tk.Frame(notebook)
    notebook.add(teller_frame, text='Teller')

    entry_label = tk.Label(teller_frame, text='Scan Barcode or Select Product:')
    entry_label.grid(row=0, column=0, padx=10, pady=10)

    entry = tk.Entry(teller_frame)
    entry.grid(row=0, column=1, padx=10, pady=10)

    items = list(products.keys())
    global item_dropdown  
    selected_product_teller = tk.StringVar()
    item_dropdown = ttk.Combobox(teller_frame, textvariable=selected_product_teller, values=items)
    item_dropdown.set('Select Product')
    item_dropdown.grid(row=1, column=0, padx=10, pady=10)

    add_from_dropdown_button = ttk.Button(teller_frame, text='Add Selected Product', command=add_product_from_dropdown)
    add_from_dropdown_button.grid(row=1, column=1, padx=10, pady=10)

    scan_button = ttk.Button(teller_frame, text='Scan and Add', command=lambda: scan_and_add(entry.get()))
    scan_button.grid(row=2, column=0, padx=10, pady=10)

    cancel_button = ttk.Button(teller_frame, text='Cancel Session', command=cancel_session)
    cancel_button.grid(row=2, column=1, padx=10, pady=10)

    takeout_button = ttk.Button(teller_frame, text='Takeout Items', command=takeout_items)
    takeout_button.grid(row=3, column=0, columnspan=2, pady=10)

    items_text = tk.Text(teller_frame, height=10, width=50)
    items_text.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    display_label = tk.Label(teller_frame, text='')
    display_label.grid(row=5, column=0, columnspan=2, pady=10)


    view_transactions_frame = tk.Frame(notebook)
    notebook.add(view_transactions_frame, text='View Transactions')

   
    transactions_text = tk.Text(view_transactions_frame, height=20, width=80, wrap=tk.NONE)
    transactions_text.pack()

   
    manage_products_frame = tk.Frame(notebook)
    notebook.add(manage_products_frame, text='Manage Products')

   
    products_listbox = tk.Listbox(manage_products_frame)
    products_listbox.pack()

    add_product_button = ttk.Button(manage_products_frame, text='Add Product', command=show_add_product_page)
    add_product_button.pack()

    remove_product_button = ttk.Button(manage_products_frame, text='Remove Product', command=lambda: remove_product())
    remove_product_button.pack()

    modify_product_button = ttk.Button(manage_products_frame, text='Modify Product', command=show_modify_product_page)
    modify_product_button.pack()

    
    for product_name, product_details in products.items():
        products_listbox.insert(tk.END, f"{product_name} - {product_details['id']} - R{product_details['price']:.2f}")

    notebook.pack(expand=1, fill="both")

    
    show_page(0)
    

    root.mainloop()
    
  
# Call the setup_gui function to run the GUI
setup_gui()
