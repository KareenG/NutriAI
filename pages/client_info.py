import streamlit as st
from database_manager import fetch_client_details, fetch_all_client_bloodTest_as_dict,\
    get_meals_with_rates_for_client,\
    display_progress, get_feedback_score, check_id_exists, \
    get_encouragement_comment, add_feedback, update_rates_of_meal

from streamlit_extras.stoggle import stoggle

#vectorDB, dictV, similarity_matrix = clients_con2VectorDB()
client_id = 0
client_name = ""
client_data=[]
calorie_per_day = 0

if st.button('show form'):
    st.session_state[f"client_id_info"] = None
def run_client_more_info(client_id, client_name):
    col1_client_info, col2_client_info = st.columns([3, 2])
    with col1_client_info:
        st.write(f"**More information for {client_name} (ID: {client_id})**")
        client_data = fetch_client_details(client_id)
        st.write(f"**Age**: {client_data['age']} years old")
        st.write(f"**Gender**: {client_data['gender']}")
        st.write(f"**Health condition**: {client_data['health_condition']}")
        st.write(f"**Current weight**: {client_data['current_weight']} kg")
        st.write(f"**Height**: {client_data['height']} cm")
        st.write(f"**Goal weight**: {client_data['goal_weight']} kg")
        st.write(f"**Calories needed per day**: {client_data['calorie_per_day']} cal")
        st.write(f"**Active in sport**: {client_data['active_sport']} active")
        st.write(f"**Liked meals**: {client_data['liked_meals']} ")
        st.write(f"**Liked vegetables**: {client_data['liked_veg']} ")
        st.write(f"**Liked fruits**: {client_data['liked_fruits']} ")
        st.write(f"**Liked snacks**: {client_data['liked_snacks']} ")
        st.write(f"**Dislikes**: {client_data['dislikes']} ")


        blood_tests_list = []
        # show latest blood test results
        blood_tests_dict, blood_test_latest_date_dict = fetch_all_client_bloodTest_as_dict()
        if client_id in blood_test_latest_date_dict.keys():
            st.write(f"Result of blood tests as of date {blood_test_latest_date_dict[client_id]} :")
            if client_id in blood_tests_dict.keys():
                for key in blood_tests_dict[client_id].keys():
                    if key not in ['age', 'gender', 'health_condition']:
                        blood_tests_list.append(key)
                        st.write(f"{key} : {blood_tests_dict[client_id][key]}")


    with col2_client_info:
        # we will ask gemini to give as a number between 1-10 of client satisfaction based on his feedbacks.
        satisfaction_level, at_most_three_feedbacks = get_feedback_score(
            client_id)  # 7  # Example client satisfaction score
        if type(satisfaction_level) == float:
            display_progress(satisfaction_level)
            st.write(get_encouragement_comment(int(satisfaction_level)))

        else:
            st.write("You have not submit a feedback yet.")
            # st.markdown('<br><br>', unsafe_allow_html=True)
            st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)
            st.write(get_encouragement_comment(satisfaction_level))

        # Use HTML to add space; adjust height as needed
        st.markdown('<br><br>', unsafe_allow_html=True)

        # Create a form with a submit button
        with st.form(key='message_form', clear_on_submit=True):
            input_data = st.text_input("Send a message for the nutritionist:")
            submit_button = st.form_submit_button(label='Submit')

            if submit_button:
                # process_input(input_data)
                if input_data:
                    add_feedback(client_id, input_data)
                input_data = None

    return client_data['calorie_per_day'], blood_tests_list



if st.session_state.get(f"client_id_info", None) is None:
    with st.form("id_check_form", clear_on_submit=True):
        st.write("## Check if Client ID Exists")
        client_id_input = st.text_input("Enter Your ID Number:", "")
        submit_button = st.form_submit_button("Check ID")


        if submit_button and client_id_input:
            try:
                client_id_inserted = int(client_id_input)
                exists = check_id_exists(client_id_inserted)
                if exists:
                    client_id, client_name = exists
                    st.session_state[f"client_id_info"] = client_id
                    st.session_state[f"client_name_info"] = client_name
                    st.session_state.active_day = None
                    st.success("Client ID exists and information displayed.")
                else:
                    st.error("Client ID does not exist.")
            except ValueError:
                st.error("Please enter a valid integer ID.")



