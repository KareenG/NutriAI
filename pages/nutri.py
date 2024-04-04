from datetime import date
import st_keyup
import streamlit as st
from database_manager import add_client, get_all_clients, fetch_client_details, get_blood_tests, insert_client_blood_test, get_feedback_score, fetch_all_client_bloodTest_as_dict
from datetime import datetime
from streamlit_extras.switch_page_button import switch_page


def display_client_registration_form():
    if st.session_state.get('show_add_client_form', False):
        with st.form("add_client_form", clear_on_submit=True):
            name = st.text_input("Name")
            id_number = st.number_input("ID Number", format="%d", step=1)
            age = st.number_input("Age", format="%d", step=1, min_value=0)
            gender = st.radio("Gender", options=["Male", "Female"])
            current_weight = st.number_input("Current Weight", format="%f")
            goal_weight = st.number_input("Goal Weight", format="%f")
            height = st.number_input("Height (cm)", format="%d", step=1)
            active_in_sports = st.radio("Active in Sports", options=["Lightly (little or no exercise)", "Moderate (exercise 1–3 days/week)", "Highly (exercise 4+ days/week)"])
            liked_meals = st.text_input("Liked Meals (separate with commas)")
            vegetables = [
                "Artichoke", "Red onion", "Spinach", "Sweet potato", "Tomato", "Yam",
                "Asparagus", "Carrot", "Cauliflower", "Celery", "Chayote", "Bamboo shoots",
                "Bean sprouts", "Green onion", "Leek", "Lettuce", "Mushroom", "Onion",
                "Parsnip", "Beans", "Beetroot", "Pepper", "Potato", "Pumpkin", "Radicchio",
                "Radish", "Bell pepper", "Broccoli", "Brussels sprouts", "Cabbage", "Cactus pear",
                "Collard greens", "Corn", "Cucumber", "Eggplant", "Endive", "Escarole", "Garlic",
                "Green beans", "Pea", "Red cabbage", "Red chili pepper", "Yellow squash", "Zucchini"
            ]

            # Remove duplicates from the list
            vegetables = list(dict.fromkeys(vegetables))

            # Streamlit multi-select widget
            selected_vegetables = st.multiselect('Select your favorite vegetables:', vegetables)

            # Concatenate selected vegetables into a string separated by commas
            liked_vegetables = ', '.join(selected_vegetables)
            #liked_fruits = st.text_input("Liked Fruits (separate with commas)")

            # List of fruits
            fruits = [
                "Apple", "Apricot", "Avocado", "Banana", "Blueberry", "Cherry", "Coconut",
                "Grape", "Grapefruit", "Fig", "Kiwi", "Lemon", "Lime", "Mandarin", "Mango",
                "Melon", "Nectarine", "Orange", "Papaya", "Passion fruit", "Peach", "Pear",
                "Pineapple", "Plum", "Pomegranate", "Raspberry", "Strawberry", "Watermelon",
                "Lychee", "Pomelo", "Jackfruit", "Wax Apples", "Rambutan", "Durian",
                "Asian Pear", "Mangosteen", "Longan", "Guava", "Lotus Fruit", "Sugar Apple",
                "Chinese Bayberry", "Starfruit", "Pulasan", "Kumquat", "Breadfruit",
                "Dragon Fruit", "Santol", "Langsat", "Snake Fruit", "Japanese Persimmon", "Passion Fruit"
            ]

            # Remove duplicates from the list
            fruits = list(dict.fromkeys(fruits))

            # Streamlit multi-select widget
            selected_fruits = st.multiselect('Select your favorite fruits:', fruits)
            liked_fruits = ', '.join(selected_fruits)


            liked_snacks = st.text_input("Liked Snacks (separate with commas)")
            dislikes = st.text_input("Dislikes (separate with commas)")
            health_condition = st.multiselect("Health Condition", options=[
                "Healthy", "Diabetes", "Cardiovascular", "Obesity", "Osteoporosis", "Allergies and intolerances",
                "Cancer", "Digestive disorders", "Kidney disease", "Malnutrition", "Anaemia",
                "Arthritis", "Celiac disease", "Chronic hepatitis", "Eating disorders",
                "HIV/AIDS", "IBS"
            ])


            submit_button = st.form_submit_button("Submit")

            if submit_button:
                flag_submit = True
                if not health_condition:
                    health_condition_state = "Healthy"
                else:
                    health_condition_state = ','.join(health_condition)

                # Split by comma and strip spaces
                cleaned_items = [item.strip() for item in liked_meals.split(',')]

                # Validate items and normalize internal spaces
                valid_items = []
                for item in cleaned_items:
                    # Normalize internal spaces (replace multiple spaces with a single space)
                    normalized_item = ' '.join(item.split())
                    # Check if the item contains only letters (allowing spaces)
                    if liked_meals and not normalized_item.replace(" ", "").isalpha():
                        st.error("Liked meals must only contain letters, commas, and spaces.")
                        flag_submit = False
                        break
                    valid_items.append(normalized_item)

                # Only update liked_meals if all items are valid
                else:
                    liked_meals = ', '.join(valid_items)

                cleaned_items = [item.strip() for item in liked_snacks.split(',')]

                # Validate items and normalize internal spaces
                valid_items = []
                for item in cleaned_items:
                    # Normalize internal spaces (replace multiple spaces with a single space)
                    normalized_item = ' '.join(item.split())
                    # Check if the item contains only letters (allowing spaces)
                    if liked_snacks and not normalized_item.replace(" ", "").isalpha():
                        st.error("Liked snacks must only contain letters, commas, and spaces.")
                        flag_submit = False
                        break
                    valid_items.append(normalized_item)

                # Only update liked_meals if all items are valid
                else:
                    liked_snacks = ', '.join(valid_items)

                cleaned_items = [item.strip() for item in dislikes.split(',')]

                # Validate items and normalize internal spaces
                valid_items = []
                for item in cleaned_items:
                    # Normalize internal spaces (replace multiple spaces with a single space)
                    normalized_item = ' '.join(item.split())
                    # Check if the item contains only letters (allowing spaces)
                    if dislikes and not normalized_item.replace(" ", "").isalpha():
                        st.error("Dislikes must only contain letters, commas, and spaces.")
                        flag_submit = False
                        break
                    valid_items.append(normalized_item)

                # Only update liked_meals if all items are valid
                else:
                    dislikes = ', '.join(valid_items)
                # Assuming you have a function to insert data into the database
                if flag_submit:

                    add_client(name, id_number, age, gender, current_weight, goal_weight, height,
                               active_in_sports, liked_meals, liked_vegetables, liked_fruits,
                               liked_snacks, dislikes, health_condition_state)


                    st.success("Client added successfully!")
                    st.session_state['show_add_client_form'] = False  # Hide the form after submission


