"""Memory management system for storing and retrieving activity history."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class Memory:
    def __init__(self, storage_path: str = "./storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.short_term_memory: List[Dict[str, Any]] = []
        self.long_term_memory: Dict[str, Any] = {}
        self.chat_log: List[Dict[str, Any]] = []  # New dedicated chat log
        self.memory_file = self.storage_path / "memory.json"
        self.initialize()

    def initialize(self):
        """Initialize memory system."""
        self._load_memory()
        # self.sync_chat_log()  # Add sync_chat_log call after loading memory

    def _load_memory(self):
        """Load memory from persistent storage."""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, "r") as f:
                    try:
                        data = json.load(f)
                        if isinstance(data, dict):
                            self.long_term_memory = data.get("long_term", {})
                            self.short_term_memory = data.get("short_term", [])
                            self.chat_log = data.get("chat_log", [])  # Load chat log
                        else:
                            logger.warning(
                                "Invalid memory file format, resetting memory"
                            )
                            self.long_term_memory = {}
                            self.short_term_memory = []
                            self.chat_log = []
                            self.persist()  # Reset the file with proper format
                    except json.JSONDecodeError as je:
                        logger.error(f"Failed to parse memory file: {je}")
                        # Backup corrupted file
                        backup_path = self.memory_file.with_suffix(".json.bak")
                        self.memory_file.rename(backup_path)
                        logger.info(f"Backed up corrupted memory file to {backup_path}")
                        # Reset memory
                        self.long_term_memory = {}
                        self.short_term_memory = []
                        self.chat_log = []
                        self.persist()  # Create new file with proper format
        except Exception as e:
            logger.error(f"Failed to load memory: {e}")
            self.long_term_memory = {}
            self.short_term_memory = []
            self.chat_log = []

    def store_activity_result(self, activity_record: Dict[str, Any]):
        """Store the result of an activity in memory."""
        try:
            # Ensure we have a valid activity record
            if not isinstance(activity_record, dict):
                logger.error("Invalid activity record format")
                return

            # Extract and validate the result
            result = activity_record.get("result", {})
            if isinstance(result, dict):
                # Store standardized activity record with UTC timestamp
                timestamp = datetime.now(timezone.utc).isoformat()
                activity_type = activity_record.get("activity_type", "Unknown")
                
                # Check if this is a chat message activity before creating memory entry
                if activity_type in ["UserChatMessage", "ReplyToChatActivity"] and result.get("data"):
                    chat_data = result["data"]
                    # Create chat entry format
                    chat_entry = {
                        "timestamp": timestamp,
                        "sender": chat_data.get("sender", "unknown"),
                        "message": chat_data.get("message", ""),
                        "activity_type": "chat_message"
                    }
                    # Add to chat log
                    self.chat_log.append(chat_entry)
                    logger.info(f"Added chat message to chat log from {chat_entry['sender']}")
                
                # Create and store the activity record
                memory_entry = {
                    "timestamp": timestamp,
                    "activity_type": activity_type,
                    "success": result.get("success", False),
                    "error": result.get("error"),
                    "data": result.get("data"),
                    "metadata": result.get("metadata", {}),
                }
                
                self.short_term_memory.append(memory_entry)
                self._consolidate_memory()
                self.persist()  # Persist after each update
                logger.info(
                    f"Stored activity result for {memory_entry['activity_type']}"
                )
            else:
                logger.error(f"Invalid result format in activity record: {result}")

        except Exception as e:
            logger.error(f"Failed to store activity result: {e}")

    def _consolidate_memory(self):
        """Consolidate short-term memory into long-term memory."""
        if len(self.short_term_memory) > 100:  # Keep last 100 activities in short-term
            older_memories = self.short_term_memory[
                :-50
            ]  # Move older ones to long-term
            self.short_term_memory = self.short_term_memory[-50:]

            for memory in older_memories:
                activity_type = memory["activity_type"]
                if activity_type not in self.long_term_memory:
                    self.long_term_memory[activity_type] = []
                self.long_term_memory[activity_type].append(memory)

    def get_recent_activities(
        self, limit: int = 10, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get recent activities from memory with success/failure status."""
        # Sort all activities by timestamp in descending order (most recent first)
        all_activities = sorted(
            self.short_term_memory, key=lambda x: x["timestamp"], reverse=True
        )

        # Apply pagination
        paginated_activities = all_activities[offset : offset + limit]

        # Format timestamps for display
        return [
            {
                "timestamp": self._format_timestamp(activity["timestamp"]),
                "activity_type": activity["activity_type"],
                "success": activity["success"],
                "error": activity.get("error"),
                "data": activity.get("data"),
                "metadata": activity.get("metadata", {}),
            }
            for activity in paginated_activities
        ]

    def _format_timestamp(self, timestamp_str: str) -> str:
        """Format ISO timestamp to human-readable format."""
        try:
            dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            return dt.isoformat()  # Return a full ISO 8601 formatted string
        except Exception:
            return timestamp_str

    def get_activity_history(self, activity_type: str) -> List[Dict[str, Any]]:
        """Get history of specific activity type."""
        activities = self.long_term_memory.get(activity_type, [])
        return [
            {**activity, "timestamp": self._format_timestamp(activity["timestamp"])}
            for activity in activities
        ]

    def persist(self):
        """Persist memory to storage."""
        try:
            memory_data = {
                "short_term": self.short_term_memory,
                "long_term": self.long_term_memory,
                "chat_log": self.chat_log,  # Include chat log in persistence
            }

            # Write to a temporary file first
            temp_file = self.memory_file.with_suffix(".json.tmp")
            with open(temp_file, "w") as f:
                json.dump(memory_data, f, indent=2)

            # Rename temporary file to actual file (atomic operation)
            temp_file.replace(self.memory_file)

        except Exception as e:
            logger.error(f"Failed to persist memory: {e}")

    def clear(self):
        """Clear all memory."""
        self.short_term_memory = []
        self.long_term_memory = {}
        self.chat_log = []  # Clear chat log
        self.persist()

    def get_activity_count(self) -> int:
        """Get total number of activities in memory."""
        return len(self.short_term_memory) + sum(
            len(activities) for activities in self.long_term_memory.values()
        )

    def get_last_activity_timestamp(self) -> str:
        """Get formatted timestamp of the last activity."""
        if not self.short_term_memory:
            return "No activities recorded"

        last_activity = max(self.short_term_memory, key=lambda x: x["timestamp"])
        return self._format_timestamp(last_activity["timestamp"])

    def add_chat_message(self, message: dict) -> None:
        """
        Add a chat message to the chat log.
        The message dict can be either:
        1. A direct message format:
          - "sender": "user" or "digital_being"
          - "message": the text
          - "timestamp": ISO timestamp string
        2. An activity format:
          - "activity_type": "UserChatMessage"
          - "timestamp": ISO timestamp string
          - "data": {
              "sender": "user" or "digital_being"
              "message": the text
            }
        """
        # Extract message data based on format
        if "data" in message and "activity_type" in message:
            # Activity format
            chat_entry = {
                "timestamp": message.get("timestamp", datetime.now(timezone.utc).isoformat()),
                "sender": message["data"].get("sender", "unknown"),
                "message": message["data"].get("message", ""),
                "activity_type": "chat_message"
            }
        else:
            # Direct format
            chat_entry = {
                "timestamp": message.get("timestamp", datetime.now(timezone.utc).isoformat()),
                "sender": message["sender"],
                "message": message["message"],
                "activity_type": "chat_message"
            }
        
        # Add to chat log
        self.chat_log.append(chat_entry)
        
        # Also maintain backward compatibility by adding to short-term memory if not already an activity
        if "activity_type" not in message:
            activity_entry = {
                "timestamp": chat_entry["timestamp"],
                "activity_type": "UserChatMessage",
                "success": True,
                "error": None,
                "data": {
                    "sender": chat_entry["sender"],
                    "message": chat_entry["message"],
                    "status": "pending"
                },
                "metadata": {}
            }
            self.short_term_memory.append(activity_entry)
        else:
            self.short_term_memory.append(message)
        
        self.persist()

    def get_chat_history(self, limit: int = 50) -> list:
        """
        Retrieve up to the latest `limit` chat messages from the chat log.
        """
        return self.chat_log[-limit:]

    def sync_chat_log(self):
        """Synchronize chat messages from activities into chat_log."""
        try:
            # Create a set of existing chat message timestamps for efficient lookup
            existing_timestamps = {entry["timestamp"] for entry in self.chat_log}
            
            # Helper function to process activities
            def process_activities(activities):
                for activity in activities:
                    # Skip if activity timestamp already exists in chat_log
                    if activity["timestamp"] in existing_timestamps:
                        continue
                        
                    # Check for chat-related activity types
                    if activity["activity_type"] in ["UserChatMessage", "ReplyToChatActivity"]:
                        if activity.get("data") and activity["success"]:
                            if activity["data"].get("sender") == "user":
                                chat_entry = {
                                    "timestamp": activity["timestamp"],
                                    "sender": activity["data"].get("sender", ""),
                                    "message": activity["data"].get("message", ""),
                                    "activity_type": "chat_message"
                                }
                            elif activity["data"].get("sender") == "digital_being" or activity["data"].get("chat_response"):
                                chat_entry = {
                                    "timestamp": activity["timestamp"],
                                    "sender": activity["data"].get("digital_being", ""),
                                    "message": activity["data"].get("chat_response", ""),
                                    "activity_type": "chat_message"
                                }
                            self.chat_log.append(chat_entry)
                            existing_timestamps.add(activity["timestamp"])
                            logger.info(f"Synced chat message from {chat_entry['sender']}")
            
            # Process short-term memory
            process_activities(self.short_term_memory)
            
            # Process long-term memory
            for activity_type, activities in self.long_term_memory.items():
                if activity_type in ["UserChatMessage", "ReplyToChatActivity"]:
                    process_activities(activities)
            
            # Sort chat log by timestamp
            self.chat_log.sort(key=lambda x: x["timestamp"])
            
            # Persist changes
            self.persist()
            logger.info("Chat log synchronization completed")
            
        except Exception as e:
            logger.error(f"Failed to synchronize chat log: {e}")
