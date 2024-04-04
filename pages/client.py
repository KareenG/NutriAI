import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import re
from database_manager import fetch_client_details, fetch_all_client_bloodTest_as_dict, add_meal_plan,\
    add_rule, get_meals_with_rates_for_client, get_new_meal_plan, change_meal_of_meal_plan,\
    display_progress, get_feedback_score, classify_comment, add_guideline


client_id = 0
client_name = ""
client_data=[]
calorie_per_day = 0
physical_activity = ''


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
        # show the latest blood test results
        blood_tests_dict, blood_test_latest_date_dict = fetch_all_client_bloodTest_as_dict()
        if client_id in blood_test_latest_date_dict.keys():
            st.write(f"**Result of blood tests as of date {blood_test_latest_date_dict[client_id]}** :")
            if client_id in blood_tests_dict.keys():
                for key in blood_tests_dict[client_id].keys():
                    if key not in ['age', 'gender', 'health_condition']:
                        blood_tests_list.append(key)
                        st.write(f"{key} : {blood_tests_dict[client_id][key]}")


    with col2_client_info:
        # we will ask gemini to give as a number between 1-10 of client satisfaction based on his feedbacks.
        satisfaction_level, at_most_three_feedbacks = get_feedback_score(client_id) #7  # Example client satisfaction score
        if type(satisfaction_level) == float:
            display_progress(satisfaction_level)
        else:
            st.write(satisfaction_level)

        # Use HTML to add space; adjust height as needed
        st.markdown('<br><br>', unsafe_allow_html=True)

        #at_most_three_feedbacks = ['efces', 'fcewrfcwer']
        if at_most_three_feedbacks:
            st.write('These are the last 3 previous feedbacks this client left for you: ')
            l = 1
            for feed in at_most_three_feedbacks:
                st.write(f"{l}.  {feed}")
                l += 1

    return client_data['calorie_per_day'], blood_tests_list


st.markdown(f"**Write here a general guideline to take into account when generating a meal."
            f" This guideline will be applied to all clients. Click submit to add the guideline. "
            f"Write it as general as possible.**")
guideline = st.text_input(f"General guideline")
if st.button('Submit general guideline'):
    if guideline:
        add_guideline(guideline)


    # Use client_id and client_name to display more details
    # and perform other actions specific to the client.

if st.session_state.get('prev_nutri', False) and 'selected_client_idMore' in st.session_state.keys() and 'selected_client_nameMore' in st.session_state.keys():
    client_id = st.session_state['selected_client_idMore']
    client_name = st.session_state['selected_client_nameMore']
    calorie_per_day, blood_tests_list = run_client_more_info(client_id, client_name)

else:
    switch_page("nutri")


def on_click_approve_flag():
    # Set a flag in the session state to indicate the approve button has been clicked for this day
    day = st.session_state['action_day']
    meal_plan_to_add = st.session_state[f'meal_plan_to_add_{day}']
    meal_plan_explanations_to_add = st.session_state[f'meal_plan_explanations_to_add_{day}']
    # Now, add your logic to add the meal plan for the specific day
    add_meal_plan(client_id, day, meal_plan_to_add, meal_plan_explanations_to_add)
    # Optionally, set a flag to indicate the meal plan has been added
    if st.session_state.get(f"meal_plan_to_to_sent_{st.session_state.active_day}", None) is not None:
        del st.session_state[f"meal_plan_to_to_sent_{st.session_state.active_day}"]
        del st.session_state[f"meal_plan_to_to_sent_explanations_{st.session_state.active_day}"]







