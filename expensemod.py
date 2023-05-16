import streamlit as st
from firebase_admin import firestore
import firebase_admin
from firebase_admin import credentials, auth
import pandas as pd
from streamlit_option_menu import option_menu
from datetime import datetime, time, timedelta, date
import numpy as np
from google.api_core import datetime_helpers
import io
from collections import defaultdict




cred = credentials.Certificate("exensefinal.json")
#firebase_admin.initialize_app(cred)
db = firestore.client()






########3 Expense Report functions#########


def show_approved_expenses():
    approved_expenses = db.collection("approved_expense").stream()
    st.subheader("Approved Expenses")

    for expense in approved_expenses:
        data = expense.to_dict()
        expense_id = expense.id

        st.markdown(f"### Expense submitted by {data['username']} for {data['expenditure_name']} at {datetime.strptime(data['submission_time'], '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M:%S')}")

        table_data = {
            "Expense ID": [expense_id],
            "Username": [data["username"]],
            "Expenditure Name": [data["expenditure_name"]],
            "Expense Date": [datetime.strptime(data["expense_date"], '%Y-%m-%d').strftime("%Y-%m-%d")],
            "Total Bill": [data["total_bill"]],
            "Bill Paid": [data["bill_paid"]],
            "Payment Method": [data["payment_method"]],
            "Cash From": [data["cash_from"]] if data["payment_method"] == "Cash" else None,
            "Bank Account": [data["bank_account"]] if data["payment_method"] == "Bank Account" else None,
            "Payment Due Date": [datetime.strptime(data["payment_due_date"], '%Y-%m-%d').strftime("%Y-%m-%d")],
            "Remarks":data["remarks"],
        }

        df = pd.DataFrame(table_data)
        st.table(df.T)

        st.success(f"Expense {expense_id} was approved.")
        st.write("---")


def show_sent_back_expenses():
    sent_back_expenses = db.collection("sent_back").stream()
    st.subheader("Sent Back Expenses")

    for expense in sent_back_expenses:
        data = expense.to_dict()
        expense_id = expense.id

        st.markdown(f"### Expense submitted by {data['username']} for {data['expenditure_name']} at {datetime.strptime(data['submission_time'], '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M:%S')}")

        table_data = {
            "Expense ID": [expense_id],
            "Username": [data["username"]],
            "Expenditure Name": [data["expenditure_name"]],
            "Expense Date": [datetime.strptime(data["expense_date"], '%Y-%m-%d').strftime("%Y-%m-%d")],
            "Total Bill": [data["total_bill"]],
            "Bill Paid": [data["bill_paid"]],
            "Payment Method": [data["payment_method"]],
            "Cash From": [data["cash_from"]] if data["payment_method"] == "Cash" else None,
            "Bank Account": [data["bank_account"]] if data["payment_method"] == "Bank Account" else None,
            "Payment Due Date": [datetime.strptime(data["payment_due_date"], '%Y-%m-%d').strftime("%Y-%m-%d")],
            "Remarks":data["remarks"],
        }

        df = pd.DataFrame(table_data)
        st.table(df.T)

        st.error(f"Expense {expense_id} was sent back.")
        st.write("---")



##############3 ends here############
def bank_account_details_form():
    with st.expander("Add New Bank Account", expanded=False):
        st.subheader("Please enter your bank account details")

        bank_name = st.text_input("Bank Name")
        branch_name = st.text_input("Branch Name")
        account_name = st.text_input("Account Name")
        account_number = st.text_input("Account Number")
        account_type_options = ["CD", "SB", "SND", "CC(H)", "Fixed Deposit", "Sanchaypatra"]
        account_type = st.selectbox("Account Type", options=account_type_options)
        available_balance = st.number_input("Available Balance", value=0.0, format='%f')

        if st.button("Save"):
            save_bank_account_details(bank_name, branch_name, account_name, account_number, account_type, available_balance)