def display_blood_test_form(client_id, client_name):
    if 'selected_addBT_action' in st.session_state:
        # Ensure session state keys are initialized at the start
        if 'test_results' not in st.session_state:
            st.session_state.test_results = []
        if 'input_key' not in st.session_state:
            st.session_state.input_key = 0
        if 'available_tests' not in st.session_state:
            st.session_state.available_tests = get_blood_tests()
        st.write(f"Adding new blood test for: {client_name} (ID: {client_id})")
        # Ensure initialization of session state keys as previously demonstrated

        # Fetch available tests and add a placeholder at the beginning of the list
        available_tests = [("placeholder", "Choose Test Name")] + st.session_state['available_tests']

        # Date input for the test date
        test_date = st.date_input("Date of the Blood Test", value=date.today(), max_value=date.today(),
                                  key=f"date_{st.session_state['input_key']}")

        # Select box for choosing a test with a placeholder as the first option
        selected_test = st.selectbox("Select Blood Test", options=available_tests, format_func=lambda x: x[1], index=0)

        # Text input for the test result
        new_result = st.text_input("Test Result", key=f"new_result_{st.session_state['input_key']}")

        # Add Test Result button with logic to handle placeholder selection
        if st.button("Add Test Result"):
            if selected_test[0] == "placeholder":
                st.error("Please choose a test name.")
            elif not new_result:
                st.error("Please enter a test result.")
            else:
                #add_test_result(selected_test, new_result, test_date)
                st.session_state['test_results'].append(
                    {"test_name": selected_test[1], "result": new_result, "test_date": test_date})
                st.session_state['available_tests'] = [test for test in st.session_state['available_tests'] if
                                                       test != selected_test]
                st.session_state['input_key'] += 1  # Increment to refresh input fields

        # Display current test results
        if 'test_results' in st.session_state:
            st.write("Current test results:")
            for test in st.session_state['test_results']:
                st.write(f"{test['test_name']} : {test['result']}")

        if st.button("Submit All Test Results"):
            # Check if a client has been selected and is stored in the session state
            if 'selected_client_id' in st.session_state:
                # Call the submit_all_test_results function with the selected client's ID
                submit_all_test_results(st.session_state['selected_client_id'])
                st.session_state['finished_add_blood_test'] = True
            else:
                st.error("No client selected for submitting test results.")



