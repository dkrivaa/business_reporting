import requests
from dotenv import load_dotenv
import os
import json
from io import BytesIO
from collections import defaultdict
import pymupdf

from general_functions import report_period


def get_token() -> str:
    """ Getting a JWT token from Morning """
    load_dotenv()
    token_url = os.getenv('TOKEN_URL')
    morning_api_key = os.getenv('MORNING_API_KEY')
    morning_secret = os.getenv('MORNING_SECRET')

    data = {
        "id": morning_api_key,
        "secret": morning_secret
    }
    values = json.dumps(data, indent=4)  # Pretty-print JSON
    headers = {
          'Content-Type': 'application/json'
        }
    response = requests.post(url=token_url, data=values, headers=headers)

    return response.json()['token']


def get_incomes(date: str = None, all_records: bool = False):
    """ This function gets all the incomes for the upcoming / present reporting period """
    load_dotenv()
    income_url = os.getenv('INCOME_URL')
    # Getting the JWT token
    token = get_token()
    # Getting upcoming / present reporting period
    fromDate, toDate = report_period(date)
    dates = {
        'fromDate': fromDate,
        'toDate': toDate,
    }
    # make json string
    values = json.dumps(dates)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    if all_records:
        response = requests.post(url=income_url, headers=headers)
        return response.json()
    else:
        response = requests.post(url=income_url, data=values, headers=headers)
        return response.json()


def get_income_doc(doc_number: str):
    """ This function gets a specific income doc according to the doc number """
    load_dotenv()
    income_url = os.getenv('INCOME_URL')
    # Getting the JWT token
    token = get_token()
    numbers = {
        'number': doc_number,
    }
    # make json string
    values = json.dumps(numbers)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.post(url=income_url, data=values, headers=headers)
    return response.json()


def get_expenses(date: str = None):
    """ This function gets all the expenses for the upcoming / present reporting period """
    load_dotenv()
    expense_url = os.getenv('EXPENSE_URL')
    # Getting the JWT token
    token = get_token()
    # Getting upcoming / present reporting period
    fromDate, toDate = report_period(date)
    dates = {
        'fromDate': fromDate,
        'toDate': toDate,
    }
    # make json string
    values = json.dumps(dates)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.post(url=expense_url, data=values, headers=headers)

    return response.json()


def expense_dict():
    """
    Function that returns a dict with companies and expected number of bills for each
    reporting period
    """
    return {
        'פלאפון תקשורת בע"מ': 2,
        'תאומי אורלי': 2,
        'פז חברת נפט בע"מ': 0,
        'אלקטרה פאוור סופרגז בע"מ': 1,
        'מי  מודיעין בע"מ': 1,
        'סלופארק טכנולוגיות': 2,
        'בזק החברה הישראלית לתקשורת בע"מ': 2,
        'דרך ארץ הייווייז (1997) בע"מ': 2,
        'חברת החשמל לישראל בעמ': 1,
        'ביטוח לאומי': 2,
        'רשות המיסים - מס הכנסה': 1,
        'רשות המיסים - מע"מ': 1,
        'ביטוח ישיר': 2,
    }


def check_number_of_expenses(date=None):
    """
    This function checks the number of bills for companies in expense_dict
    and if expected companies have bills
    """
    data = get_expenses(date)

    def count_func(company):
        return sum(1 for d in data['items'] if d.get("supplier", {}).get("name") == company)

    no_bills = []
    lacking_bills = []

    if data:
        # Checking if number of bills is as expected
        for exp in data['items']:
            company = exp['supplier']['name']
            count = count_func(company)
            expected = 0
            if company in list(expense_dict().keys()):
                expected = expense_dict()[company]

            if count < expected:
                no_bills.append(f'{company}')

        # Checking if all expected companies have bills
        expected_companies = list(expense_dict().keys())
        actual_companies = list({d.get("supplier", {}).get("name") for d in data['items']
                                 if "supplier" in d})

        for company in expected_companies:
            if company not in actual_companies:
                lacking_bills.append(f'{company}')

    return lacking_bills, no_bills


