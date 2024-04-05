import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import re
import random
from datetime import datetime
import streamlit as st
import google.generativeai as genai
# importing os module for environment variables
import os
# importing necessary functions from dotenv library
from dotenv import load_dotenv, dotenv_values


# loading variables from .env file
load_dotenv()


def create_database():
    conn = sqlite3.connect('my_rules.db')
    c = conn.cursor()  # ruleType TEXT
    c.execute('''CREATE TABLE IF NOT EXISTS rules
                 (id_rule INTEGER PRIMARY KEY AUTOINCREMENT,
                  rule TEXT NOT NULL,
                  
                  restrictions TEXT,
                  id_client INTEGER,
                  meal_type TEXT,
                  meal_info TEXT,
                  FOREIGN KEY (id_client) REFERENCES clients(id_number))''')

    # Create the 'clients' table with the specified columns
    c.execute('''CREATE TABLE IF NOT EXISTS clients
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      id_number INTEGER UNIQUE NOT NULL,
                      age INTEGER,
                      gender TEXT,
                      current_weight REAL,
                      goal_weight REAL,
                      height REAL,
                      active_in_sports TEXT,
                      liked_meals TEXT,
                      liked_veg TEXT,
                      liked_fruits TEXT,
                      liked_snacks TEXT,
                      dislikes TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS normalBloodTests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    mark TEXT NOT NULL,
    measurement_units TEXT,
    normal_range TEXT,
    bloodTestType TEXT
    )''')


    c.execute('''CREATE TABLE IF NOT EXISTS clientsBloodTests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_client TEXT INTEGER UNIQUE NOT NULL,
    client_name TEXT,
    age INTEGER,
    gender TEXT,
    health_condition TEXT,
    blood_test_name TEXT,
    test_result TEXT,
    date_of_blood_test DATE,
    FOREIGN KEY (id_client) REFERENCES clients(id_number),
    FOREIGN KEY (blood_test_name) REFERENCES normalBloodTests(name))''')

    


    c.execute('''CREATE TABLE IF NOT EXISTS clients_meals_with_rates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_client INTEGER NOT NULL,
        day_number INTEGER,
        date_of_meal_plan DATE,
        breakfast TEXT,
        breakfast_rate TEXT,
        snack1 TEXT,
        snack1_rate TEXT,
        lunch TEXT,
        lunch_rate TEXT,
        snack2 TEXT,
        snack2_rate TEXT,
        dinner TEXT,
        dinner_rate TEXT,
        breakfast_explanations TEXT,
        
        snack1_explanations TEXT,

        lunch_explanations TEXT,

        snack2_explanations TEXT,

        dinner_explanations TEXT,

        FOREIGN KEY (id_client) REFERENCES clients(id_number)
        )''')



    c.execute('''CREATE TABLE IF NOT EXISTS clients_feedback_for_nutri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_client INTEGER NOT NULL,
            date_of_feedback DATE,
            feedback TEXT,
            FOREIGN KEY (id_client) REFERENCES clients(id_number)
            )''')

    c.execute('''CREATE TABLE IF NOT EXISTS general_guidelines
                     (guideline TEXT)''')

    conn.commit()
    conn.close()


# Initialize database and table
create_database()


# Add rule to the rules table
def add_rule(rule, restriction, id_c, meal_t, meal_data):
    conn = sqlite3.connect('my_rules.db')
    c = conn.cursor()
    c.execute("INSERT INTO rules (rule, restrictions, id_client, meal_type, meal_info) VALUES (?, ?, ?, ?, ?)", (rule, restriction, id_c, meal_t, meal_data))
    conn.commit()
    conn.close()


# Extract all restrictions from the rules table
def get_all_rules():
    conn = sqlite3.connect('my_rules.db')
    c = conn.cursor()
    for row in c.execute('SELECT * FROM rules'):
        print(row)  # This will now include the ruleType value
    conn.close()


