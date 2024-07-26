# JasleenSandhu

# Research Interests Wayfinder: A Prospective Student's Guide to Academic Exploration

## Purpose / (R2)

The "Research Interests Wayfinder: A Prospective Student's Guide to Academic Exploration" is designed to assist target users who are research oriented students interested in exploring different areas of research and seeking collaboration opportunities with professors or universities. This application aims to provide a user-friendly interface for students to discover faculty profiles, top keywords in publications, and recommended universities based on their research interests. By leveraging data from MongoDB, Neo4j, and MySQL databases, the objective of the application is to streamline the process of finding potential research collaborators and institutions.

## Demo / (R3)

https://mediaspace.illinois.edu/media/t/1_pkig8bhe

## Usefulness (R4)

Research Wayfinder is a valuable tool for researchers, students, and anyone interested in exploring academic research topics. It enables users to:

- **Discover New Research**: Allows users to search for and explore academic research topics based on keywords.
- **Faculty Information**: Provides detailed information about faculty members, including their research interests, affiliations, and associated publications.
- **University Insights**: Offers insights into universities based on research activity and faculty expertise.
- **Find Experts**: Users can identify experts in specific research areas by comparing faculty members based on Keyword Relevance Citation Scores.
- **Gain Insights**: The application provides insights into research trends throughout the years, allowing users to understand research activity and expertise across different institutions. 

## Uniqueness (R5)

Research Wayfinder stands out as a unique application in the following ways:

- **Focused on Keywords**: While there are many academic search engines and databases available, Research Wayfinder's focus on keyword-based exploration sets it apart. It allows users to navigate through research content in a more targeted and intuitive manner.
- **Comprehensive Faculty Information**: Unlike traditional academic search engines, Research Wayfinder provides comprehensive information about faculty members, including their research interests, affiliations, and publication history.
- **Interactive Visualization**: The application offers interactive visualizations, such as sunburst charts, bar charts, tables and pie charts, to present research data in a user-friendly and engaging manner.
- **Rectangular card layout design**: The user interface of Research Wayfinder is designed using Bootstrap, a popular front-end framework for building responsive and mobile-first websites.

## Installation

To install the application, follow these steps:
1. Clone the repository to your local machine.
2. Install the required Python packages listed in `requirements.txt`.
3. Ensure that MongoDB, Neo4j, and MySQL databases are running with the necessary data.
4. Run the application using `python3 app.py`.
5. Access the application at `http://127.0.0.1:8050` in your web browser.

## Usage

Once the application is running, users can:
- Select a faculty member to view their profile details including their associated keywords and publications.
- Input a year range to view the top keywords in publications.
- Select a keyword to see the top universities associated with it.
- Choose a university to explore the top keywords for that institution.
- Add or delete their research interests and view related professors and universities.
- Click on a research interest to see recommended faculty members and universities based on Keyword Relevant Scores.

## Design (R6/R7/R8)

The application architecture consists of various widgets that interact with MongoDB, Neo4j, and MySQL databases to retrieve and display relevant information to users. Dash, a Python web framework, is used to build the web application, while Plotly is utilized for creating interactive visualizations.

## Widgets (R9/R10/R11/R12)

### Widget 1: Faculty Profile Viewer. User selects a faculty member from dropdown.

- **Source**: MongoDB and MySQL (Multidatabase querying for subwidget)
- **Functionality**: Allows users to select a faculty member from a dropdown menu and view their profile, including name, position, affiliation, photo, and research interests. Includes two additional hyperlinked widgets:
**Associated Keywords**: Retrieved using selected faculty id as input to mongodb database and returning keywords array for faculty member.
**Associated Publications**: Retrieved using multidatabase querying, taking publication_ids as output from mongodb and feeding input to the MySQL publication table to return publication details like title, venue, year and number of citations.

### Widget 2: Top Keywords in Publications. User inputs a year range in slider.
 
