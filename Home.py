import streamlit as st
# from streamlit_extras.stoggle import stoggle
from streamlit_extras.switch_page_button import switch_page

st.session_state['prev_nutri'] = False

st.set_page_config(
    page_title="Home.py",
    #page_icon="👋",
)

st.write("# Welcome to NutriAI Planner! 🥗🤖")

st.markdown(" Making Meal Planning Easy and Personal ")

st.markdown(
    """
    NutriAI Planner is here to change the way nutritionists and their clients work together towards healthier eating 
    habits. With the help of smart technology, we make meal planning simpler, faster, and tailored just for you.

    Nutritionists : Say goodbye to the old ways of planning. Our system uses information about your clients' health, what 
    they like to eat, and their goals to automatically create meal plans they'll love. This means you get to focus more 
    on helping your clients succeed, with less time spent on the details.
    
    Clients : Your food preferences and health goals are unique to you. That's why you get meal plans made just for you, 
    helping you stay on track and reach your health goals faster. Plus, you can easily share how you're doing and what 
    you think of your meals, making sure your plan always fits your needs.
    
    How It Works: NutriAI Planner brings nutritionists and clients closer. Our system understands what clients need and 
    like, thanks to smart tech that learns and adjusts. It's all about making meal plans that fit perfectly, with fewer 
    changes needed over time.""")


st.markdown(f"**Currently, the system only support three goal types of the client: loss,"
            f"maintain or gain weight. (based on the client's current weight and goal weight)**")


st.markdown(f"**This system is designed to tailor meal plans according to individual client information, "
            f"incorporating the daily caloric requirements necessary to achieve specific health goals, whether it "
            f"is to lose, maintain, or gain weight. This calculation employs the Mifflin-St Jeor equation, adjusted "
            f"by a multiplier reflective of the client's activity level, which takes into account both their health "
            f"condition and physical activity. Additionally, the system integrates an analysis of blood tests and "
            f"incorporates ongoing feedback from a nutritionist to ensure the meal plans are optimized for the "
            f"client's nutritional needs and health objectives.**")

st.write()

st.markdown(
    """
Join NutriAI Planner and discover a new way to think about meal planning. Your journey to better eating starts here.
"""
)

col1, col2 = st.columns([3, 6])
with col1:
    if st.button("I'm a Nutritionist"):
        switch_page("nutri")
with col2:
    if st.button("I'm a Client"):
        switch_page("client_info")