# Add client to the clients table
def add_client(name, id_number, age, gender, current_weight, goal_weight, height, active_in_sports, liked_meals, liked_veg, liked_fruits, liked_snacks, dislikes, health_condition):
    if not liked_meals:
        liked_meals = 'No preference'
    if not liked_veg:
        liked_veg = 'No preference'
    if not liked_fruits:
        liked_fruits = 'No preference'
    if not liked_snacks:
        liked_snacks = 'No preference'
    if not dislikes:
        dislikes = 'No preference'
    conn = sqlite3.connect('my_rules.db')
    c = conn.cursor()
    c.execute('''INSERT INTO clients (name, id_number, age, gender, current_weight, goal_weight, height, active_in_sports, liked_meals, liked_veg, liked_fruits, liked_snacks, dislikes, health_condition)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (name, id_number, age, gender, current_weight, goal_weight, height, active_in_sports, liked_meals, liked_veg, liked_fruits, liked_snacks, dislikes, health_condition))
    conn.commit()
    conn.close()


def add_guideline(guideline):
    model = genai.GenerativeModel('gemini-pro')
    genai.configure(api_key='AIzaSyC1KgUEcEDdzGtPhOx7FsJ6cYxexjA1mUE')

    # cont = 'is this text ' + guideline + ' understandable or has any meaning? if Yes the response should be "True", ' \
    #                                        'otherwise "False"'
    response = model.generate_content(guideline)#cont)
    response_text = response.text
    if response_text == "False":
        print(f"This guideline: {guideline} has no meaning, Therefor, ignored.")
    else:
        conn = sqlite3.connect('my_rules.db')
        c = conn.cursor()
        c.execute("INSERT INTO general_guidelines (guideline) VALUES (?)", (guideline,))
        conn.commit()
        conn.close()


# Extract name and mark of blood tests from the normalBloodTests table
def get_blood_tests():
    conn = sqlite3.connect('my_rules.db')
    c = conn.cursor()
    c.execute('SELECT mark, name FROM normalBloodTests')
    blood_tests = c.fetchall()
    conn.close()
    return [(f"{test[0]}, {test[1]}", f"{test[1]} ({test[0]})") for test in blood_tests]


# Function to check if an ID exists in the database
def check_id_exists(client_id):
    conn = sqlite3.connect('my_rules.db')
    c = conn.cursor()
    c.execute('SELECT id_number, name FROM clients WHERE id_number = ?', (client_id,))
    result = c.fetchone()
    conn.close()
    return result


# Get ids and names of all clients from the clients table
def get_all_clients():
    conn = sqlite3.connect('my_rules.db')
    c = conn.cursor()
    c.execute('SELECT id_number, name FROM clients')
    clients = c.fetchall()
    conn.close()
    return clients


# Get all details regarding client_id from the clients table
def fetch_client_details(client_id):
    # Connect to database and fetch details
    #print(client_id)
    conn = sqlite3.connect('my_rules.db')
    c = conn.cursor()
    c.execute("SELECT * FROM clients WHERE id_number = ?", (client_id,))
    details = c.fetchone()
    conn.close()
    if details:
        # Map the query result to a dictionary (example, adjust fields accordingly)
        return {
            'name': details[1],  # Assuming 'name' is the second column
            'id': details[2],
            'age': details[3],  # And so on
            'gender': details[4],
            'health_condition': details[14],
            'current_weight': details[5],
            'height': details[7],
            'goal_weight': details[6],
            'calorie_per_day': calculate_calorie_needs(details[7], details[5], details[6], details[3], details[4], details[14], details[8]),
            'active_sport': details[8],
            'liked_meals': details[9],
            'liked_veg': details[10],
            'liked_fruits': details[11],
            'liked_snacks': details[12],
            'dislikes': details[13]


            # Include other fields as needed
        }
    return None


# Get all meals that the client_id rated for a giving day.
def get_meals_with_rates_for_client(client_id, day):
    conn = sqlite3.connect('my_rules.db')
    c = conn.cursor()
    # SQL query to get meals for a specific client and day
    # Order by date first, then by id for entries on the same date
    query = '''
    SELECT 
        breakfast, breakfast_rate, 
        snack1, snack1_rate, 
        lunch, lunch_rate, 
        snack2, snack2_rate, 
        dinner, dinner_rate,
        breakfast_explanations, snack1_explanations, 
        lunch_explanations, snack2_explanations, dinner_explanations, id
    FROM clients_meals_with_rates
    WHERE id_client = ? AND day_number = ?
    ORDER BY date_of_meal_plan DESC, id DESC
    LIMIT 1
    '''
    c.execute(query, (client_id, day))
    # Fetch the result
    result = c.fetchone()
    conn.close()
    # If there is no entry for the given client_id and day, return an empty dict
    if not result:
        return {}, None

    # Creating a dictionary with the meal type as key and a tuple (meal text, rate) as value
    meals_with_rates = {
        'Breakfast': (result[0], result[1], result[10]),
        'Mid-Morning Snack': (result[2], result[3], result[11]),
        'Lunch': (result[4], result[5], result[12]),
        'Afternoon Snack': (result[6], result[7], result[13]),
        'Dinner': (result[8], result[9], result[14]),
    }

    return meals_with_rates, result[15]


# Add meal plan with explanations for a whole giving day for the giving client. When added
# there will be no rates of these meals. The client can rate them later on, in their specific
# page (client_info.py)
def add_meal_plan(client_id, day, meal_dict, meal_explanations_dict):
    # Assuming meal_dict format: meal_dict[0]=Breakfast text, meal_dict[1]=Mid-Morning Snack text, etc.
    # Connect to the SQLite database
    try:
        with sqlite3.connect('my_rules.db') as conn:
            c = conn.cursor()
            # Prepare the current date
            current_date = datetime.now().strftime('%Y-%m-%d')

            # Prepare the SQL statement for inserting a new record
            sql = '''INSERT INTO clients_meals_with_rates (
                            id_client, day_number, date_of_meal_plan,
                            breakfast, breakfast_rate,
                            snack1, snack1_rate,
                            lunch, lunch_rate,
                            snack2, snack2_rate,
                            dinner, dinner_rate,
                            breakfast_explanations, snack1_explanations, 
                            lunch_explanations, snack2_explanations, dinner_explanations
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
            # Prepare the data tuple for insertion
            data = (
                client_id, day, current_date,
                meal_dict[0], None,
                meal_dict[1], None,
                meal_dict[2], None,
                meal_dict[3], None,
                meal_dict[4], None,
                meal_explanations_dict[0],
                meal_explanations_dict[1],
                meal_explanations_dict[2],
                meal_explanations_dict[3],
                meal_explanations_dict[4]
            )
            # Execute the SQL command
            c.execute(sql, data)
            # Commit changes (not needed with 'with' statement, but included for clarity)
            conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        # Handle the error or re-raise it
        raise


# Add rates giving by this client to the giving meal
def update_rates_of_meal(id_meal, meal_type, meal_rate):
    # id_meal is the key of the meal in clients_meals_with_rates table
    # if meal_type = 0 then it is regarding the breakfast meal, 1 - snack1, 2 - lunch, 3 - snack2, 4 -dinner
    conn = sqlite3.connect('my_rules.db')
    c = conn.cursor()

    # Define the mapping of meal_type to the column name
    meal_columns = {
        0: 'breakfast_rate',
        1: 'snack1_rate',
        2: 'lunch_rate',
        3: 'snack2_rate',
        4: 'dinner_rate'
    }

    # Get the correct column name for the meal type
    rate_column = meal_columns.get(meal_type)

    if rate_column is None:
        print("Invalid meal type provided")
        return

    # SQL statement to update the meal rate
    sql = f'''
            UPDATE clients_meals_with_rates
            SET {rate_column} = ?
            WHERE id = ?
        '''

    try:
        # Execute the update statement
        c.execute(sql, (meal_rate, id_meal))
        # Commit the changes
        conn.commit()
        print(f"Meal rate updated successfully for {rate_column}.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the connection
        conn.close()


def get_guidelines():
    conn = sqlite3.connect('my_rules.db')
    c = conn.cursor()

    # Create a query string
    query = f"SELECT guideline FROM general_guidelines"

    # Execute the query
    c.execute(query)

    # Fetch all results from the query
    results = c.fetchall()
    # Commit the changes to the database
    conn.commit()
    #print("Guideline added successfully.")
    conn.close()

    # Convert the results to a list (assuming each row contains only one column)
    column_data = [row[0] for row in results]
    return column_data


# Calculate calorie needed daily based on the current weight, goal,weight, height, age, gender and health condition
def calculate_calorie_needs(height_cm, weight_kg, goal_weight_kg, age, gender, health_condition, activity):
    # The Mifflin-St Jeor equation
    if gender.lower() == 'male':
        bmr = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
    elif gender.lower() == 'female':
        bmr = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)
    else:
        raise ValueError("Gender must be 'male' or 'female'")

    # Here, we'll use a sedentary activity factor
    activity_factor = 1.2  # Little to no exercise or physical activity throughout the day.
    if health_condition == "Healthy":
        if activity == 'Moderate':
            activity_factor = 1.375
        if activity == 'Highly':
            activity_factor = 1.55

    tdee = bmr * activity_factor

    if goal_weight_kg > weight_kg:  # goal: add weight
        tdee = tdee + 500
    elif goal_weight_kg < weight_kg:  # goal: loss weight
        tdee = tdee - 500
    else:  # goal: maintain weight
        pass
    return round(tdee)


# Add blood test of a giving client to the clientsBloodTests
def insert_client_blood_test(client_id, client_name, age, gender, health_condition, blood_test_name, result, date_blood_test):
    # Insert the test result into clientsBloodTests
    #print(client_id)
    conn = sqlite3.connect('my_rules.db')
    c = conn.cursor()
    c.execute('''INSERT INTO clientsBloodTests (id_client, client_name, age, gender, health_condition, blood_test_name, test_result, date_of_blood_test)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (client_id, client_name, age, gender, health_condition, blood_test_name, result, date_blood_test))
    conn.commit()
    conn.close()


# Extract as dict with id_clients as keys all details by the id_clients
def fetch_all_client_details_as_dict():
    # Connect to your database
    conn = sqlite3.connect('my_rules.db')
    conn.row_factory = sqlite3.Row  # Set the row_factory to sqlite3.Row
    cursor = conn.cursor()

    # SQL query to select all data from the clients table
    query = 'SELECT * FROM clients'
    cursor.execute(query)

    # Fetch all data from the cursor
    rows = cursor.fetchall()

    # Convert rows into the desired dictionary format
    clients_dict = {}
    for row in rows:
        # Convert row to a dict
        row_dict = dict(row)
        id_number = row_dict['id_number']  # Now you can access by column name
        # Build a dictionary for the current row excluding id_number
        client_data = {column_name: row_dict[column_name] for column_name in row_dict.keys() if (column_name != 'id_number' and column_name != 'id' and column_name != 'name')}
        # Assign the client_data dictionary to the correct id_number in the main dictionary
        clients_dict[id_number] = client_data

    # Close the database connection
    cursor.close()
    conn.close()

    # At this point, clients_dict is the desired dictionary
    #print(clients_dict)
    return clients_dict


# Coverts the data from clients table to VectorDatabase. This function calls fetch_all_client_details_as_dict function
def clients_con2VectorDB():
    data = fetch_all_client_details_as_dict()
    # Create a DataFrame from the dictionary
    df = pd.DataFrame.from_dict(data, orient='index')
    #print()
    #print(df['dislikes'])
    # Text columns to process
    text_columns = ['liked_meals', 'liked_veg', 'liked_fruits',
       'liked_snacks', 'dislikes', 'health_condition']

    # Process text columns with TF-IDF
    # for column in text_columns:
    #     #df[column] = df[column].apply(correct_spelling)  # Correct spelling
    #     tfidf_vectorizer = TfidfVectorizer()
    #     tfidf_matrix = tfidf_vectorizer.fit_transform(df[column])
    #     tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), index=df.index, columns=tfidf_vectorizer.get_feature_names())
    #     df = df.drop(column, axis=1).join(tfidf_df, rsuffix=f'_{column}')
    for column in text_columns:
        #print(column)
        #print(df[column])
        #print()
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(df[column].fillna(''))  # Fill NaNs with empty strings
        # Use get_feature_names_out() for compatibility with newer sklearn versions
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), index=df.index,
                                columns=tfidf_vectorizer.get_feature_names_out())
        df = df.drop(column, axis=1).join(tfidf_df, rsuffix=f'_{column}')
    # Categorical columns to process
    # Mapping for 'gender'
    gender_mapping = {'Female': 0, 'Male': 1}
    df['gender'] = df['gender'].map(gender_mapping)
    # Mapping for 'active_in_sports'
    active_in_sports_mapping = {'Lightly (little or no exercise)': 0, 'Moderate (exercise 1–3 days/week)': 1, 'Highly (exercise 4+ days/week)': 2}
    df['active_in_sports'] = df['active_in_sports'].map(active_in_sports_mapping)
    # Numerical columns to scale
    numerical_columns = ['age', 'current_weight', 'goal_weight', 'height']
    scaler = StandardScaler()
    df[numerical_columns] = scaler.fit_transform(df[numerical_columns])

    # At this point, 'df' has all the features encoded as numbers and is ready for similarity computation
    # or other machine learning tasks. 'id_number' is the index of the DataFrame.

    # If you want to convert this DataFrame into a dictionary of vectors:
    vectors = df.to_dict(orient='index')
    #print(vectors)
    # To compute the cosine similarity between all clients (rows) in the DataFrame:
    cosine_sim_matrix = cosine_similarity(df.values)
    #print(cosine_sim_matrix)
    return df, vectors, cosine_sim_matrix  # return the clients' data as a VectorDB and as a dict of victors
    # and the cosine_sim_matrix of the clients


# Extract as dict with id_clients as keys the latest blood tests added by the id_clients
def fetch_latest_blood_tests_as_dict():
    # Connect to your database
    conn = sqlite3.connect('my_rules.db')  # Change to your database file
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # SQL query to select the latest blood test date for each client_id
    query = '''SELECT id_client, MAX(date_of_blood_test) as latest_date
               FROM clientsBloodTests
               GROUP BY id_client'''
    cursor.execute(query)

    # Fetch all data from the cursor and build the dictionary
    latest_dates = {row['id_client']: row['latest_date'] for row in cursor.fetchall()}

    # Close the database connection
    cursor.close()
    conn.close()

    return latest_dates


# Extract as dict with id_clients as keys and dicts as values about blood tests(with blood test name as key and the
# result of this blood test as value)
def fetch_all_client_bloodTest_as_dict():
    latest_dates = fetch_latest_blood_tests_as_dict()

    # Connect to your database
    conn = sqlite3.connect('my_rules.db')  # Change to your database file
    conn.row_factory = sqlite3.Row  # Set row factory to sqlite.Row
    cursor = conn.cursor()

    # SQL query to select all the latest blood tests with additional details
    query = '''SELECT bt.id_client, bt.blood_test_name, bt.test_result, bt.date_of_blood_test,
                              bt.gender, bt.age, bt.health_condition
                       FROM clientsBloodTests bt
                       WHERE bt.date_of_blood_test = (SELECT MAX(date_of_blood_test)
                                                      FROM clientsBloodTests
                                                      WHERE id_client = bt.id_client)'''
    cursor.execute(query)

    # Fetch all data from the cursor
    rows = cursor.fetchall()

    # Data structure to hold the latest blood tests for each client, including additional details
    blood_tests_dict = {}

    # Process the fetched rows
    for row in rows:
        # Now you can access columns by name
        id_client = row['id_client']
        blood_test_name = row['blood_test_name']
        test_result = row['test_result']
        gender = row['gender']
        age = row['age']
        health_condition = row['health_condition']

        # Initialize the client's dictionary if it doesn't exist
        if id_client not in blood_tests_dict:
            blood_tests_dict[id_client] = {'age': age, 'gender': gender, 'health_condition': health_condition}

        # Update the client's dictionary with test results
        blood_tests_dict[id_client][blood_test_name] = test_result

    # Close the database connection
    cursor.close()
    conn.close()

    # print(blood_tests_dict)
    return blood_tests_dict, latest_dates


# This function is not used!
# Coverts the data about blood tests results of clients to VectorDatabase.
# This function calls fetch_all_client_bloodTest_as_dict function
def bloodTestsClients_con2VectorDB():
    # Fetch all blood test data
    blood_tests_dict, _ = fetch_all_client_bloodTest_as_dict()

    # Create a DataFrame from the blood test dictionary
    df = pd.DataFrame.from_dict(blood_tests_dict, orient='index')

    # Handle NaN cases before normalizing - some client has a blood test and another don't

    # Excluded columns that should not undergo the NaN-filling process
    excluded_columns = ['health_condition', 'gender', 'age']

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        # Iterate over each column that is not in the excluded list
        for column in df.columns:
            if column not in excluded_columns:
                # Check if the current entry is NaN
                if pd.isna(row[column]):
                    # Extract the mark from the current column name if it is within parentheses
                    match = re.search(r'\((.*?)\)', column)
                    if match:
                        mark_to_query = match.group(1)
                    else:
                        mark_to_query = column  # Fallback to the original column name

                    # Get the normal range for the mark based on the extracted mark
                    normal_range = get_normal_range(mark_to_query, row.get('gender'))

                    # If a normal range is found, get a random value within this range and assign it to the NaN entry
                    if normal_range:
                        df.at[index, column] = get_random_value_from_range(normal_range)


    numerical_columns = df.columns.tolist().copy()
    #print('df_columns_copy', df_columns_copy)


    #print(df.columns)
    text_columns = ['health_condition']  # Adjusted to the blood test scenario
    # Process text columns with TF-IDF
    for column in text_columns:
        #if column not in ['age', 'gender', 'test_result']:
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(df[column].fillna(''))  # Fill NaNs with empty strings
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), index=df.index,
                                columns=tfidf_vectorizer.get_feature_names_out())
        df = df.drop(column, axis=1).join(tfidf_df, rsuffix=f'_{column}')

    # For blood tests, 'gender' might still be relevant, but 'active_in_sports' would likely not be included
    gender_mapping = {'Female': 0, 'Male': 1}
    if 'gender' in df.columns:
        df['gender'] = df['gender'].map(gender_mapping)

    # Include relevant numerical columns from the blood tests, adjusting as necessary

    numerical_columns.remove('health_condition')
    numerical_columns.remove('gender')
    #print(df_columns_copy)
    #numerical_columns = df_columns_copy

    #numerical_columns = ['age', 'current_weight', 'goal_weight', 'height']
    scaler = StandardScaler()
    df[numerical_columns] = scaler.fit_transform(df[numerical_columns])

    # if any(item in numerical_columns for item in df.columns):
    #     scaler = StandardScaler()
    #     df[numerical_columns] = scaler.fit_transform(df[numerical_columns])





    # Convert the DataFrame into a dictionary of vectors and compute the cosine similarity matrix
    vectors = df.to_dict(orient='index')
    cosine_sim_matrix = cosine_similarity(df.values)

    return df, vectors, cosine_sim_matrix


# Extract the normal range of a giving blood test based on the gender
def get_normal_range(mark, gender):
    # Extract the part of the mark that is within parentheses using regular expression
    match = re.search(r'\((.*?)\)', mark)
    if match:
        mark_to_query = match.group(1)  # This is the extracted part
    else:
        mark_to_query = mark  # Fallback to the original mark if no parentheses are found

    # Connect to the database
    conn = sqlite3.connect('my_rules.db')
    cursor = conn.cursor()

    # Execute query to get the normal_range for the specific mark
    cursor.execute("SELECT normal_range FROM normalBloodTests WHERE LOWER(mark) = LOWER(?)", (mark_to_query,))
    result = cursor.fetchone()

    # Close the database connection
    cursor.close()
    conn.close()

    if result:
        normal_range = result[0]
        # Parse the normal_range based on gender if applicable
        if ',' in normal_range and gender:
            normal_ranges = normal_range.split(',')
            if gender.lower() == 'female':
                normal_range = normal_ranges[0]
            elif gender.lower() == 'male' and len(normal_ranges) > 1:
                normal_range = normal_ranges[1]
        return normal_range
    else:
        return None


# This function is used when trying to convert the blood tests to VectorDatabase.
# The ides behind it is that if the nutritionist did not include some blood test that
# exists for other client it is reasonable to assume that for this giving client, the result of
# this blood test falls in the normal range, therefore a random value in this range is returned
# Handles NaNs in the blood tests
def get_random_value_from_range(normal_range):
    if not normal_range:
        return None

    lower = normal_range.split('-')[0]
    upper = normal_range.split('-')[1]
    if lower == '*':
        lower = float(upper) - 100
    elif upper =='*':
        upper = float(lower) + 150
    lower = float(lower)
    upper = float(upper)

    return random.uniform(lower, upper)


# Returns a list of tuples of rating if exists for previous ranked meals by the giving id_client on the giving meal type
# Assuming that tuple(0) is the meal description and tuple(1) is the satisfaction rate
def get_previous_ranked_meals(id_client, meal_type):
    conn = sqlite3.connect('my_rules.db')  # Change to your database file
    cursor = conn.cursor()

    # This dictionary maps meal types to their respective rating column names
    meal_rating_columns = {
        'breakfast': 'breakfast_rate',
        'snack1': 'snack1_rate',
        'lunch': 'lunch_rate',
        'snack2': 'snack2_rate',
        'dinner': 'dinner_rate',
    }

    # Check if the provided meal_type is valid
    if meal_type not in meal_rating_columns:
        raise ValueError("Invalid meal_type. Choose from 'breakfast', 'snack1', 'lunch', 'snack2', or 'dinner'.")

    # Get the rating column name based on meal_type
    rating_column = meal_rating_columns[meal_type]

    # Construct the SQL query, exclude the most recent date
    query = f"""SELECT {meal_type}, {rating_column}
            FROM clients_meals_with_rates
            WHERE id_client = ? AND {rating_column} IS NOT NULL
        
        """

    # Execute the query
    cursor.execute(query, (id_client, ))

    # Fetch all results and convert them into tuples
    rows = cursor.fetchall()

    # Check if the fetch retrieved any rows
    if rows:
        # Convert them into tuples
        ranked_meals = [tuple(row) for row in rows]
        return ranked_meals
    else:
        return []


# Gets the ids of other clients that are found similar (similarity_score>0.9) for the giving id_client
# This functions calls the clients_con2VectorDB function
def get_similar_clients(id_client):
    # returns a list of ids of similar personal data, if above 0.9 in similarity_matrix then consider similar
    # Call the function to get the DataFrame and cosine similarity matrix
    df, vectors, cosine_sim_matrix = clients_con2VectorDB()

    # Find the index of the client in the DataFrame
    try:
        client_index = df.index.get_loc(id_client)
    except KeyError:
        raise ValueError(f"Client ID {id_client} not found in the DataFrame.")

    # Get the similarity scores for the client
    similarity_scores = cosine_sim_matrix[client_index]

    # Find indices of clients with similarity score of 0.9 and above
    similar_indices = [i for i in range(len(similarity_scores)) if similarity_scores[i] >= 0.9 and i != client_index]

    # Get the client IDs for the similar clients
    similar_client_ids = df.iloc[similar_indices].index.tolist()

    return similar_client_ids


# for all blood test restrictions/rules/reasons, if we find a rule that is related to a result that is not in the
# normal range, we want to make it global to all clients with this type of result.
# For each blood test result assume 3 types: under, in and above normal range.
# returns a dict with rule(blood test names, 'other') as keys and a dict as a value, that will contain
# two keys: + (above) and - (under) and value of list of restrictions.
# run over all rows in the rules table, for each row is the reason is BT then
# check the type of result for this client.
# if in range - pass
# if under/ above save in the dict
def get_TB_rules_not_normal_range():
    # Fetch all client details
    blood_tests_dict, latest_dates = fetch_all_client_bloodTest_as_dict()

    # Connect to your database
    conn = sqlite3.connect('my_rules.db')  # Change to your database file
    conn.row_factory = sqlite3.Row  # Set the row factory
    cursor = conn.cursor()

    # Fetch all rules from the database
    cursor.execute("SELECT id_rule, rule, restrictions, id_client FROM rules")
    rules = cursor.fetchall()

    # Prepare a list to store clients with test results not in the normal range
    clients_not_normal = {}

    for rule_row in rules:
        rule = rule_row['rule'].lower()
        id_client = rule_row['id_client']
        restrictions = rule_row['restrictions']
        if rule not in clients_not_normal.keys():
            clients_not_normal[rule] = {}
        if 'under' not in clients_not_normal[rule].keys():
            clients_not_normal[rule]['under'] = []
        if 'in' not in clients_not_normal[rule].keys():
            clients_not_normal[rule]['in'] = []
        if 'above' not in clients_not_normal[rule].keys():
            clients_not_normal[rule]['above'] = []

        # If rule is not 'other', proceed to check the client's blood test result
        if rule != 'other' and id_client in blood_tests_dict:
            # Get the blood test result for the client that matches the rule
            client_tests = blood_tests_dict[id_client]
            for test_name, test_result in client_tests.items():
                if rule.lower() in test_name.lower():
                    # Assuming that the test_result is a numerical value and normal range is a tuple of (low, high)
                    normal_range = get_normal_range(rule, client_tests['gender'])
                    in_range_flag, type_f = is_in_normal_range(test_result, normal_range)
                    # If the test result is not in the normal range, add to the list
                    if normal_range and not in_range_flag: #and type_f != 'in':
                        clients_not_normal[rule][type_f].append(restrictions)

    # Close the database connection
    cursor.close()
    conn.close()

    return clients_not_normal


# returns if test result is within the normal range. Assume normal_range in string
def is_in_normal_range(test_result, normal_range):
    normal_range_split = normal_range.split('-')
    if normal_range_split[0] == '*':
        if test_result > normal_range_split[1]:
            return False, 'above'
        else:
            return True, 'in'
    elif normal_range_split[1] == '*':
        if test_result < normal_range_split[0]:
            return False, 'under'
        else:
            return True, 'in'
    else:
        low, high = map(float, normal_range_split)
        if low <= float(test_result) <= high:
            return True, 'in'
        else:
            return False, 'above' if float(test_result) > high else 'under'


# runs over all data regarding this id_client and extract the relevant data from the rules table, then run over
# his blood test results from the BT table and check if they fall under, in or above the normal range. if in - pass,
# otherwise save the restriction of this type.
def get_rules_by_nutri(id_client):
    # Get the global rules by blood test results that are not within the normal range
    global_rules_by_BT = get_TB_rules_not_normal_range()

    # Fetch the specific client's blood test results
    blood_tests_dict, latest_dates = fetch_all_client_bloodTest_as_dict()

    # Get the blood test results for the specified client
    client_tests = blood_tests_dict.get(id_client, {})

    # Prepare a dict to store restrictions based on the blood test result
    # If the blood test is either 'under' or 'above' normal, add its restrictions to the list
    # Also prepare a list for 'other' restrictions
    dict_rest = {}
    other_rules = []

    # Connect to the database to get 'other' restrictions
    conn = sqlite3.connect('my_rules.db')
    cursor = conn.cursor()

    # Fetch 'other' restrictions for the client
    cursor.execute("SELECT restrictions FROM rules WHERE rule = 'other' AND id_client = ?", (id_client,))
    other_restrictions = cursor.fetchall()

    # Add 'other' restrictions to the restriction_dict
    for restriction in other_restrictions:
        other_rules.append(restriction[0])

    # Close the database connection
    cursor.close()
    conn.close()

    # Convert all elements to lowercase (or uppercase) and then to a set. REMOVE DUPLICATIONS
    unique_other_strings = set(s.lower() for s in other_rules)
    other_rules = list(unique_other_strings)


    for test_name, test_result in client_tests.items():
        if test_name not in ['age', 'gender', 'health_condition']:
            match = re.search(r'\((.*?)\)', test_name)
            if match:
                test_name = match.group(1)
            if test_name != 'other':
                dict_rest[test_name] = {'above': [], 'under': [], 'other': []}

                # Iterate over the client's blood tests

                # Compare with the global rules
                for rule, threshold_dict in global_rules_by_BT.items():
                    if rule.lower() in test_name.lower() and rule.lower!= 'other':
                        # Check if the test result is within the normal range
                        normal_range = get_normal_range(test_name, client_tests['gender'])
                        if normal_range:
                            in_range, range_status = is_in_normal_range(test_result, normal_range)
                            # If not 'in' range, then add the restriction to the list
                            if not in_range and range_status in ['above', 'under']:

                                dict_rest[test_name][range_status].extend(threshold_dict[range_status])


    for test_name, value_dict in dict_rest.items():
        for case in value_dict:
            # Convert all elements to lowercase (or uppercase) and then to a set. REMOVE DUPLICATIONS
            unique = set(s.lower() for s in dict_rest[test_name][case])
            dict_rest[test_name][case] = list(unique)

    filtered_data = {}
    for key, value in dict_rest.items():
        if isinstance(value, dict):
            non_empty_values = {}
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, list):
                    non_empty_values[sub_key] = [v for v in sub_value if v.strip()]
            if any(non_empty_values.values()):
                filtered_data[key] = non_empty_values

    return filtered_data, other_rules


# Function to display progress level based on the progress_level
def display_progress(progress_level):
    progress_level = max(0.0, min(10.0, progress_level))  # Bounds between 0 and 10

    # Display the progress score as a metric
    # Use round() for displaying a rounded value in the metric, but keep the original float for the progress calculation
    st.metric(label="Client Progress Score By Previous Feedbacks", value=f"{round(progress_level)} / 10")

    # Convert the progress level to a percentage for the progress bar
    # Ensure it's an integer between 0 and 100
    progress_percentage = int(progress_level * 10)
    st.progress(progress_percentage)


# Returns all feedbacks left by this id_client from the clients_feedback_for_nutri
def get_feedbacks(id_client):
    # Connect to your database
    conn = sqlite3.connect('my_rules.db')  # Change to your database file
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # SQL query to select the 3 latest feedbacks for the given client
    query = '''SELECT feedback FROM clients_feedback_for_nutri
                   WHERE id_client = ?
                   ORDER BY date_of_feedback DESC, id DESC
                   LIMIT 3'''

    # Execute the query with the provided id_client
    cursor.execute(query, (id_client,))

    # Fetch all data from the cursor
    feedbacks = [row['feedback'] for row in cursor.fetchall()]

    # Close the database connection
    cursor.close()
    conn.close()

    return feedbacks


# Returns True if the comment includes a word that has infinite effect regarding time. for example,
# if the comment include the word always/never or something similar then the returned value is True
def classify_comment(comment):
    # Simple classification based on keywords indicating permanency.
    permanent_keywords = ["Always",
                          "Forever",
                          "Perpetually",
                          "Continually",
                          "Constantly",
                          "Invariably",
                          "Unceasingly",
                          "Endlessly",
                          "Eternally",
                          "Everlastingly",
                          "Ceaselessly",
                          "Unendingly",
                          "Perennially",
                          "Incessantly",
                          "Without end",
                          "Infinitely",
                          "never",
                          "At no time",
                          "Under no circumstances",
                          "Not ever",
                          "Not at any time",
                          "Not once",
                          "In no way",
                          "Nowhere",
                          "Not in any degree",
                          "Absolutely not",
                          "By no means",
                          "Zero chance",
                          "Not in the least",
                          "Not under any condition",
                          "No way",
                          "Not for a moment",
                          "Not at all",
                          "At all",
                          ]
    lowercase_comment = comment.lower()
    comment_classification = 'General' if any(keyword.lower() in lowercase_comment for keyword in permanent_keywords) else 'Specific'
    #print(comment_classification == 'General')
    return comment_classification == 'General'


#########################################################  From here on, these functions uses API calls.


# Add client feedback to the clients_feedback_for_nutri
def add_feedback(client_id, feed_text):
    model = genai.GenerativeModel('gemini-pro')
    genai.configure(api_key=os.getenv("MY_API_KEY"))

    cont = 'is this text : ' + feed_text + ' has any meaning? if Yes the response should be "True", ' \
                                           'otherwise "False"'

    response = model.generate_content(cont)
    response_text = response.text
    if response_text == "False":
        print(f"This feedback: {feed_text} has no meaning, Therefor, ignored.")
    else:
        conn = sqlite3.connect('my_rules.db')
        c = conn.cursor()

        # Get the current date in the format that your database expects (usually YYYY-MM-DD)
        current_date = datetime.now().strftime('%Y-%m-%d')

        # SQL statement to insert a new row into the table
        c.execute('''
                INSERT INTO clients_feedback_for_nutri (id_client, date_of_feedback, feedback)
                VALUES (?, ?, ?)
            ''', (client_id, current_date, feed_text))

        # Commit the changes to the database
        conn.commit()
        #print("Feedback added successfully.")
        conn.close()



# Returns a number that indicates his progress in scale from 0-10 based on his feedbacks if exists,
# otherwise returns a text to display that asks the client to add a feedback.
def get_feedback_score(id_client):
    """
    At the command line, only need to run once to install the package via pip:

    $ pip install google-generativeai
    """

    genai.configure(api_key=os.getenv("MY_API_KEY"))
    # Set up the model
    generation_config = {
        "temperature": 0.2,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
    }

    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_ONLY_HIGH"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_ONLY_HIGH"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_ONLY_HIGH"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_ONLY_HIGH"
        },
    ]

    new_model2 = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)

    convo = new_model2.start_chat(history=[
    ])

    feedbacks_list = get_feedbacks(id_client)
    feedbacks_relevant = []
    avg_score_last_three_feeds = 0.0
    cnt_relevant_feeds = 0
    if feedbacks_list:
        feedback_list_as_string = ''
        for feed in feedbacks_list:
            content_feed = 'based on this feedbacks text left by a client: ' + feed + ' , generate a number between 0 - 10 ' \
                                            'that best represents the positive level meaning. 10 is highest level and 0' \
                                            ' is the lowest. if this text have a positive meaning with high probability then it indicates ' \
                                            'high score. if the text has a neutral meaning then it indicates score' \
                                            'around 5, if the text has a negative meaning then it indicates low score.'
            relevant_response_flag = False
            #while not relevant_response_flag:
                #convo.send_message(content_feed)
                #if convo.last:
                    #relevant_response_flag = True
            convo.send_message(content_feed)
            try:
                int(convo.last.text)  # Attempt to convert text to an integer
                add_flag = True
            except ValueError:  # If an error is raised, it means text cannot be converted to an integer
                add_flag = False

            if add_flag:
                cnt_relevant_feeds += 1
                avg_score_last_three_feeds += int(convo.last.text)
                feedback_list_as_string += feed + ', '
                feedbacks_relevant.append(feed)

        if cnt_relevant_feeds > 0:
            avg_score_last_three_feeds = avg_score_last_three_feeds/cnt_relevant_feeds
            last_comma_index = feedback_list_as_string.rfind(',')
            feedback_list_as_string = feedback_list_as_string[:last_comma_index] + feedback_list_as_string[last_comma_index + 1:]
            return round(avg_score_last_three_feeds, 1), feedbacks_relevant  # feedback_list_as_string.split(",")

        else:
            return 'There is no feedbacks left by this client.', []
    else:
        return 'There is no feedbacks left by this client.', []


# Based on progress_score generate encouragement comment for the client
def get_encouragement_comment(progress_score):
    """
    At the command line, only need to run once to install the package via pip:

    $ pip install google-generativeai
    """
    #genai.configure(api_key="YOUR_API_KEY")
    genai.configure(api_key=os.getenv("MY_API_KEY"))
    # Set up the model
    generation_config = {
        "temperature": 0.2,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
    }

    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_ONLY_HIGH"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_ONLY_HIGH"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_ONLY_HIGH"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_ONLY_HIGH"
        },
    ]

    new_model2 = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)

    convo = new_model2.start_chat(history=[
    ])
    # content = feedback_list_as_string + 'based on these feedbacks generate a number between 0 - 10 ' \
    #                                     'that best represents the satisfaction= level. 10 is highly satisfied and 0' \
    #                                     ' is not satisfied at all. the satisfaction is about generated meal plans'
    if type(progress_score) == int:
        content = str(progress_score) + ' is a number between 0 - 10 ' \
                                        'that best represents the progress level. 10 is highest level and 0' \
                                        ' is the lowest. the progress is regarding the progress with the generated ' \
                                        'meal plans. generate a message of encouragement based on this number ' \
                                    'with no numbers and at most 2 sentences.' \
                                        'examples: for high number: 1. you are in the right track. keep going! ' \
                                        '2. Youre doing awesome! 3. Keep on keeping on!' \
                                        'for a lower number: 1. Your speed doesnt matter. Forward is forward. ' \
                                        '2. Every accomplishment starts with the decision to try. ' \
                                        '3. Be positive, patient, and persistent.'
    else:
        content = 'generate a message of 2 sentences at most, of encouragement for someone who is still in the start of his journey on ' \
                  'reaching his/her weight or health goal. also recommend him/her to leave some feedbacks. make it so that it ' \
                  'refers to males and females and only relevant to the one who sees it. do not include meal plan in the text. ' \
                  'examples: 1. A journey starts with one step. 2. Every moment is a fresh beginning. ' \
                  '3. It always seems impossible until its done. 4. Every accomplishment starts with the decision to try.'

    relevant_response_flag = False
    # while not relevant_response_flag:
    #     convo.send_message(content)
    #     if convo.last:
    #         relevant_response_flag = True
    convo.send_message(content)
    return convo.last.text


# Returns a dict of all meal types, first the prompt is constructed and later on passed to the model and lastly
# divided based on meal types. The prompt is based on:
# 1. clients data and nutritious recommendations(how much protein, fat and carbs )
# 2. rules added by nutritionist for this specific client
# 3. rules added by nutritionist for a blood test that is not in the normal range and are relevant to this
#    client based on his test results. for example: if the nutritionist added a rule for some client
#    that has a high Glucose to have fewer carbohydrates in their meals, and the
#    giving client also has a high Glucose then this rule should also be applied to him.
# 4. Previous meals of the same meal type(like: breakfast) with their satisfaction rates if exists.
# 5. Previous meals of similar other clients if found of the same meal type with their satisfaction rates if exists.
# Note: two clients are considered similar if the similarity_score in the similarity matrix is higher than 0.9.
def get_new_meal_plan(id_client, daily_cal):

    prompt = f"for one day with daily calories {daily_cal}, generate in a healthy, balanced and sensible way," \
             f" a meal plan of these five meals: 'Breakfast', " \
             f"'Mid-Morning Snack', 'Lunch', 'Afternoon Snack', 'Dinner' make it suitable for middle eastern cuisine.\n" \
             f" The response should include " \
             f"for each meal type:\n" \
             f"1. brief name with description including ingredients and their amount/quantities and their calories\n" \
             f"2. Feedback that is explainable for this client, the client should understand why a specific meal is recommended\n\n"


    prompt += f"the generated meal plan should be logical in term of combination of the ingredients.\n" \
              f" Consider combining meals or ingredients that this client like to eat, as long as that " \
              f"the combination is logical.\n\n"

    prompt += f"For each meal type, make sure that the sum of all ingredients of the meal is close to the total " \
              f"calories of the meal \n\n"

    prompt += f"The data of this client are: \n"

    details = fetch_client_details(id_client)
    for key, value in details.items():
        if key not in ['name', 'id', 'current_weight', 'height', 'goal_weight']:
            if value:
                prompt += ''+str(key)+': '+str(value) + ',\n'

    prompt += f"\n\n"

    rules, other_rules = get_rules_by_nutri(id_client)

    if rules:

        prompt += f"\nthese restrictions are very important to take into account when ' \
                  'generating this meal because they are related to the blood tests of this client. ' \
                  'inside the () are the reasons of the relevant restrictions (for each restriction that is not ' \
                  'understandable Ignore):\n"

        i = 1
        for test_name, test_d in rules.items():
            for res_type in test_d:
                restrictions = rules[test_name][res_type]
                if restrictions:
                    prompt += f"restrictions {i}: "
                    for j in range(len(restrictions)):

                        restric = f"{restrictions[j]}"

                        if res_type in ['under', 'in', 'above']:
                            restric += f"(result of blood test {test_name} is {res_type} the normal range),\n"
                            prompt += restric  # + '\n '
                            i += 1

    i = 1
    if other_rules:
        prompt += f"these are general restrictions that are very important to take to account:\n "
        for j in range(len(other_rules)):
            restric = other_rules[j]

            prompt += f"restrictions {i}: {restric},\n "

            i += 1

    prompt += f"\n\n"

    meal_type_list = ['breakfast', 'snack1', 'lunch', 'snack2', 'dinner']
    k = 1
    prev_meal_rates_prompt = f""
    for meal_type in meal_type_list:
        prev_meals = get_previous_ranked_meals(id_client, meal_type)  # list of tuples
        if prev_meals:
            for meal_type_c, value in prev_meals:
                prev_meal_rates_prompt += f"option {k}: {meal_type_c} with rate of satisfaction: {value}, \n\n"
                k += 1


    if prev_meal_rates_prompt:
        prompt += f"\nThese are previous meals and their rate of satisfaction of this client:\n {prev_meal_rates_prompt}"
        prompt += f"\n\n"

    similar_clients = get_similar_clients(id_client)
    similar_client_meal_prompt = f""
    if similar_clients:
        k = 1
        for id_c in similar_clients:
            for meal_type in meal_type_list:
                prev_meals_similar_client = get_previous_ranked_meals(id_c, meal_type)
                if prev_meals_similar_client:
                    for meal_type_c, value in prev_meals_similar_client:#prev_meals_similar_client.items():
                        if value.lower() in ['satisfied', 'highly satisfied']:
                            similar_client_meal_prompt += f"recommendation {k}: {meal_type_c} with rate of satisfaction: {value},\n\n"
                            k += 1
    if similar_client_meal_prompt:
        prompt += f"\nThese are previous meals and their rate of satisfaction of other clients that are" \
                        f"considered very similar to this client, that you can refer to: {similar_client_meal_prompt}"





    model = genai.GenerativeModel('gemini-pro')
    genai.configure(api_key=os.getenv("MY_API_KEY"))
    relevant_response_flag = False
    while not relevant_response_flag:
        response = model.generate_content(prompt)
        if response:
            relevant_response_flag = True

    print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    print(response.text)
    print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')

    response_text = response.text
    meals_title = ['Breakfast', 'Mid-Morning Snack', 'Lunch', 'Afternoon Snack', 'Dinner']
    meals_info = {}  # dict of lists [meal_type_index, meal_calories, meal_description, meal_feedback]
    for meal_t in meals_title:
        meals_info[meal_t] = []

    meal_index = 0
    for meal_t in meals_title:
        meals_info[meal_t].append(meal_index)
        content1 = f"extract from {response_text} the calories regarding the {meal_t} 'meal.\n " \
                   f"the response should be only the number of calories of this meal"
        meal_cal = model.generate_content(content1)
        meal_cal_text = meal_cal.text
        meals_info[meal_t].append(meal_cal_text)

        content2 = f"extract from {response_text} the meal type with the calories and the description of the {meal_t} 'meal without the feedback.\n " \
                  f"the response should be the meal type, brief name with description including ingredients and their amount/quantities and their calories, " \
                  f"in this structure:\n" \
                  f"**meal type: meal title (Approximately meal's calories)**:\n  " \
                  f"meal description including ingredients and their amount/quantities and their calories, for this use simple font with no bullets\n"
        meal_info = model.generate_content(content2)
        meal_info_text = meal_info.text
        meals_info[meal_t].append(meal_info_text)

        content3 = f"extract from {response_text} the info regarding the feedback regarding the {meal_t} 'meal.\n " \
                   f"the response should be only the feedback of this meal, for this use simple font with no bullets"
        meal_feed = model.generate_content(content3)
        meal_feed_text = meal_feed.text
        meals_info[meal_t].append(meal_feed_text)

        meal_index += 1


    # print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    # print(meals_info)
    # print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')

    return response_text, meals_info


# Returns a new meal with explanation with the same calories and type as the giving one, based on the comment
# left by the nutritionist on this giving meal. Prompt is first constructed and then passed to the model
# and lastly extracted and returns.
def change_meal_of_meal_plan(id_client, current_meal_plan='', nutri_comment_temp='', meal_to_change='', meal_type=''):
    if nutri_comment_temp:
        prompt = f"for the giving meal plan of a whole day {current_meal_plan}\n\nThe nutritionist left" \
                 f"this comment: {nutri_comment_temp} regarding this meal:\n{meal_to_change}\n\n" \
                 f"Generate a new meal of the same type with the same calories based on this comment such that " \
                 f"the updated meal plan with " \
                 f"the new meal (that replaces the one the nutritionist left a comment on) is considered" \
                 f"healthy, balanced and sensible.\n\n The response should include for this meal:\n" \
                 f"1. Brief name with description including ingredients and their amount/quantities and their calories\n" \
                 f"2. Feedback that is explainable for this client, the client should understand why a specific meal is recommended." \
                 f"do not include that the nutritionist made a change or that there were chane/swap. it is " \
                 f"not relevant to the client to know.\n\n"\

        prompt += f"this comment left by the nutritionist should be the main reason behind the generation. " \
                  f"It the highest priority possible when you generate the meal\n\n"
    else:
        prompt = f"for the giving meal plan of a whole day {current_meal_plan}\n\nThe nutritionist wants" \
                 f"to regenerate a new {meal_type} meal instead of the current one:\n{meal_to_change}\n\n" \
                 f"Generate a new meal of the same type, such that the updated meal plan with " \
                 f"the new meal (that replaces the one the nutritionist left a comment on) is considered" \
                 f"healthy, balanced and sensible.\n\n The response is the generated meal in " \
                 f"the same structure of the other meals, That is:\n" \
                 f"1. Brief name with description including ingredients and their amount/quantities and their calories.\n" \
                 f"2. Feedback that is explainable for this client, the client should understand why a specific meal is recommended\n\n" \

    prompt += f"For the new generated meal, make sure that the sum of all ingredients of the meal is close to the total " \
              f"calories of the meal \n\n"

    prompt += f"The data of this client are: \n"

    details = fetch_client_details(id_client)
    for key, value in details.items():
        if key not in ['name', 'id', 'current_weight', 'height', 'goal_weight']:
            if value:
                prompt += f" {key}: {value} ,\n"

    prompt += f"\n\n"

    rules, other_rules = get_rules_by_nutri(id_client)

    if rules:

        prompt += f"\nthese restrictions are very important to take into account when ' \
                  'generating this meal because they are related to the blood tests of this client. ' \
                  'inside the () are the reasons of the relevant restrictions (for each restriction that is not ' \
                  'understandable Ignore):\n"

        i = 1
        for test_name, test_d in rules.items():
            for res_type in test_d:
                restrictions = rules[test_name][res_type]
                if restrictions:
                    prompt += f"restrictions {i}: "
                    for j in range(len(restrictions)):

                        restric = f"{restrictions[j]}"

                        if res_type in ['under', 'in', 'above']:
                            restric += f"(result of blood test {test_name} is {res_type} the normal range),\n"
                            prompt += restric  #+ '\n '
                            i += 1

    i = 1
    if other_rules:
        prompt += f"these are general restrictions that are very important to take to account:\n "
        for j in range(len(other_rules)):
            restric = other_rules[j]

            prompt += f"restrictions {i}: {restric},\n "

            i += 1

    prompt += f"\n\n"

    meal_type_list = ['breakfast', 'snack1', 'lunch', 'snack2', 'dinner']
    for meal_type in meal_type_list:
        prev_meals = get_previous_ranked_meals(id_client, meal_type)  # list of tuples

        if prev_meals:
            #print('prev_meals: ', prev_meals)
            prompt += f"\nThese are previous meals and their rate of satisfaction of this client:\n "
            k = 1
            for meal_type_c, value in prev_meals:
                prompt += f"option {k}: {meal_type_c} with rate of satisfaction: {value}, \n"
                k += 1

            prompt += f"\n\n"

    model = genai.GenerativeModel('gemini-pro')
    genai.configure(api_key=os.getenv("MY_API_KEY"))
    #response = model.generate_content(prompt)
    relevant_response_flag = False
    while not relevant_response_flag:
        response = model.generate_content(prompt)
        if response:
            relevant_response_flag = True

    print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    print(f"meal to change:\n {meal_to_change}\nnew meal info:\n")
    print(response.text)
    print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')

    response_text = response.text
    meals_title = ['Breakfast', 'Mid-Morning Snack', 'Lunch', 'Afternoon Snack', 'Dinner']
    meal_index = -1
    for i in range(0, 5):
        if meal_type == meals_title[i]:
            meal_index = i
    new_meal_info = []
    new_meal_info.append(meal_index)

    content1 = f"extract from {response_text} the calories regarding the {meal_type} 'meal.\n " \
               f"the response should be only the number of calories of this meal."
    meal_cal = model.generate_content(content1)
    meal_cal_text = meal_cal.text
    new_meal_info.append(meal_cal_text)

    content2 = f"extract from {response_text} the meal type with the calories and the description of the {meal_type} 'meal without the feedback.\n " \
               f"the response should be the meal type, brief name with description including ingredients and their amount/quantities and their calories, " \
               f"in this structure:\n" \
               f"**meal type: meal title (Approximately meal's calories)**:\n  " \
               f"meal description including ingredients and their amount/quantities and their calories, for this use simple font with no bullets\n"

    meal_info = model.generate_content(content2)
    meal_info_text = meal_info.text
    new_meal_info.append(meal_info_text)

    content3 = f"extract from {response_text} the info regarding the *feedback* part regarding the {meal_type} 'meal.\n " \
              f"the response should be only the feedback of this meal, for this use simple font with no bullets."
    meal_feed = model.generate_content(content3)
    meal_feed_text = meal_feed.text
    new_meal_info.append(meal_feed_text)

    #print(new_meal_info)
    return new_meal_info