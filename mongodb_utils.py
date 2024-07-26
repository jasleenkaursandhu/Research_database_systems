from pymongo import MongoClient

# Connect to MongoDB
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['academicworld']

# Widget 1 implementation
def fetch_mongodb_faculty_data(faculty_id):
    """
    Fetches faculty data from MongoDB based on the given faculty ID.

    Args:
        faculty_id (int): The ID of the faculty member.

    Returns:
        dict: A dictionary containing the processed faculty data with extracted fields.
    """
    faculty_collection = mongo_db['faculty']
    faculty_data = faculty_collection.find_one({'id': faculty_id})

    # Extracting fields with handling for None/null values
    affiliation = faculty_data.get('affiliation', {})
    position = faculty_data.get('position', '')
    research_interest = faculty_data.get('researchInterest', '')
    email = faculty_data.get('email', '')
    phone = faculty_data.get('phone', '')

    # Extracting keywords with handling for None/null values
    keywords = []
    for keyword_data in faculty_data.get('keywords', []):
        keyword_name = keyword_data.get('name', '')
        keywords.append(keyword_name)

    # Extracting publication IDs
    publication_ids = faculty_data.get('publications', [])

    # Creating a new dictionary with extracted data
    processed_faculty_data = {
        'name': faculty_data.get('name', ''),
        'position': position,
        'researchInterest': research_interest,
        'email': email,
        'phone': phone,
        'affiliation': {
            'name': affiliation.get('name', ''),
            'photoUrl': affiliation.get('photoUrl', '')
        },
        'photoUrl': faculty_data.get('photoUrl', ''),
        'keywords': keywords,
        'publication_ids': publication_ids  # Storing publication IDs
    }

    return processed_faculty_data

# Widget 2 implementation
def get_top_keywords_by_year_range(year_range):
    """
    Fetches the top keywords by publication count within the specified year range from MongoDB.

    Args:
        year_range (tuple): A tuple containing the start and end years of the range.

    Returns:
        list: A list of dictionaries containing the top keywords and their publication counts.
    """
    pipeline = [
        {"$match": {"year": {"$gte": year_range[0], "$lte": year_range[1]}}},
        {"$unwind": "$keywords"},
        {"$group": {"_id": "$keywords.name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
        {"$project": {"_id": 1, "count": 1}}
    ]

    result = mongo_db.publications.aggregate(pipeline)
    top_keywords = [{"keyword": doc["_id"], "count": doc["count"]} for doc in result]
    return top_keywords