def save_bank_account_details(bank_name, branch_name, account_name, account_number, account_type, available_balance):
    bank_details_ref = db.collection("bank_details")

    bank_details_ref.add({
        "bank_name": bank_name,
        "branch_name": branch_name,
        "account_name": account_name,
        "account_number": account_number,
        "account_type": account_type,
        "available_balance": available_balance,
    })

    st.success("Bank account details saved successfully.")


def bank_account_details_dashboard():
    with st.expander("Bank Account Details", expanded=False):
        st.subheader("Bank Account Details")

        bank_account_details = get_bank_account_details()
        display_bank_account_table(bank_account_details)


def get_bank_account_details():
    bank_details_ref = db.collection("bank_details").stream()

    bank_account_details = []
    for bank_detail in bank_details_ref:
        bank_data = bank_detail.to_dict()
        bank_data["id"] = bank_detail.id
        bank_account_details.append(bank_data)

    return bank_account_details


def display_bank_account_table(bank_account_details):
    table_data = {
        "Bank Name": [],
        "Branch Name": [],
        "Account Name": [],
        "Account Number": [],
        "Account Type": [],
        "Available Balance": []
    }

    for bank_data in bank_account_details:
        table_data["Bank Name"].append(bank_data['bank_name'])
        table_data["Branch Name"].append(bank_data['branch_name'])
        table_data["Account Name"].append(bank_data['account_name'])
        table_data["Account Number"].append(bank_data['account_number'])
        table_data["Account Type"].append(bank_data['account_type'])
        table_data["Available Balance"].append(bank_data['available_balance'])

    df = pd.DataFrame(table_data)
    st.table(df)


def delete_bank_account_form():
    with st.form("Delete Bank Account"):
        st.header("Delete a Bank Account")
        
        bank_account_details = get_bank_account_details()

        # Create a list of bank names for the selectbox
        bank_names = [bank_detail["bank_name"] for bank_detail in bank_account_details]

        # Create a list of branch names for the selectbox
        branch_names = [bank_detail["branch_name"] for bank_detail in bank_account_details]

        # Show a selectbox with the bank names
        selected_bank = st.selectbox("Select a Bank", bank_names)

        # Show a selectbox with the branch names
        selected_branch = st.selectbox("Select a Branch", branch_names)

        # If the user clicks the "Delete Account" button, delete the selected account
        if st.form_submit_button("Delete Account"):
            delete_bank_account(selected_bank, selected_branch)
            st.success(f"Bank account at '{selected_bank}' in branch '{selected_branch}' deleted.")
            

def delete_bank_account(bank_name, branch_name):
    bank_details_ref = db.collection("bank_details")

    # Fetch the documents for the selected bank and branch
    selected_bank_docs = bank_details_ref.where("bank_name", "==", bank_name).where("branch_name", "==", branch_name).stream()

    # Delete all documents for the selected bank and branch
    for doc in selected_bank_docs:
        bank_details_ref.document(doc.id).delete()


#####2######### pending task in admin panel

def pending_notification():
    pending_expenses = db.collection("pending_approval").stream()
    usernames = []
    for expense in pending_expenses:
        data = expense.to_dict()
        usernames.append(data["username"])
    num_pending_expenses = len(usernames)
    if num_pending_expenses > 0:
        st.warning(f"You have {num_pending_expenses} pending expenses from users: {', '.join(usernames)}")