def add_test_result(selected_test, result, test_date):
    """Append a new test result to the session state list and reset available tests."""
    st.session_state['test_results'].append({"test_name": selected_test[1], "result": result, "test_date": test_date})
    st.session_state['available_tests'] = [test for test in st.session_state['available_tests'] if test != selected_test]
    st.session_state['input_key'] += 1  # Increment to refresh input fields


def submit_all_test_results(client_id):
    # Fetch client details from the database or session state
    client_details = fetch_client_details(client_id)  # Make sure to implement this function

    for test_result in st.session_state['test_results']:
        insert_client_blood_test(client_id,
                   client_details['name'],
                   client_details['age'],
                   client_details['gender'],
                   client_details.get('health_condition', ''),  # Example: handle missing details
                   test_result['test_name'],
                   test_result['result'],
                   test_result['test_date'])


    # Clear session state after successful submission
    st.session_state['test_results'] = []
    st.success("All test results submitted successfully.")



















def run_nutri():
    if 'selected_more_action' in st.session_state and 'selected_client_idMore' in st.session_state and 'selected_client_nameMore' in st.session_state:
        id_client = st.session_state['selected_client_idMore']
        name_client = st.session_state['selected_client_nameMore']
        # Clear the page
        st.empty()

    clients = get_all_clients()
    st.header("Clients Dashboard")


    # Button to toggle the client registration form
    if st.button('Add Client'):
        st.session_state['show_add_client_form'] = True


    if not clients:
        st.write("There are no clients to display.")
    else:
        st.markdown("""
        -  ⚠️ Indicates that there is an issue regarding the progress of the client. Please contact him/her.
        -  ⬆️ Indicates that it has been 6 months since the last blood test. Consider to ask the client to provide
                 a new blood test.
        """)

        blood_tests_dict, blood_test_latest_date_dict = fetch_all_client_bloodTest_as_dict()

        col_widths = [5, 4, 15]
        cols = st.columns(col_widths)
        headers = ["ID Number", "Name", "Actions"]

        for col, header in zip(cols, headers):
            col.markdown(f"**{header}**")

        for id_number, name in clients:
            cols = st.columns(col_widths)
            with cols[0]:
                if id_number in blood_test_latest_date_dict:
                    # if blood_test_latest_date_dict[id_number]:
                    date_of_last_BT = datetime.strptime(blood_test_latest_date_dict[id_number], "%Y-%m-%d")
                    # Get the current date
                    current_date = datetime.now()
                    # Calculate the difference between the two dates
                    difference = current_date - date_of_last_BT

                    # Check if the difference is at least 4 months (approximately 4 * 30 days)
                    new_blood_test_needed_flag = difference.days >= 6 * 30

                else:  # no blood tests yet
                    new_blood_test_needed_flag = True
                progress_by_feedbacks_score, at_most_three_feedbacks = get_feedback_score(id_number)

                if type(progress_by_feedbacks_score) == float:
                    check_on_client_flag = progress_by_feedbacks_score <= 4
                else:  # no feedbacks yet
                    check_on_client_flag = True


                if new_blood_test_needed_flag and check_on_client_flag:
                    id_with_icons = f"`{id_number}` ⚠️ ⬆️"
                elif new_blood_test_needed_flag and not check_on_client_flag:
                    id_with_icons = f"`{id_number}` ️ ⬆️"
                elif not new_blood_test_needed_flag and check_on_client_flag:
                    id_with_icons = f"`{id_number}` ⚠️ ️"
                else:
                    id_with_icons = f"`{id_number}`"

                st.markdown(id_with_icons, unsafe_allow_html=True)

            cols[1].markdown(f"{name}", unsafe_allow_html=True)


            with cols[2]:
                # Reset or initialize form-related session state when the button is clicked
                if st.button("Add New Blood Test", key=f"add_{id_number}"):
                    # Reset session state related to the blood test form
                    st.session_state['selected_client_id'] = id_number
                    st.session_state['selected_client_name'] = name
                    st.session_state['selected_addBT_action'] = True
                    # Initialize or reset the form state
                    st.session_state['test_results'] = []  # Reset test results
                    st.session_state['input_key'] = 0  # Reset input key
                    st.session_state['available_tests'] = get_blood_tests()  # Refresh the list of available tests

                if st.button("More", key=f"more_{id_number}"):
                    # Set session state variables for client ID and name
                    st.session_state['selected_client_idMore'] = id_number
                    st.session_state['selected_client_nameMore'] = name
                    st.session_state['selected_more_action'] = True
                    st.session_state['prev_nutri'] = True
                    switch_page("client")


        # Check if a client has been selected for adding a new blood test
        if 'selected_addBT_action' in st.session_state and 'selected_client_id' in st.session_state and 'selected_client_name' in st.session_state:
            # Call display_blood_test_form with the selected client's ID and name
            # client_id = st.session_state['selected_client_id']
            # client_name = st.session_state['selected_client_name']
            # st.session_state['finished_add_blood_test'] = False

            #while not st.session_state.get('finished_add_blood_test', False):
            display_blood_test_form(st.session_state['selected_client_id'],
                                    st.session_state['selected_client_name'])

    # Display the client registration form if the flag is set
    if st.session_state.get('show_add_client_form', False):
        display_client_registration_form()







