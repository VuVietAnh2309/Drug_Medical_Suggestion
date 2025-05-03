"""
Database Initialization Script

This script loads prescription data from an Excel file into MongoDB.
It creates a 'thuoc_database' with a 'thuoc_collection' collection
containing patient information and prescribed medications.
"""

import pandas as pd
from pymongo import MongoClient

def connect_to_mongodb(host='localhost', port=27017):
    """
    Establish connection to MongoDB server.
    
    Args:
        host: MongoDB server hostname (default: localhost)
        port: MongoDB server port (default: 27017)
        
    Returns:
        MongoDB client and database object
    """
    try:
        client = MongoClient(f'mongodb://{host}:{port}/')
        db = client['thuoc_database']
        print(f"✅ Successfully connected to MongoDB at {host}:{port}")
        return client, db
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        return None, None

def load_data_from_excel(file_path):
    """
    Load prescription data from Excel file.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        Pandas DataFrame containing the data
    """
    try:
        print(f"Loading data from {file_path}...")
        df = pd.read_excel(file_path)
        print(f"✅ Successfully loaded {len(df)} records from Excel file")
        return df
    except Exception as e:
        print(f"❌ Error loading Excel file: {e}")
        return None

def populate_mongodb(collection, dataframe):
    """
    Populate MongoDB collection with data from DataFrame.
    
    Args:
        collection: MongoDB collection object
        dataframe: Pandas DataFrame containing the data
        
    Returns:
        Number of records inserted
    """
    if dataframe is None or collection is None:
        return 0
        
    try:
        # Convert DataFrame to list of dictionaries
        records = dataframe.to_dict(orient='records')
        
        # Clear existing data
        delete_result = collection.delete_many({})
        print(f"Deleted {delete_result.deleted_count} existing records")
        
        # Insert new data
        insert_result = collection.insert_many(records)
        inserted_count = len(insert_result.inserted_ids)
        print(f"✅ Successfully inserted {inserted_count} records into MongoDB")
        return inserted_count
    except Exception as e:
        print(f"❌ Error populating MongoDB: {e}")
        return 0

def main():
    """Main function to execute the database initialization process."""
    # Database connection
    client, db = connect_to_mongodb()
    if client is None or db is None:
        return
    
    # Collection reference
    thuoc_collection = db['thuoc_collection']
    
    # Data file path
    file_path = 'data/data_preprocess.xlsx'
    
    # Load and process data
    df = load_data_from_excel(file_path)
    
    # Populate database
    records_inserted = populate_mongodb(thuoc_collection, df)
    
    # Summary
    print(f"\n===== Database Initialization Summary =====")
    print(f"Database: thuoc_database")
    print(f"Collection: thuoc_collection")
    print(f"Records inserted: {records_inserted}")
    print(f"==========================================")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    main()