def render_frame(day, already_exists_approved_meal, already_exists_approved_meal_explanations):
    # Key action flags from session state
    if already_exists_approved_meal and st.session_state.get(f"meal_plan_to_to_sent_{day}", None) is None:
        flag_approved = True
        show_reg_buttons_flag = False
        show_approve_button_flag = False
    else:
        flag_approved = False
        show_reg_buttons_flag = True
        show_approve_button_flag = True


    st.write(f"Meal Plan for Day {day} - Approximately {calorie_per_day} calories")

    edit_approved_meal = False

    if "edit_clicked" not in st.session_state:
        st.session_state.edit_clicked = {}

    meal_types = ['Breakfast', 'Mid-Morning Snack', 'Lunch', 'Afternoon Snack', 'Dinner']

    if st.session_state.get(f"edit_meals_day_clicked_{day}", False):
        show_reg_buttons_flag = True

    if flag_approved:
        if st.button(f"Edit", key=f"edit_meals_day_{day}"):
            st.session_state[f"edit_meals_day_clicked_{day}"] = True

    if flag_approved and edit_approved_meal:
        show_reg_buttons_flag = True


    all_meal_plan = ''
    if not already_exists_approved_meal:  # No approved meal plan for this client and day
        all_meal_plan, current_meals_nested_list = get_new_meal_plan(client_id, calorie_per_day)
        #print(current_meals_nested_list)
        for index, value in enumerate(meal_types):
            already_exists_approved_meal[index] = current_meals_nested_list[value][2]
            already_exists_approved_meal_explanations[index] = current_meals_nested_list[value][3]


    for block in range(0, 5):
        col1, col2 = st.columns((30, 16))

        # Column 1: Text generated by another function
        with col1:
            st.write(already_exists_approved_meal[block])
            st.write(f"**Explanation**: {already_exists_approved_meal_explanations[block]}")
            if not flag_approved:
                if st.session_state.get(f"new_prompt_{day}_{block}", None) is not None:
                    new_meal = st.session_state[f"new_prompt_{day}_{block}"]
                    new_meal_feed = st.session_state[f"new_prompt_explanations_{day}_{block}"]

                    already_exists_approved_meal[block] = new_meal
                    already_exists_approved_meal_explanations[block] = new_meal_feed

                    st.session_state[f"new_prompt_{day}_{block}"] = None
                    st.session_state[f"new_prompt_explanations_{day}_{block}"] = None

            else:
                if st.session_state.get(f"new_prompt_{day}_{block}", None) is not None:
                    new_meal = st.session_state[f"new_prompt_{day}_{block}"]
                    new_meal_feed = st.session_state[f"new_prompt_explanations_{day}_{block}"]

                    already_exists_approved_meal[block] = new_meal
                    already_exists_approved_meal_explanations[block] = new_meal_feed

                    st.session_state[f"new_prompt_{day}_{block}"] = None
                    st.session_state[f"new_prompt_explanations_{day}_{block}"] = None

        # Column 2: Button
        with col2:
            if show_reg_buttons_flag:

                if st.button("🔄", key=f"edit_{day}_{block}"):
                    # Use session state to track that the edit button has been clicked for this block
                    st.session_state[f"edit_clicked_{day}_{block}"] = True
                if st.session_state.get(f"edit_clicked_{day}_{block}", False):
                    new_meal, new_meal_feed = '', ''
                    input_key = f"input_{day}_{block}"
                    submit_key = f"submit_{day}_{block}"
                    option_list = blood_tests_list.copy()
                    option_list.append('Other')
                    explanations = {}

                    # Header
                    st.write(
                        f"Reason of why you chose to change this meal and what is the problem with the proposed meal:")

                    # Render checkboxes and text inputs
                    opt_num = 0
                    for option in option_list:
                        if st.checkbox(option, key=f"checkbox_{day}_{block}_{opt_num}"):
                            explanations[option] = st.text_input(f"Brief explanation for {option}", key=f"input_{option}_{day}_{block}")
                        opt_num += 1
                    # Submit button
                    if st.button("Submit", key=submit_key):#if st.button('Submit'):
                        # Use session state to track that the submit button has been clicked for this block
                        st.session_state[f"submit_clicked_rest_{day}_{block}"] = True
                        # add rules
                        for option, expla in explanations.items():
                            match = re.search(r'\((.*?)\)', option)
                            option_en = option
                            if match:
                                option_en = match.group(1)
                            meal_t = meal_types[block]
                            current_meal_to_change = ''
                            if block in already_exists_approved_meal.keys():
                                current_meal_to_change = already_exists_approved_meal[block]
                            if expla:
                                #expla_reason_type, expla_text = extract_reason_type_and_restrictions(client_id, meal_types[block], current_melas_nested_list[block], cal_per_meal_type[block], expla)
                                if option == 'Other' and classify_comment(expla):
                                    add_rule(option_en.lower(), expla, client_id, meal_t.lower(), already_exists_approved_meal[block])  # expla
                                if option != 'Other':
                                    add_rule(option_en.lower(), expla, client_id, meal_t.lower(),
                                             already_exists_approved_meal[block])


                        new_meal_info = change_meal_of_meal_plan(client_id, current_meal_plan=all_meal_plan, nutri_comment_temp=expla,
                                                 meal_to_change=already_exists_approved_meal[block], meal_type=meal_types)

                        new_meal = new_meal_info[2]
                        new_meal_feed = new_meal_info[3]

                        st.session_state[f"new_prompt_w_{day}_{block}"] = new_meal
                        st.session_state[f"new_prompt_explanations_w_{day}_{block}"] = new_meal_feed

                        st.write('new generated meal:')
                        #st.markdown('<br>', unsafe_allow_html=True)
                        st.write(new_meal)
                        st.write(f"**Explanation**: {new_meal_feed}")

                    if st.session_state.get(f"submit_clicked_rest_{day}_{block}", False):

                        if st.button("Submit Change", key=f"submit_change_{day}_{block}"):  # if st.button('Submit'):
                            # Use session state to track that the submit changes button has been clicked for this block

                            already_exists_approved_meal[block] = st.session_state[f"new_prompt_w_{day}_{block}"]
                            already_exists_approved_meal_explanations[block] = st.session_state[f"new_prompt_explanations_w_{day}_{block}"]
                            # Update the session state for the text to display in col1
                            st.session_state[f"new_prompt_{day}_{block}"] = st.session_state[f"new_prompt_w_{day}_{block}"]
                            st.session_state[f"new_prompt_explanations_{day}_{block}"] = st.session_state[f"new_prompt_explanations_w_{day}_{block}"]

                            del st.session_state[f"new_prompt_w_{day}_{block}"]
                            del st.session_state[f"new_prompt_explanations_w_{day}_{block}"]
                            del st.session_state[f"submit_clicked_rest_{day}_{block}"]
                            del st.session_state[f"edit_clicked_{day}_{block}"]

    if show_approve_button_flag:
        st.session_state['action_day'] = day
        st.session_state[f'meal_plan_to_add_{day}'] = already_exists_approved_meal
        st.session_state[f'meal_plan_explanations_to_add_{day}'] = already_exists_approved_meal_explanations
        if st.button("Approve",
                     key=f"approve_button_{day}", on_click=lambda: on_click_approve_flag()):#on_click=on_click_approve_flag(day, already_exists_approved_meal)):
            st.header(f"✅")
            st.session_state[f"show_approve_button_of_day_{st.session_state.active_day}"] = False

    else:
        st.header(f"✅")

    return already_exists_approved_meal, already_exists_approved_meal_explanations#, add_flag





