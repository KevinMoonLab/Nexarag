import shutil
import sqlite3
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

def clear_conversation_history(session_id: str = "default"):
    history = SQLChatMessageHistory(
        session_id=session_id,
        connection_string="sqlite:////data/chat_conversations.db"
    )
    history.clear()

def get_conversation_history(session_id: str):
    history = SQLChatMessageHistory(
        session_id=session_id,
        connection_string="sqlite:////data/chat_conversations.db"
    )
    return history.messages

def list_all_sessions():
    conn = sqlite3.connect("/data/chat_conversations.db")
    cursor = conn.cursor()
    
    # Get all unique session IDs
    cursor.execute("SELECT DISTINCT session_id FROM message_store")
    sessions = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return sessions

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    return SQLChatMessageHistory(
        session_id=session_id,
        connection_string="sqlite:////data/chat_conversations.db"
    )

def get_session_summary(session_id: str):
    history = get_conversation_history(session_id)
    if not history:
        return {"session_id": session_id, "message_count": 0, "last_message": None}
    
    return {
        "session_id": session_id,
        "message_count": len(history),
        "first_message": history[0].content if history else None,
        "last_message": history[-1].content if history else None,
        "last_timestamp": history[-1].additional_kwargs.get('timestamp') if history else None
    }

def restore_conversation_from_backup(backup_file: str, target_db: str = "/data/chat_conversations.db"):
    shutil.copy2(backup_file, target_db)
    print(f"Conversations restored from {backup_file}")

def backup_conversations(backup_file: str = "chat_backup.db"):
    import shutil
    shutil.copy2("chat_conversations.db", backup_file)
    print(f"Conversations backed up to {backup_file}")