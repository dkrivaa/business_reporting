import os
from dotenv import load_dotenv
import streamlit as st


def main():
    """ This function is for simple login """
    load_dotenv()
    # Login
    code = st.text_input('Enter code', type='password', value=None)
    if code is not None:
        if code == os.getenv('CODE'):
            st.switch_page('views/home.py')
        else:
            st.write('Incorrect Code')


if __name__ == '__main__':
    main()