- **Source**: MongoDB
- **Functionality**: Displays the top keywords in publications within a selected year range using a range slider.

### Widget 3: Top Universities for Keyword by Faculty Members Count. User selects a keyword name from dropdown.

- **Source**: MySQL
- **Functionality**: Shows a pie chart of the top universities associated with a selected keyword based on the count of faculty members.

### Widget 4: Top Keywords for University by Keyword Relevant Citation (KRC) Score. User selects a university name from dropdown.

- **Source**: Neo4j
- **Functionality**: Displays a pie chart of the top keywords for a selected university based on their Keyword Relevant Score (KRC).

### Widget 5/6: Add/Delete Research Interests. User updates their research interests in a new table in MySQL

- **Source**: MySQL (Backend Update)
- **Functionality**: Allows users to add or delete their research interests. Provides feedback on the success or failure of the operation.

### Widget 5/6: List of User Research Interests. User clicks a research interest topic to retrieve KRC score calculation.

- **Source**: MySQL
- **Functionality**: Dynamically updates a table displaying the user's research interests. Users can click on keywords to view related professors and universities.

### Widget 7: Recommended Faculty for User Research Interest Clicked by KRC Score.

- **Source**: Neo4j
- **Functionality**: Displays recommended faculty members associated with a clicked keyword based on their KRC scores. Includes a pie chart showing the distribution of KRC scores.

### Widget 8: Recommended Universities by User Research Interest Clicked by KRC Score.

- **Source**: MySQL
- **Functionality**: Shows recommended universities associated with a clicked keyword based on their KRC scores. Includes a pie chart illustrating the distribution of scores.

## Implementation

- Dash: Python web framework for building web applications with Python.
- Plotly: Visualization library used to create interactive plots, charts and tables.
- MongoDB: Document database used to store faculty data.
- Neo4j: Graph database used to store publication and keyword data.
- MySQL: Relational database used to store faculty, university and research interest data.
- Bootstrap: Implemented for front-end design, providing responsive and card-like web layout and components.

## Database Techniques (R13/14/15)

### Indexing
- **Source**: mysql_utils.py (create_research_interests_table)
Indexing has been implemented in the `mysql_utils.py` file function create_research_interests_table() to enhance query performance. Specifically, an index has been created on the newly defined `research_interests` table for the `keyword_name` column.

### Constraint
- **Source**: mysql_utils.py (create_research_interests_table)
A constraint has been applied to the `research_interests` table in the `mysql_utils.py` file function create_research_interests_table() to enforce data integrity. The newly added `keyword_name` column has been defined as NOT NULL, ensuring that it cannot contain NULL values.

### Stored Procedure 

- **Source**: mysql_utils.py (create_add_research_interest_procedure)
- **Functionality**: Added a stored procedure named `AddResearchInterest` to the MySQL database. This stored procedure allows for the insertion of a new research interest into the `research_interests` table. The procedure takes a single parameter `keyword_name` and inserts the provided value into the `keyword_name` column of the table. This provides a more efficient and secure way to add new research interests to the database.

## Extra Credit Capabilities (A1)

### Multidatabase quering: Widget 1 Retrieves Faculty Publication Information Based on Selected Faculty Member from MongoDB and ingests into MySQL

- **Source**: mongodb_utils.py (fetch_mongodb_faculty_data), mysql_utils.py (get_publications_by_ids)
- **Functionality**: Allows users to select a faculty member from a dropdown menu and view their profile, including name, position, affiliation, photo, and research interests. Additionally, it ingests data from MySQL to retrieve publication rows based on the publication IDs associated with the selected faculty member.

## Note

- This application assumes that the databases are set up with the required schema and populated with relevant data.

## Contributions

I (Jasleen Kaur Sandhu) designed the entire application myself and spent approximately 50 hours on it. My contributions include:
- Designing the application architecture and components.
- Implementing the functionalities using Dash, Plotly, MongoDB, Neo4j, and MySQL.
- Documenting the project functions and writing the README.md file.
