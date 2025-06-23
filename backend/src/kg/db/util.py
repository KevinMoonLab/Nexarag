import os
from langchain_neo4j import Neo4jGraph
from neo4j import GraphDatabase
import neo4j
from neomodel import adb
from neomodel import config
import os
from dataclasses import dataclass

@dataclass
class NeomodelConnectionResult:
    success: bool
    message: str

async def neomodel_connect(uri = 'nexarag.neo4j'):
    # Extract environment variables
    neo4j_user = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "password")

    # Create URL
    neo4j_url = f"bolt://{neo4j_user}:{neo4j_password}@{uri}:7687"

    # Connect to Neo4j
    config.DATABASE_URL = neo4j_url

    try:
        await adb.set_connection(config.DATABASE_URL)
        return NeomodelConnectionResult(True, "Successfully connected to Neo4j!")
    except Exception as e:
        return NeomodelConnectionResult(False, f"Failed to connect to Neo4j: {str(e)}")


def load_config():
    config = {
        'database': {
            'uri': os.getenv('NEO4J_URI'),
            'username': os.getenv('NEO4J_USERNAME'),
            'password': os.getenv('NEO4J_PASSWORD'),
            'database': os.getenv('NEO4J_DATABASE', 'neo4j')  # Default to 'neo4j' if not set
        }
    }
    return config

def load_default_kg():
    config = load_config()
    return load_kg(config)

def load_kg(config):
    kg = Neo4jGraph(
        url=config['database']['uri'], 
        username=config['database']['username'], 
        password=config['database']['password'],
        database=config['database']['database']
    )
    return kg

def load_kg_db():
    config = load_config()
    auth = (config['database']['username'], config['database']['password'])
    uri = config['database']['uri']
    return lambda: GraphDatabase.driver(uri, auth=auth)

def run_query(kg, cypher, params=None):
    if params is None:
        params = {}
    with kg.session() as session:
        result = session.run(cypher, **params)
        return [serialize_record(record) for record in result]

def serialize_record(record):
    serialized = {}
    for key, value in record.items():
        if isinstance(value, (list, tuple)):
            serialized[key] = [serialize_node(item) if isinstance(item, neo4j.graph.Node) else item for item in value]
        elif isinstance(value, neo4j.graph.Node):
            serialized[key] = serialize_node(value)
        elif isinstance(value, neo4j.graph.Relationship):
            serialized[key] = serialize_relationship(value)
        else:
            serialized[key] = value
    return serialized

def serialize_node(node):
    return {
        "id": node.element_id,
        "labels": list(node.labels),
        "properties": dict(node)
    }

def serialize_relationship(relationship):
    return {
        "id": relationship.element_id, 
        "type": relationship.type, 
        "properties": dict(relationship) 
    }

def init_schema(tx):
    # Create unique constraint on paper_id
    tx.run("""
        CREATE CONSTRAINT paper_id_unique IF NOT EXISTS
        FOR (p:Paper)
        REQUIRE p.paper_id IS UNIQUE;
    """)
    # Create index on paper_id
    tx.run("""
        CREATE INDEX paper_id_index IF NOT EXISTS
        FOR (p:Paper)
        ON (p.paper_id);
    """)
    # Create unique constraint on author_id
    tx.run("""
        CREATE CONSTRAINT author_id_unique IF NOT EXISTS
        FOR (a:Author)
        REQUIRE a.author_id IS UNIQUE;
    """)
    # Create index on author_id
    tx.run("""
        CREATE INDEX author_id_index IF NOT EXISTS
        FOR (a:Author)
        ON (a.author_id);
    """)

def initialize(kg):
    with kg.session() as session:
        session.execute_write(init_schema)

def check_connection():
    try:
        db_loader = load_kg_db()
        with db_loader() as db:
            return db.verify_connectivity() is None
    except Exception as e:
        return False