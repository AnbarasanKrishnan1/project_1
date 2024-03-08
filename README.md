# YouTube Data Harvesting and Warehousing

## Overview
This project aims to streamline the retrieval, storage, and presentation of YouTube channel data. It utilizes a combination of Python, MongoDB, MySQL, and Streamlit to accomplish this task. The application fetches data from the YouTube Data API, stores it initially in MongoDB, migrates and transforms it into a structured MySQL database, and finally presents it through a user-friendly Streamlit interface.

##Goal of YDH&W
 YouTube Data Harvesting and Warehousingserves several purposes
- Data Retrieval from YouTube
- Data Storage
- Data Transformation
- User Interface
- Analysis and Reporting

Overall, the YouTube Data Harvesting facilitates the seamless extraction, storage, transformation, and analysis of YouTube data, empowering users to derive valuable insights for various purposes, such as marketing, research, or content creation strategies.

## Technologies Used
- Python
- MongoDB
- MySQL
- Streamlit
- Google YouTube Data API

## Key Features
- Data Retrieval: Utilizes the YouTube Data API to fetch channel data.
- Storage: Stores the retrieved data in MongoDB for initial storage.
- Migration and Transformation: Converts and organizes the data into a SQL database for structured storage and enhanced querying capabilities.
- Data Presentation: Displays the queried data through a Streamlit application, providing users with a seamless interface for accessing and analyzing YouTube channel insights.


## How to Run the Application
1. Clone this repository to your local machine.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Obtain API keys for YouTube Data API and replace `api_key` variable in the code with your own API key.
4. Make sure you have MongoDB installed and running locally or provide the appropriate MongoDB URI in the code.
5. Make sure you have MySQL installed and running locally or provide the appropriate MySQL connection details in the code.
6. Run the Streamlit application using `streamlit run app.py`.
7. You should now be able to access the application via your web browser.

## work Flow Diagram

<p> """ A[Start] --> B{Run Script (streamlit run foldername.py)}<br>
B --> C{Streamlit App Opens}<br>
C --> D{Extract & Transform (Optional)}<br>
    [Yes (Transform Required)] --> D1{Perform Transformations}<br>
    D1 --> E{Extracted Data}<br>
C --> E{Extracted Data (No Transformation)}<br>
E --> F{Upload Channel ID}<br>
    [Valid Channel ID?] --> F1{Invalid ID: Error Message}<br>
    F --> G{Extract Data}<br>
        [API Rate Limit?] --> G1{Wait for Reset or Retry Later}<br>
        G --> H{Store to MongoDB (Optional)}<br>
            [MongoDB Connection Successful?] --> H1{Connection Error: Retry or Fix Configuration}<br>
            H --> I{View}<br>
            H --> N{Skip MongoDB Upload}<br>
        G --> I{View} (Data not stored in MongoDB)<br>
I[Select Channel (Dropdown Menu)] --> J{Submit}<br>
J --> K{Formulate Question based on User Input}<br>
K --> L{Retrieve Answer from Processed Data}<br>
    [Answer Found?] --> L1{No Answer Found: Display Message}<br>
    L --> M{Display Answer}<br>
M --> A (Loop back to Start)"""</p>

## Screenshots
![image](https://github.com/AnbarasanKrishnan1/project_1/assets/142040700/fd18529a-a9f0-4b89-b6d3-8616419cf245)

## Future Improvements
- Implement user authentication and authorization for secure access to the application.
- Enhance data visualization capabilities with more interactive charts and graphs.
- Implement scheduled data updates to keep the database current with the latest YouTube channel data.

## Contributors
[Anbarasan](https://www.linkedin.com/in/anbarasan-krishnan-data-scientist/)

## License
This project is licensed under the MIT License.
