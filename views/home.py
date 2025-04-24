import streamlit as st
from datetime import datetime
import io
import zipfile
from general_functions import report_period
from morning_api import (make_expense_pdf, make_income_pdf, make_non_docs_expense_dict,
                         check_number_of_expenses, check_number_of_expenses)


def make_zip_from_pdf(pdf_buffer, pdf_name):
    """ This function makes zip for download """
    pdf_bytes = pdf_buffer.getvalue()

    # Create a ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{pdf_name}.pdf", pdf_bytes)

    # Move to beginning so Streamlit reads it correctly
    zip_buffer.seek(0)

    return zip_buffer



def download_zip(buffer, zip_name):
    """ This function makes streamlit download button """
    st.download_button(
        label=f"📄 Download {zip_name} zip",
        data=buffer,
        file_name=f"{zip_name}.zip",
        mime="application/zip"
    )


def reported_expenses(date: str = None):
    no_bills, lacking_bills = check_number_of_expenses(date)
    st.write('No bills at all', no_bills)
    st.write('Not the expected amount of bills', lacking_bills)


@st.fragment
def income_data(date: str = None):
    """ This function creates the download button for income file """
    income_buffer = make_income_pdf(date)
    zip_buffer = make_zip_from_pdf(income_buffer, 'income')
    download_zip(zip_buffer, 'income')


@st.fragment
def expense_data(date: str = None):
    """ This function creates the download button for expense pdf """
    expense_buffer = make_expense_pdf(date)
    zip_buffer = make_zip_from_pdf(expense_buffer, 'income')
    download_zip(zip_buffer, 'expense')


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