def make_expense_pdf(date=None):
    """ This function gets all expense docs from morning and merge them into one pdf buffer """
    data = get_expenses(date)['items']
    # Return pdf buffer from expense data
    return make_pdf_buffer(data)


def make_non_docs_expense_dict(date: str = None) -> dict[str, int]:
    """
    This function gets all expense without docs from morning and sums them by name and
    returns a dict - {name: sum}
    """
    data = get_expenses(date)
    # Keep all expenses without doc
    non_download_urls = [d for d in data['items'] if 'url' not in d]

    def sum_by_key(data, group_keys, sum_key):
        grouped_sum = defaultdict(int)

        for item in data:
            # Navigate through nested keys
            group_value = item
            for key in group_keys:
                group_value = group_value.get(key)

            # Sum the target value
            grouped_sum[group_value] += item[sum_key]

        return dict(grouped_sum)

    return sum_by_key(non_download_urls, ['supplier', 'name'], 'amount')


def make_income_pdf(date: str = None):
    """ This function gets all income docs from morning and merge them into one pdf buffer """
    data = get_incomes(date)['items']

    # Make list of document numbers for invoices of type 305
    all_invoice_only_numbers = [d['number'] for d in data if d['type'] == 305]
    # Initialize empty list to hold invoices from previous report periods if receipt in the reporting period
    invoices = []
    # Dealing with receipts
    for doc in data:
        if doc['type'] == 400:  # receipt
            # Getting corresponding invoice number
            invoice_number = doc['remarks'].split(' ')[4]
            # If relevant invoice in same reporting period
            if invoice_number in all_invoice_only_numbers:
                all_invoice_only_numbers.remove(invoice_number)
            # If relevant invoice not in current reporting period (getting the specific invoice from Morning)
            else:
                invoice = get_income_doc(invoice_number)['items']
                invoices.append(invoice[0])

    # Removing invoices that do not correspond with receipt in current reporting period
    data = [d for d in data if d['number'] not in all_invoice_only_numbers]
    # Adding invoices from previous reporting periods to data
    for invoice in invoices:
        data.append(invoice)

    def organize(data):
        """ This function organizes the docs list so that חשבונית comes right after קבלה """
        # Separate dictionaries with type 400 and 305
        type_400 = [d for d in data if d['type'] == 400]
        type_305 = [d for d in data if d['type'] == 305]
        others = [d for d in data if d['type'] not in (400, 305)]

        # Map type 305 by their amount for quick lookup
        type_305_map = {d['amount']: d for d in type_305}

        # Organize the result
        result = []
        for d in type_400:
            result.append(d)  # Add type 400
            if d['amount'] in type_305_map:
                result.append(type_305_map.pop(d['amount']))  # Add matching type 305

        # Add remaining type 305 and other items
        result.extend(type_305_map.values())
        result.extend(others)

        return result

    # Organize the list of docs
    data = organize(data)

    # Return pdf buffer from income data
    return make_pdf_buffer(data)


def make_pdf_buffer(data):
    """ This function returns a pdf buffer from list of dicts of Morning docs """
    try:
        # Income
        download_urls = [d['url']['he'] for d in data if 'url' in d]
    except TypeError:
        # Expenses
        download_urls = [d['url'] for d in data if 'url' in d]

    # Create an empty PDF
    data_pdf = pymupdf.open()

    # Download and merge PDFs
    for url in download_urls:
        response = requests.get(url)

        # Ensure successful download
        if response.status_code == 200:
            # Load PDF from memory
            pdf = pymupdf.open("pdf", response.content)

            # Append pages to merged PDF
            data_pdf.insert_pdf(pdf)

    # Save combined PDF to memory (BytesIO)
    pdf_buffer = BytesIO()
    data_pdf.save(pdf_buffer)
    pdf_buffer.seek(0)

    return pdf_buffer




