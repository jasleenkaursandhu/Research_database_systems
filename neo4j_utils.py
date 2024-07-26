from neo4j import GraphDatabase
import pandas as pd

# Connect to Neo4j
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "Iamkhaleesi187"
DATABASE_NAME = "academicworld"

def execute_neo4j_query(uri, username, password, database_name, query):
    """
    Executes a Neo4j query and returns the result.

    Args:
        uri (str): The URI of the Neo4j server.
        username (str): The username for authentication.
        password (str): The password for authentication.
        database_name (str): The name of the database.
        query (str): The Neo4j query to be executed.

    Returns:
        list: A list of dictionaries containing the query result.
    """
    try:
        with GraphDatabase.driver(uri, auth=(username, password)) as driver:
            with driver.session(database=database_name) as session:
                result = session.run(query)
                return result.data()
    except Exception as e:
        print(f"Failed to execute Neo4j query: {e}")
        return None

# Widget 4 implementation
def get_university_keyword_scores(school):
    """
    Fetches keyword scores for a university from Neo4j.

    Args:
        school (str): The name of the university.

    Returns:
        pandas.DataFrame: A DataFrame containing keyword names and their total scores.
    """
    query = f'''
        MATCH (i1:INSTITUTE) <- [:AFFILIATION_WITH] - (f1:FACULTY) -[i:INTERESTED_IN] -> (k:KEYWORD)
        WHERE i1.name = "{school}"
        RETURN k.name, SUM(i.score) AS total_score
        ORDER BY total_score DESC
        LIMIT 10
    '''
    result = execute_neo4j_query(URI, USERNAME, PASSWORD, DATABASE_NAME, query)
    df = pd.DataFrame([dict(_) for _ in result]).rename(
        columns={'k.name': 'keyword', 'total_score': 'total score'})
    return df

# Widget 7 implementation
def fetch_top_professors_for_keyword(keyword):
    """
    Fetches the top professors associated with a given keyword from Neo4j.

    Args:
        keyword (str): The keyword for which to fetch top professors.

    Returns:
        list: A list of dictionaries containing professor names and their KRC scores.
    """
    neo4j_query = f"""
        MATCH (publication:PUBLICATION)-[rel:LABEL_BY]->(:KEYWORD {{name: '{keyword}'}})
        MATCH (faculty)-[:PUBLISH]->(publication)
        WITH faculty, publication, rel.score AS keyword_score, publication.numCitations AS num_citations
        RETURN faculty.name AS faculty_name, SUM(keyword_score * num_citations) AS KRC
        ORDER BY KRC DESC
        LIMIT 5
    """
    try:
        with GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD)) as driver:
            with driver.session(database=DATABASE_NAME) as session:
                result = session.run(neo4j_query)
                professors_with_scores = [{"professor": record["faculty_name"], "KRC": record["KRC"]} for record in result]
                return professors_with_scores
    except Exception as e:
        print(f"Failed to execute Neo4j query: {e}")
        return []