# Function to update the session state to indicate the button has been clicked
def on_button_click():
    st.session_state.button_clicked = True
    st.session_state[f"return_meal_plan_{day}"] = False


# Initialize session state
if 'active_day' not in st.session_state:
    st.session_state.active_day = None

st.markdown('<br>', unsafe_allow_html=True)
st.markdown(f"""
**Notes**:

* A "block" refers to the assigned area for each meal.

* If a meal plan for a specific day hasn't been approved yet, clicking on that day's button will automatically
 create one. Once generated, you can:
    1. Approve it if suitable by clicking the "Approve" button that appears in the bottom of the meal plan.
    2. Regenerate the meal by clicking the same day button again or use the regenerate buttons 🔄 for specific meals.
 To generate a specific meal without specifying a reason, select "other" and click "Submit" in the relevant block.
  It's recommended to provide reasons for issues with the current meal so the system can learn and improve. Lastly,
  if the new generated one which will appear below the "Submit" button, is a meal you want to replace the current 
  meal with then "Submit Change". The meal plan then will be updated with the new meal, to approve and save this meal 
  plan, click the "Approve" button that appears in the bottom of the meal plan.

* To permanently influence the generation of meal plans for a client, include comments with 'always' in any block;
 otherwise, comments are considered specific to the current meal only and will influence only the next meal plan generation.

* An "approved" meal plan is indicated by a green checkmark ✅ at its bottom.

* To edit an approved meal, click the "edit" button at the top of the meal plan.

* Review client feedback to determine if the meal plan requires modifications.
""")
st.markdown('<br>', unsafe_allow_html=True)