def show_pending_expenses():
    pending_expenses = db.collection("pending_approval").stream()
    st.subheader("Pending Expenses for Approval")

    for expense in pending_expenses:
        data = expense.to_dict()
        expense_id = expense.id
        st.markdown(f"### Expense submitted by {data['username']} for {data['expenditure_name']} on {datetime.strptime(data['submission_time'], '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M')}")

        table_data = {
            "Expense ID": [expense_id],
            "Username": [data["username"]],
            "Expenditure Name": [data["expenditure_name"]],
            "Expense Date": [datetime.strptime(data["expense_date"], '%Y-%m-%d').strftime("%Y-%m-%d")],
            "Total Bill": [data["total_bill"]],
            "Bill Paid": [data["bill_paid"]],
            "Payment Method": [data["payment_method"]],
            "Cash From": [data["cash_from"]] if data["payment_method"] == "Cash" else None,
            "Bank Account": [data["bank_account"]] if data["payment_method"] == "Bank Account" else None,
            "Payment Due Date": [datetime.strptime(data["payment_due_date"], '%Y-%m-%d').strftime("%Y-%m-%d")],
            "Remarks":data["remarks"],
        }

        df = pd.DataFrame(table_data)
        st.table(df.T)

        with st.container():
            col1, col2 = st.columns(2)
            if col1.button("Approve", key=f"approve_{expense_id}"):
                data["status"] = "approved"
                db.collection("approved_expense").add(data)
                db.collection("pending_approval").document(expense_id).delete()
                st.success(f"Expense {expense_id} approved.")
            if col2.button("Reject", key=f"reject_{expense_id}"):
                data["status"] = "rejected"
                db.collection("sent_back").add(data)
                db.collection("pending_approval").document(expense_id).delete()
                st.error(f"Expense {expense_id} rejected.")

        st.write("---")


########end of 2######
####1.

def subtotal_row(index):
    cols = st.columns(3)
    item_name = cols[0].text_input("Item Name", key=f"item_name_{index}")
    quantity = cols[1].number_input("Quantity", min_value=0, step=1, key=f"quantity_{index}")
    unit_price = cols[2].number_input("Unit Price", min_value=0.0, step=0.01, key=f"unit_price_{index}")
    total_amount = quantity * unit_price
    return item_name, quantity, unit_price, total_amount


def generate_remarks(bill_type, item_data):
    if bill_type == "Subtotal Bill" and item_data:
        remarks = "Subtotal Billing Details:\n"
        for idx, item in enumerate(item_data):
            remarks += f"  {idx + 1}. Item Name: {item[0]}, Quantity: {item[1]}, Unit Price: {item[2]}, Total Amount: {item[3]}\n"
    else:
        remarks = ""
    return remarks



