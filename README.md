YouTube Data Harvesting and Warehousing

Overview
This project aims to streamline the retrieval, storage, and presentation of YouTube channel data. It utilizes a combination of Python, MongoDB, MySQL, and Streamlit to accomplish this task. The application fetches data from the YouTube Data API, stores it initially in MongoDB, migrates and transforms it into a structured MySQL database, and finally presents it through a user-friendly Streamlit interface.

Key Features
Data Retrieval: Utilizes the YouTube Data API to fetch channel data.
Storage: Stores the retrieved data in MongoDB for initial storage.
Migration and Transformation: Converts and organizes the data into a SQL database for structured storage and enhanced querying capabilities.
Data Presentation: Displays the queried data through a Streamlit application, providing users with a seamless interface for accessing and analyzing YouTube channel insights.

Technologies Used
Python
MongoDB
MySQL
Streamlit
Google YouTube Data API

How to Run the Application
1. Clone this repository to your local machine.
2. Install the required dependencies using pip install -r requirements.txt.
3. Obtain API keys for YouTube Data API and replace api_key variable in the code with your own API key.
4. Make sure you have MongoDB installed and running locally or provide the appropriate MongoDB URI in the code.
5. Make sure you have MySQL installed and running locally or provide the appropriate MySQL connection details in the code.
6. Run the Streamlit application using streamlit run app.py.
7. You should now be able to access the application via your web browser.


Future Improvements
=> Implement user authentication and authorization for secure access to the application.
=> Enhance data visualization capabilities with more interactive charts and graphs.
=> Implement scheduled data updates to keep the database current with the latest YouTube channel data.

Contributors
Anbarasan

License
This project is licensed under the MIT License.
