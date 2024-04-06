 # NutriAI Planner

NutriAI Planner is a sophisticated meal planning tool designed to assist nutritionists in creating personalized meal plans. Leveraging the power of artificial intelligence, NutriAI Planner adapts to individual client health data, dietary preferences, nutritionist feedbacks/comments, and blood tests to deliver a tailored meal plans that support nutritional goals and wellness.

## Features

	•	Personalized Meal Planning: Utilizes client health data and dietary preferences to generate meal suggestions.
	•	Nutritionist-AI Collaboration: Integrates nutritionist expertise with AI recommendations for meal planning.
	•	Client Feedback Loop: Incorporates client meal ratings to refine and adapt meal suggestions.
	•	Health Data Integration: Takes into account blood tests and health conditions in meal customization.
	•	User-Friendly Interface: Provides an intuitive web interface for easy interaction with the system.

## Prerequisites

Before you begin, ensure you have the following installed:
- [Anaconda](https://www.anaconda.com/products/distribution) (for managing virtual environments)
- [Streamlit](https://streamlit.io/) (for running the web application)

## Installation

1. Clone the repository to your local machine:
    bash
    git clone https://github.com/KareenG/NutriAIPlanner.git
    cd NutriAIPlanner
    or download as a ZIP file then extract the repository locally(I reccomend this way).


2. Create and activate the virtual environment using the provided environment.yml file:
    Once openning the repository locally in pycharm, go to settings and make sure that the Python Interpreter is set to <No interpreter>, only then a comment will be presented in the upper part of the .py files, the left one lets to add interperter using the yml file in this directory. By clicking on this the envirnoment will be set.
   ![image](https://github.com/KareenG/NutriAI/assets/66648432/dfe85119-ad4a-41be-a6d7-7830f1113f3c)

    

## Configuration

To interact with the Google Generative AI, you need to obtain an API key:

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey) to generate your Google Generative API key.

2. Once you have your API key, locate the .env file in the repository. It contains a placeholder for the API key:

    plaintext
    MY_API_KEY = ""
    

3. Replace the empty quotes with your API key, ensuring to keep it within the quotes:

    plaintext
    MY_API_KEY = "your-google-generative-api-key-here"
    

4. Save the .env file with your API key included. This file will be used by the application to authenticate API requests.

5. Run the database_manager.py script to set up the database:

    bash
    python database_manager.py
    

With the environment set, the API key configured, and the database initialized, you're all set to run the application.

## Running the Application

After completing the installation and configuration steps, launch the NutriAA Planner with the following command:

```bash
streamlit run Home.py

Open your web browser and navigate to the local server address provided by Streamlit (typically http://localhost:8501) to use the application.