def submit_expense(username, expense=None):
    st.subheader("Update Expense" if expense else "Submit New Expense")
    bank_accounts = [doc.to_dict() for doc in db.collection("bank_details").stream()]
    petty_cash_users = [doc.to_dict() for doc in db.collection("petty_cash").stream()]

    mill_name = st.selectbox("Mill Name", ["Sirajgonj Mill", "Demra Mill"], index=0 if not expense else ["Sirajgonj Mill", "Demra Mill"].index(expense["mill_name"]))

    expenditure_name = st.selectbox("Expenditure Name", ["Expenditure Name", "Category"], index=0 if not expense else ["Expenditure Name", "Category"].index(expense["expenditure_name"]))
    if expenditure_name == "Expenditure Name":
        expenditure_name = st.text_input("Title of the Expense", value="" if not expense else expense["expenditure_name"])
    else:
        categories = ["Category 1", "Category 2", "Category 3"]
        expenditure_name = st.selectbox("Select Category", categories, index=0 if not expense else categories.index(expense["expenditure_name"]))

    expense_date = st.date_input("Expense Date", value=datetime.today() if not expense else expense["expense_date"])

    bill_type = st.selectbox("Bill Type", ["Total Bill", "Subtotal Bill"], index=0 if not expense else ["Total Bill", "Subtotal Bill"].index(expense["bill_type"]))

    if bill_type == "Subtotal Bill":
        num_rows = st.session_state.get("num_rows", 1)
        total_bill = 0.0
        item_data = []
        for idx in range(num_rows):
            item_name, quantity, unit_price, total_amount = subtotal_row(idx)
            item_data.append((item_name, quantity, unit_price, total_amount))
            total_bill += total_amount

        if st.button("Add another item"):
            num_rows += 1
            st.session_state.num_rows = num_rows

        remarks = generate_remarks(bill_type, item_data)
    else:
        total_bill = st.number_input("Total Bill Amount", min_value=0.0, step=0.01, value=0.0 if not expense else expense["total_bill"])
        remarks = ""

    bill_paid = st.number_input("Bill Paid", min_value=0.0, step=0.01, value=0.0 if not expense else expense["bill_paid"])
    payment_method = st.selectbox("Payment Method", ["Cash", "Bank Account"], index=0 if not expense else ["Cash", "Bank Account"].index(expense["payment_method"]))

    if payment_method == "Cash":
        # Show the list of users from petty_cash data
        cash_from = st.selectbox(
            "From whom the cash was paid",
            [user["username"] for user in petty_cash_users],
            index=0 if not expense else [user["username"] for user in petty_cash_users].index(expense["cash_from"])
        )
    else:
        # Show the list of available bank accounts
        bank_account = st.selectbox(
            "Bank Account",
            [f"{acc['bank_name']}-{acc['branch_name']}" for acc in bank_accounts],
            index=0 if not expense else [f"{acc['bank_name']}-{acc['branch_name']}" for acc in bank_accounts].index(expense["bank_account"])
        )
    payment_due_date = st.date_input("Payment Due Date", value=datetime.today() + timedelta(days=1) if not expense else expense["payment_due_date"])

    if st.button("Update" if expense else "Submit"):
        # Set submission time with hours and minutes
        submission_time = datetime.now().strftime('%Y-%m-%d %H:%M')

        expense_data = {
            "username": username,
            "mill_name": mill_name,
            "expenditure_name": expenditure_name,
            "expense_date": expense_date.strftime('%Y-%m-%d'),
            "bill_type": bill_type,
            "total_bill": total_bill,
            "bill_paid": bill_paid,
            "payment_method": payment_method,
            "cash_from": cash_from if payment_method == "Cash" else None,
            "bank_account": bank_account if payment_method == "Bank Account" else None,
            "payment_due_date": payment_due_date.strftime('%Y-%m-%d'),
            "submission_time": submission_time,
            "remarks": remarks if bill_type == "Subtotal Bill" else None,
        }

        if total_bill <= 5000:
            expense_data["status"] = "approved"
            if expense:  # if we are updating an existing expense
                db.collection("approved_expense").document(expense['id']).set(expense_data)
                st.success("Expense updated and approved.")
            else:  # if we are creating a new expense
                db.collection("approved_expense").add(expense_data)
                st.success("Expense submitted and approved.")
        else:
            expense_data["status"] = "pending"
            if expense:  # if we are updating an existing expense
                db.collection("pending_approval").document(expense['id']).set(expense_data)
                st.success("Expense updated for approval.")
            else:  # if we are creating a new expense
                db.collection("pending_approval").add(expense_data)
                st.success("Expense submitted for approval.")
        


def display_pending_expenses(username):
    st.subheader("Pending Expenses")

    # Query the Firestore collection for pending expenses for this user
    docs = db.collection('pending_approval').where('username', '==', username).stream()

    # Parse the returned documents into a list of dictionaries
    pending_expenses = [doc.to_dict() for doc in docs]

    # If there are any pending expenses, display them in a table
    if pending_expenses:
        for i, expense in enumerate(pending_expenses, 1):
            st.subheader(f"Pending Expense #{i}")
            df = pd.DataFrame(expense, index=[0])
            st.table(df.transpose())

            # Add buttons for updating and deleting the expense
            update_button = st.button(f"Update Expense #{i}")
            delete_button = st.button(f"Delete Expense #{i}")

            # If the delete button is clicked, delete the expense from the Firestore
            if delete_button:
                db.collection('pending_approval').document(expense['id']).delete()
                st.success(f"Deleted Expense #{i}")

            # If the update button is clicked, display a form for updating the expense
            if update_button:
                st.subheader(f"Update Expense #{i}")
                # Here, you call the submit_expense function with the current expense data
                submit_expense(username, expense)
    else:
        st.write("You have no pending expenses.")


