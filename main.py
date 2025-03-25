import streamlit as st

# App pages
login_page = st.Page(
    title='Login',
    page='views/login.py',
    default=True
)

home_page = st.Page(
    title='Home',
    page='views/home.py'
)

pages = [login_page, home_page]

# Run the App
pg = st.navigation(pages=pages, position='hidden')
pg.run()