if st.session_state.get(f"client_id_info", None) is not None:
    client_id = st.session_state[f"client_id_info"]
    client_name = st.session_state[f"client_name_info"]
    calorie_per_day, blood_tests_list = run_client_more_info(client_id, client_name)



def render_frame(day, already_exists_approved_meal, already_exists_approved_meal_explanations, id_meal):
    # Creating 5 blocks, each with 3 columns for text, button, and image
    meal_types = ['Breakfast', 'Mid-Morning Snack', 'Lunch', 'Afternoon Snack', 'Dinner']
    meal_cal = calorie_per_day/10
    cal_per_meal_type = [meal_cal*2, meal_cal*1.5, meal_cal*2.5, meal_cal, meal_cal*3]

    if already_exists_approved_meal:

        st.write(f"Meal Plan for Day {day} - Approximately {calorie_per_day} calories")

        for block in range(0, 5):
            col1, col2 = st.columns((30, 16))

            # Column 1: Text generated by another function
            with col1:
                #st.markdown(f"**{meal_types[block]} - Approximately {int(cal_per_meal_type[block])} calories**")
                st.write(already_exists_approved_meal[block])
                stoggle('Click here for more', already_exists_approved_meal_explanations[block],)
                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)
            # Column 2: Button
            with col2:
                if st.button("💬", key=f"rate_{day}_{block}"):
                    # Use session state to track that the edit button has been clicked for this block
                    st.session_state[f"rate_clicked_{day}_{block}"] = True
                if st.session_state.get(f"rate_clicked_{day}_{block}", False):
                    input_key = f"rate_input_{day}_{block}"
                    submit_key = f"rate_submit_{day}_{block}"

                    # Define the satisfaction options
                    satisfaction_options = [
                        "Highly Satisfied",
                        "Satisfied",
                        "Moderately Satisfied",
                        "Barely Satisfied",
                        "Not Satisfied"
                    ]

                    # Create the radio button
                    satisfaction_level = st.radio(f"How satisfied are you with this {meal_types[block]} meal?", satisfaction_options, key=f"radio_{day}_{block}")

                    # Submit button
                    if st.button("Submit", key=submit_key):#if st.button('Submit'):
                        # add rate
                        update_rates_of_meal(id_meal, block, satisfaction_level)
                        del st.session_state[f"rate_clicked_{day}_{block}"]


    else:
        st.header(f"The nutritionist has not yet approved a meal plan for you for day {day}")


if client_id:
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown(f"""
    **Notes**:

    * Clicking on specific day button will be presented the last meal plan approved by the nutritionist of this day.

    * By clicking on the 💬 buttons, please rate your meals based on your satisfaction to enhance meal plan suggestions 
    tailored to your preferences 
    and satisfaction.
    """)
    st.markdown('<br>', unsafe_allow_html=True)

    # Initialize session state
    if 'active_day' not in st.session_state:
        st.session_state.active_day = None

    # Main layout columns for days buttons and frame content
    button_col, _, frame_col= st.columns([1, 0.1, 7])

    # Render days buttons
    with button_col:
        st.write("## Days")  # Header for the button column
        for day in range(1, 8):
            if st.button(f"Day {day}", key=f"day_{day}"):
                st.session_state.active_day = day


    # Render the frame based on the selected day
    with frame_col:
        if st.session_state.active_day is not None:
            meal_types = ['Breakfast', 'Mid-Morning Snack', 'Lunch', 'Afternoon Snack', 'Dinner']
            latest_meals_with_rates, id_meal = get_meals_with_rates_for_client(client_id, st.session_state.active_day)
            already_exists_approved_meal = {}
            already_exists_approved_meal_explanations = {}

            if latest_meals_with_rates:
                for index, re_meal_type in enumerate(meal_types):  # ret_meal_types
                    already_exists_approved_meal[index] = latest_meals_with_rates[re_meal_type][0]
                    already_exists_approved_meal_explanations[index] = latest_meals_with_rates[re_meal_type][2]

            render_frame(st.session_state.active_day, already_exists_approved_meal, already_exists_approved_meal_explanations, id_meal)

        else:
            st.write("Please select a day.")