###############





def login():
    with st.expander("Login", expanded=True):
        st.subheader("Please enter your credentials")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if verify_credentials(username, password):
                st.success(f"Logged in as {username}")
                st.session_state.logged_in = True
                st.session_state.username = username
            else:
                st.error("Invalid credentials")


def verify_credentials(username, password):
    users_ref = db.collection("users").stream()
    
    for user in users_ref:
        user_data = user.to_dict()
        if user_data["username"] == username and user_data["password"] == password:
            return True
            
    return False


def create_user_form():
    with st.expander("Create User"):
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        full_name = st.text_input("Full Name")
        phone_number = st.text_input("Phone Number")
        emergency_contact = st.text_input("Emergency Contact")
        address = st.text_area("Address")
        reference = st.text_input("Reference")
        job_desk_task = st.selectbox("Job Desk & Task", ["Finance", "Sales", "Operations", "Distribution House"])
        start_date = st.date_input("Start Date")  # collect joining date
        present_salary = st.number_input("Present Salary")

        if st.button("Create User"):
            create_user(new_username, new_password, full_name, phone_number, emergency_contact, address, reference, job_desk_task, start_date, present_salary)

def create_user(username, password, full_name, phone_number, emergency_contact, address, reference, job_desk_task, start_date, present_salary):
    users_ref = db.collection("users")
    users_ref.add({
        "username": username,
        "password": password,
        "full_name": full_name,
        "phone_number": phone_number,
        "emergency_contact": emergency_contact,
        "address": address,
        "reference": reference,
        "job_desk_task": job_desk_task,
        "Start Date": start_date.strftime("%Y-%m-%d"),  # store the date as string
        "Present Salary": present_salary,
    })
    st.success(f"User {username} created.")

def delete_user_form():
    with st.expander("Delete User"):
        username_to_delete = st.selectbox(
            "Select User to Delete",
            options=get_all_usernames(),
            index=0
        )
        
        if st.button("Delete User"):
            delete_user(username_to_delete)

def delete_user(username):
    users_ref = db.collection("users")
    user_docs = users_ref.where('username', '==', username).stream()
    
    for doc in user_docs:
        users_ref.document(doc.id).delete()

    st.success(f"User {username} deleted.")

def get_all_usernames():
    users_ref = db.collection("users").stream()
    usernames = [doc.to_dict()["username"] for doc in users_ref]
    usernames.remove('Admin')  # Removing 'admin' from the list
    return usernames

def user_detail_view():
    with st.expander("View User Details"):
        # Get the list of usernames from the database
        users_ref = db.collection("users").stream()
        # Exclude "admin" from the list
        usernames = [user.to_dict()["username"] for user in users_ref if user.to_dict()["username"].lower() != "admin"]

        # Create a selectbox for the user to select the username
        selected_user = st.selectbox("Select User", usernames)

        # Retrieve and display the selected user's details
        user_details = get_user_details(selected_user)
        display_user_details(user_details)


def get_user_details(username):
    docs = db.collection('users').where('username', '==', username).stream()
    docs = list(docs)  # convert to list to check its length

    if len(docs) == 0:
        st.error("No user data found.")
        return None

    # If we have documents, we continue with the first one
    doc = docs[0]
    user_data = doc.to_dict()

    return user_data


def display_user_details(user_data):
    if user_data is None:
        return

    # Create a dataframe for display
    df = pd.DataFrame(user_data, index=[0])

    # Reorder the columns
    df = df[["username", "password", "full_name", "job_desk_task", "phone_number", "address", "emergency_contact", "reference", "Start Date", "Present Salary"]]

    # Transpose the dataframe
    df_transposed = df.T

    # Display the transposed dataframe
    st.table(df_transposed)