##################################################################################

# # Initialize session state variables if not already set
# if 'all_tests' not in st.session_state:
#     st.session_state['all_tests'] = get_blood_tests()  # Fetch and store all available test names
# if 'selected_tests' not in st.session_state:
#     st.session_state['selected_tests'] = []  # Track user-selected tests
# if 'current_test' not in st.session_state:
#     st.session_state['current_test'] = ''  # Currently selected test for result entry
# if 'test_result' not in st.session_state:
#     st.session_state['test_result'] = ''  # Placeholder for inputting a test result
#
# # Function to handle adding test result
# def add_test_result():
#     # Example function that could update a database or just print to console
#     test_name = st.session_state['current_test']
#     test_result = st.session_state['test_result']
#     print(f"Added result for {test_name}: {test_result}")  # Replace with actual logic
#
#     # Remove the selected test from 'all_tests' and reset 'current_test'
#     if test_name in st.session_state['all_tests']:
#         st.session_state['all_tests'].remove(test_name)
#         st.session_state['selected_tests'].append((test_name, test_result))
#     st.session_state['current_test'] = ''
#     st.session_state['test_result'] = ''  # Reset test result input
#
# # Conditionally display the selectbox and related inputs if there are tests left to select
# if st.session_state['all_tests']:
#     # Dropdown to select the test name
#     st.session_state['current_test'] = st.selectbox(
#         'Select Blood Test',
#         options=st.session_state['all_tests'],
#         key='current_test'
#     )
#
#     # Text input for the test result
#     st.session_state['test_result'] = st.text_input('Test Result', key='test_result')
#
#     # Button to add test result
#     if st.button('Add Test Result'):
#         add_test_result()
# else:
#     st.write('All tests have been selected.')
#
# # Displaying selected tests
# st.write('Current test results:')
# for test_name, test_result in st.session_state['selected_tests']:
#     st.write(f"{test_name}: {test_result}")
#
# # Button to submit all test results
# if st.button('Submit All Test Results'):
#     # Example submission logic
#     st.write('All test results submitted.')  # Replace with your logic to submit results
#     # Here you could iterate over 'selected_tests' and perform submission logic for each
#     # After submission, you might want to reset 'selected_tests' or redirect the user, etc.

##################################################################################

run_nutri()