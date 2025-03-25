import streamlit as st
from datetime import datetime
from general_functions import report_period
from morning_api import (make_expense_pdf, make_income_pdf, make_non_docs_expense_dict,
                         check_number_of_expenses, check_number_of_expenses)


def download_pdf(buffer, pdf_name):
    """ This function makes streamlit download button """
    st.download_button(
        label=f"📄 Download {pdf_name} PDF",
        data=buffer,
        file_name=f"{pdf_name}.pdf",
        mime="application/pdf"
    )


def reported_expenses(date: str = None):
    no_bills, lacking_bills = check_number_of_expenses(date)
    st.write('No bills at all', no_bills)
    st.write('Not the expected amount of bills', lacking_bills)


@st.fragment
def income_data(date: str = None):
    """ This function creates the download button for income pdf """
    income_buffer = make_income_pdf(date)
    download_pdf(income_buffer, 'income')


@st.fragment
def expense_data(date: str = None):
    """ This function creates the download button for expense pdf """
    expense_buffer = make_expense_pdf(date)
    download_pdf(expense_buffer, 'expense')


@st.fragment
def non_doc_expenses(date: str = None):
    """ This function creates the dataframe for expenses without docs """
    st.dataframe(make_non_docs_expense_dict(date))


def main():
    """ This function runs the app """
    my_date = st.date_input('Enter Date', value=datetime.today(), max_value=datetime.today(),
                            format='DD/MM/YYYY')

    date_string = my_date.strftime('%Y-%m-%d')
    if st.button('Continue'):
        st.divider()
        start, end = report_period(date_string)
        st.write(f'Report for period {start} - {end}')
        reported_expenses(date_string)
        st.divider()
        income_data(date_string)
        expense_data(date_string)
        non_doc_expenses(date_string)


main()