def petty_home():
    with st.expander("Distribute Petty Cash", expanded=False):
        st.subheader("Distribute Petty Cash to User")
        usernames = get_all_usernames()
        selected_user = st.selectbox("Select User", usernames)
        amount = st.number_input("Enter Amount", min_value=0.0, step=0.01)
        if st.button("Distribute"):
            distribute_petty_cash(selected_user, amount)


def distribute_petty_cash(username, amount):
    distribution_date = datetime.now().strftime("%Y-%m-%d")
    db.collection("petty_cash").add({
        "username": username,
        "amount": amount,
        "distribution_date": distribution_date,
    })
    st.success(f"Distributed {amount} to {username} on {distribution_date}")


def petty_available_home():
    # Add existing code for Distribute Petty Cash expander
    with st.expander("Available Petty Cash", expanded=False):
        st.subheader("User-wise Petty Cash Available")
        petty_cash_data = get_petty_cash_data()
        display_petty_cash_table(petty_cash_data)


def get_petty_cash_data():
    petty_cash_ref = db.collection("petty_cash").stream()

    user_petty_cash = defaultdict(lambda: {'amount': 0})
    for entry in petty_cash_ref:
        data = entry.to_dict()
        username = data["username"]
        amount = data["amount"]
        #date = data.get("distribution_date", "Not Available")
        user_petty_cash[username]['amount'] += amount
        #user_petty_cash[username]['date'] = date

    return user_petty_cash


def display_petty_cash_table(petty_cash_data):
    table_data = {
        "Username": [],
        "Petty Cash Available": [],
    }

    for username, data in petty_cash_data.items():
        if username != "Admin":
            table_data["Username"].append(username)
            table_data["Petty Cash Available"].append(round(data['amount'], 2))  # rounded to 2 decimal places

    df = pd.DataFrame(table_data)
    st.table(df)

def user_petty_cash_summary():
    users_ref = db.collection("users").stream()
    petty_cash_ref = db.collection("petty_cash").stream()

    # Retrieve user data
    user_data = []
    for user in users_ref:
        data = user.to_dict()
        data["id"] = user.id
        user_data.append(data)
    df_users = pd.DataFrame(user_data)

    # Exclude 'password' and 'id' columns
    df_users = df_users.drop(columns=['password', 'id'])

    # Retrieve petty cash data
    user_petty_cash = defaultdict(lambda: {'amount': 0})
    for entry in petty_cash_ref:
        data = entry.to_dict()
        username = data["username"]
        amount = data["amount"]
        user_petty_cash[username]['amount'] += amount
    df_petty_cash = pd.DataFrame(user_petty_cash).T.reset_index().rename(columns={'index': 'username', 'amount': 'petty_cash_available'})

    # Merge the dataframes
    df = df_users.merge(df_petty_cash, on='username', how='left')

    # Replace NaN values with 0
    df['petty_cash_available'] = df['petty_cash_available'].fillna(0)

    # Reorder the columns
    df = df[["username", "full_name", "job_desk_task", "phone_number", "address", "emergency_contact", "reference", "Start Date", "Present Salary", "petty_cash_available"]]

    # Transpose the dataframe
    df_transposed = df.T

    # Display the transposed dataframe
    st.table(df_transposed)




def verify_credentials(username, password):
    users_ref = db.collection("users").stream()
    
    for user in users_ref:
        user_data = user.to_dict()
        if user_data["username"] == username and user_data["password"] == password:
            return True
            
    return False

def user_profile(username):
    docs = db.collection('users').where('username', '==', username).stream()
    docs = list(docs)  # convert to list to check its length
    
    if len(docs) == 0:
        st.error("No user data found.")
        return
    
    # If we have documents, we continue with the first one
    doc = docs[0]
    user_data = doc.to_dict()

    profile_data = {
        "Username": [user_data["username"]],
        "Full Name": [user_data["full_name"]],
        "Phone Number": [user_data["phone_number"]],
        "Emergency Contact": [user_data["emergency_contact"]],
        "Address": [user_data["address"]],
        "Reference": [user_data["reference"]],
        "Job Desk & Task": [user_data["job_desk_task"]],
        #"Start Date": [user_data["start_date"]],
        #"Present Salary":[user_data["present_salary"]],
    }

    df = pd.DataFrame(profile_data)
    st.table(df.T)