# Main layout columns for days buttons and frame content
button_col, _, frame_col= st.columns([1, 0.1, 7])

# Render days buttons
with button_col:
    st.write("## Days")  # Header for the button column
    for day in range(1, 8):
        if st.button(f"Day {day}", key=f"day_{day}"):
            st.session_state.active_day = day

            if st.session_state.get(f"meal_plan_to_to_sent_{st.session_state.active_day}", None) is not None:
                st.session_state[f"meal_plan_to_to_sent_{st.session_state.active_day}"] = None
                st.session_state[
                    f"meal_plan_to_to_sent_explanations_{st.session_state.active_day}"] = None


# Render the frame based on the selected day
with frame_col:
    if st.session_state.active_day is not None:
        meal_types = ['Breakfast', 'Mid-Morning Snack', 'Lunch', 'Afternoon Snack', 'Dinner']
        latest_meals_with_rates, id_meal = get_meals_with_rates_for_client(client_id, st.session_state.active_day)
        already_exists_approved_meal = {}
        already_exists_approved_meal_explanations = {}


        if latest_meals_with_rates:
            for index, re_meal_type in enumerate(meal_types):
                already_exists_approved_meal[index] = latest_meals_with_rates[re_meal_type][0]
                already_exists_approved_meal_explanations[index] = latest_meals_with_rates[re_meal_type][2]

        if st.session_state.get(f"meal_plan_to_to_sent_{st.session_state.active_day}", None) is not None:
            meal_plan_to_add, meal_plan_explanations_to_add = render_frame(st.session_state.active_day,
                                                                            st.session_state[f"meal_plan_to_to_sent_{st.session_state.active_day}"],
                                                                            st.session_state[
                                                                                f"meal_plan_to_to_sent_explanations_{st.session_state.active_day}"])
            st.session_state[f"show_approve_button_of_day_{st.session_state.active_day}"] = True

        else:
            if not latest_meals_with_rates:
                st.session_state[f"show_approve_button_of_day_{st.session_state.active_day}"] = True

            meal_plan_to_add,  meal_plan_explanations_to_add = render_frame(st.session_state.active_day, already_exists_approved_meal, already_exists_approved_meal_explanations)

        if 'active_day' in st.session_state:
            active_day = st.session_state.active_day
            # Check if the approve button for the active day has been clicked
            if st.session_state.get(f"approve_clicked_{active_day}", False):
                # Add the meal plan here because the approve button has been clicked
                add_meal_plan(client_id, active_day, meal_plan_to_add, meal_plan_explanations_to_add)
                # Reset the flag to prevent repeated adds on refresh
                st.session_state[f"approve_clicked_{active_day}"] = False

                if st.session_state.get(f"meal_plan_to_to_sent_{st.session_state.active_day}", None) is not None:
                    del st.session_state[f"meal_plan_to_to_sent_{st.session_state.active_day}"]
                    del st.session_state[f"meal_plan_to_to_sent_explanations_{st.session_state.active_day}"]


        latest_meals_with_rates_after_render, id_meal_r = get_meals_with_rates_for_client(client_id, st.session_state.active_day)
        changes_flag_without_approve = False
        if latest_meals_with_rates_after_render:
            for index, re_meal_type in enumerate(meal_types):  # ret_meal_types
                if meal_plan_to_add[index] != latest_meals_with_rates_after_render[re_meal_type][0]:
                    changes_flag_without_approve = True
                    break
        else:
            changes_flag_without_approve = True

        if changes_flag_without_approve:
            st.session_state[f"meal_plan_to_to_sent_{st.session_state.active_day}"] = meal_plan_to_add.copy()
            st.session_state[
                f"meal_plan_to_to_sent_explanations_{st.session_state.active_day}"] = meal_plan_explanations_to_add.copy()

    else:
        st.write("Please select a day.")