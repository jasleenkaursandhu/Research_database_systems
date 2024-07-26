import mysql.connector  # Importing MySQL connector for database operations
import logging  # Importing logging module for error handling/logging
import time  # Importing time module for timestamp

# Configuration for MySQL connection
config = {
    'user': 'root',  # MySQL username
    'password': 'Iamkhaleesi187',  # MySQL password
    'host': 'localhost',  # MySQL server hostname
    'database': 'academicworld',  # MySQL database name
    'raise_on_warnings': True  # Raise errors for warnings
}

# Class to manage MySQL database operations
class MySQLUtils:
    def __init__(self, config):
        self.config = config
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = mysql.connector.connect(**self.config)
        self.cursor = self.connection.cursor(buffered=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logging.exception("Exception occurred")  # Log any exceptions that occurred during database operations
        self.cursor.close()
        self.connection.close()

    def execute_query(self, query, values=None):
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            logging.exception(f"Failed to execute query: {error}")  # Log any errors that occurred during query execution
            self.connection.rollback()
            return False

    def fetch_data(self, query, values=None):
        self.cursor.execute(query, values)
        return self.cursor.fetchall()

    def create_index(self, table_name, column_name):
        index_name = f"idx_{table_name}_{column_name}"
        query = f"CREATE INDEX {index_name} ON {table_name} ({column_name})"
        return self.execute_query(query)

    def add_not_null_constraint(self, table_name, column_name):
        query = f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} VARCHAR(255) NOT NULL"
        return self.execute_query(query)

# Function to fetch faculty data from MySQL database
def fetch_faculty_data():
    with MySQLUtils(config) as db:
        query = "SELECT id, name FROM faculty"  # SQL query to fetch faculty data
        return db.fetch_data(query)

# Function to fetch all keyword names from MySQL database
def fetch_all_keywords():
    with MySQLUtils(config) as db:
        query = "SELECT id, name FROM keyword"  # SQL query to fetch all keyword names
        return db.fetch_data(query)

# Function to fetch all university names from MySQL database
def fetch_all_university_names():
    with MySQLUtils(config) as db:
        query = "SELECT name FROM university"  # SQL query to fetch all university names
        result = db.fetch_data(query)
        if result:
            return [row[0] for row in result]  # Return list of university names
        else:
            return []  # Return empty list if no data found

# Function to get publications by IDs from the MySQL database
def get_publications_by_ids(publication_ids):
    with MySQLUtils(config) as db:
        result = []
        for publication_id in publication_ids:
            query = f"SELECT * FROM publication WHERE id = {publication_id}"
            publications = db.fetch_data(query)
            if publications:
                result.extend(publications)
        return result

# Widget 3 implementation 
# Function to fetch universities with the most faculty for a given keyword
def fetch_universities_with_most_faculty(keyword):
    with MySQLUtils(config) as db:
        query = f"""
            SELECT u.name AS university_name, 
                   COUNT(DISTINCT f.id) AS num_faculty_members 
            FROM faculty f 
            JOIN faculty_keyword fk ON f.id = fk.faculty_id 
            JOIN keyword k ON fk.keyword_id = k.id 
            JOIN university u ON f.university_id = u.id 
            WHERE k.name = '{keyword}'
            GROUP BY u.name 
            ORDER BY num_faculty_members DESC 
            LIMIT 10;
        """  # SQL query to fetch universities with the most faculty for a given keyword
        return db.fetch_data(query)

# Widget 5/6 implementation updation of backend MySQL
# Database techniques- add indexing and constraint.
# Function to create the research_interests table if it doesn't exist
def create_research_interests_table():
    with MySQLUtils(config) as db:
        query = """
            CREATE TABLE IF NOT EXISTS research_interests (
                keyword_name VARCHAR(255) NOT NULL PRIMARY KEY
            )
        """  # SQL query to create research interests table if not exists
        db.execute_query(query)
        
        # Add indexing to the keyword_name column
        db.create_index("research_interests", "keyword_name")

        # Add constraint to make keyword_name column NOT NULL
        db.add_not_null_constraint("research_interests", "keyword_name")

# Function to create a stored procedure for adding a research interest
# Database techniques- stored procedure implementation to insert into research interests.
def create_add_research_interest_procedure():
    with MySQLUtils(config) as db:
        procedure_query = """
            CREATE PROCEDURE AddResearchInterest(IN keyword_name VARCHAR(255))
            BEGIN
                INSERT INTO research_interests (keyword_name) VALUES (keyword_name);
            END;
        """
        db.execute_query(procedure_query)

# Function to add a research interest using the stored procedure
# Database techniques- stored procedure implementation.
def add_research_interest_with_procedure(keyword_name):
    with MySQLUtils(config) as db:
        create_add_research_interest_procedure()  # Create the stored procedure first
        query = "CALL AddResearchInterest(%s)"  # SQL query to call the stored procedure
        values = (keyword_name, )
        if db.execute_query(query, values):
            logging.info("Keyword added to research_interests successfully")  # Log success message if keyword added successfully

# Function to delete a research interest from the research_interests table
def delete_research_interest(keyword):
    with MySQLUtils(config) as db:
        if not research_interests_table_exists(db):
            logging.error("Error: research_interests table does not exist")  # Log error if research_interests table does not exist
            return
        query = "DELETE FROM research_interests WHERE keyword_name = %s"  # SQL query to delete a research interest
        values = (keyword, )
        if db.execute_query(query, values):
            logging.info("Keyword deleted from research_interests successfully")  # Log success message if keyword deleted successfully

# Function to check if the research_interests table exists in the database
def research_interests_table_exists(db):
    query = "SHOW TABLES LIKE 'research_interests'"  # SQL query to check if research_interests table exists
    return bool(db.fetch_data(query))

# Function to fetch all research interests of the user from backend in real-time
def fetch_all_research_interests():
    with MySQLUtils(config) as db:
        if not research_interests_table_exists(db):
            create_research_interests_table(db)

        query = "SELECT keyword_name FROM research_interests"
        result = db.fetch_data(query)
        if result:
            return [row[0] for row in result]
        else:
            return []

# Widget 8 implementation 
# Function to fetch top universities based on KRC score associated with a keyword from research_interests table
def fetch_top_universities_for_keyword(keyword):
    with MySQLUtils(config) as db:
        query = f"""SELECT university.name AS university, COUNT(*) AS count, SUM(score) AS score
                    FROM university, faculty_keyword, faculty, research_interests, keyword
                    WHERE university.id = faculty.university_id 
                        AND faculty_keyword.faculty_id = faculty.id 
                        AND faculty_keyword.keyword_id = keyword.id 
                        AND keyword.name = research_interests.keyword_name
                    GROUP BY university.name
                    ORDER BY score DESC
                    LIMIT 5"""  # SQL query to fetch top universities based on KRC score associated with a keyword
        result = db.fetch_data(query)
        universities = []
        for row in result:
            universities.append({'university': row[0], 'score': row[2]})
        return universities  # Return list of top universities with their scores