def admin_dashboard():
    st.subheader("Admin Dashboard")
    pending_notification()
    dash= option_menu(
            options=['Home', 'Order Management', 'Expense Management', 'Product Management', 'Customer Management', 'Distribution House management'],
            menu_title=None,
            menu_icon='cast',
            orientation='horizontal')
#Home Button Functions#######
    if dash=="Home":
        home_option=option_menu(
            options=['User Management', 'Bank Account Management', 'Petty Cash Management'],
            menu_title=None,
            menu_icon='cast',
            orientation='horizontal')
        if home_option=='User Management':
            with st.expander("Details of all user", expanded=False):
                user_petty_cash_summary()
            user_detail_view()
            create_user_form()
            delete_user_form()
            
          
        elif home_option=="Bank Account Management":
            bank_account_details_form()
            bank_account_details_dashboard()
            with st.expander("Delete Bank Account", expanded=False):
                delete_bank_account_form()
        elif home_option=="Petty Cash Management":
            petty_home()
            petty_available_home()
        
#########Expense Management Functions############        
        
        

    elif dash=="Expense Management":
        choice = option_menu(
            options=['Pending Expenses for Approval', 'Due Dates', 'Expense Report'],
            menu_title=None,
            menu_icon='cast',
            orientation='horizontal')

        if choice == "Pending Expenses for Approval":
            show_pending_expenses()
            
        elif choice=="Due Dates":
            st.write('Upcoming Due dates in chronological order')
            
        elif choice=="Expense Report":
            st.write("Expense Reports from all users")

    elif dash=="Order Management":
        st.subheader("orders will be managed with brief summary")      
        
    elif dash=="Product Management":
        st.subheader("Product will be managed with brief summary")
    elif dash=="Customer Management":
        st.subheader("list of customers with their dues and past histories will be available here")

    elif dash=="Distribution House management":
        st.write("Detailed Management of Distribution House")
     
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        login()
    
    

def user_dashboard(username):
    if username == 'Admin':
        st.title(f"Welcome, {username}!")
        admin_dashboard()
    else:
        st.title(f"Welcome, {username}! Greetings!")
        choices = option_menu(
            options=['Profile', 'Expense Module', 'Order Management','Product Management'],
            menu_title=None,
            menu_icon='cast',
            orientation='horizontal')

        if choices=="Profile":
            st.subheader("Will be the Details of the User, their past, RM details, in hand petty cash, contact details")
            user_profile(username)

        elif choices=="Expense Module":
            
            choice = option_menu(
            options=['Submit New Expense', 'Pending Expenses', 'Sent Back Expenses','Expense Report'],
            menu_title=None,
            menu_icon='cast',
            orientation='horizontal')

            if choice == "Submit New Expense":
                submit_expense(username)
                
            elif choice == "Pending Expenses":
                display_pending_expenses(username)
            elif choice == "Sent Back Expenses":
                st.write("will show all the tables with status 'sent back' with two option - Delete or resubmit")
                show_sent_back_expenses()
                
            elif choice == "Expense Report":
                st.write("all the expenses having approved status in a  big table sorted by respective user")
                with st.expander("Show Approved Expense Details individually"):
                    show_approved_expenses()
        elif choices=="Order Management":
            st.title("Here, order will be managed")
        elif choices=="Product Management":
            st.title("Products and stocks will be maintained from here")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        login()
    

if __name__ == "__main__":
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        if st.session_state.username == "Admin":
            admin_dashboard()
        else:
            user_dashboard(st.session_state.username)
    else:
        login()
