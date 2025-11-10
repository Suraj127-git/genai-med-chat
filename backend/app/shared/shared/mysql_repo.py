from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Text, JSON, Enum, TIMESTAMP
from sqlalchemy.sql import func
from shared.config import settings

metadata = MetaData()

users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", String(255), unique=True),
    Column("email", String(255), unique=True),
    Column("password_hash", String(255)),
    Column("role", String(50)),
    Column("created_at", TIMESTAMP, server_default=func.current_timestamp())
)

conversations = Table(
    "conversations", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer),
    Column("title", String(255)),
    Column("created_at", TIMESTAMP, server_default=func.current_timestamp())
)

messages = Table(
    "messages", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("conv_id", Integer),
    Column("sender", Enum("user", "bot")),
    Column("content", Text),
    Column("metadata", JSON),
    Column("created_at", TIMESTAMP, server_default=func.current_timestamp())
)

# Simple synchronous engine for demo. In production use async engine + session
engine = create_engine(settings.MYSQL_DSN, echo=False, future=True)


class MySQLRepo:
    def __init__(self):
        # Create tables if not exist (simple demo)
        metadata.create_all(engine)

    def create_user(self, username: str, email: str, password_hash: str, role: str = "user"):
        with engine.begin() as conn:
            res = conn.execute(users.insert().values(username=username, email=email, password_hash=password_hash, role=role))
            return res.inserted_primary_key[0]

    def create_message(self, conv_id, sender, content, metadata: dict = None):
        with engine.begin() as conn:
            res = conn.execute(messages.insert().values(conv_id=conv_id, sender=sender, content=content, metadata=metadata))
            return res.inserted_primary_key[0]

    def create_conversation(self, user_id: int, title: str = None):
        with engine.begin() as conn:
            res = conn.execute(conversations.insert().values(user_id=user_id, title=title))
            return res.inserted_primary_key[0]

    def create_graph_node(self, conv_id: int, node_type: str, content: str, metadata: dict = None):
        # Using raw SQL execution here (tables were created via schemas.sql)
        with engine.begin() as conn:
            res = conn.execute(
                "INSERT INTO graph_nodes (conv_id, node_type, content, metadata) VALUES (%s, %s, %s, %s)",
                (conv_id, node_type, content, metadata or {})
            )
            return conn.execute("SELECT LAST_INSERT_ID()").scalar()

    def create_graph_edge(self, conv_id: int, from_node: int, to_node: int, relation: str, metadata: dict = None):
        with engine.begin() as conn:
            res = conn.execute(
                "INSERT INTO graph_edges (conv_id, from_node, to_node, relation, metadata) VALUES (%s, %s, %s, %s, %s)",
                (conv_id, from_node, to_node, relation, metadata or {})
            )
            return conn.execute("SELECT LAST_INSERT_ID()").scalar()

    def get_graph(self, conv_id: int):
        with engine.begin() as conn:
            nodes = conn.execute("SELECT id, node_type, content, metadata, created_at FROM graph_nodes WHERE conv_id = %s", (conv_id,)).fetchall()
            edges = conn.execute("SELECT id, from_node, to_node, relation, metadata, created_at FROM graph_edges WHERE conv_id = %s", (conv_id,)).fetchall()
            # convert to list of dicts
            nodes_list = [dict(row._mapping) for row in nodes]
            edges_list = [dict(row._mapping) for row in edges]
            return {"nodes": nodes_list, "edges": edges_list}