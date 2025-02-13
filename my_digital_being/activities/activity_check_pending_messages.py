import logging
from typing import Dict, Any
from framework.activity_decorator import activity, ActivityBase, ActivityResult
from framework.main import DigitalBeing

logger = logging.getLogger(__name__)

@activity(
    name="CheckPendingMessages",
    energy_cost=0.1,
    cooldown=2,  # Check every 2 seconds
    required_skills=[]  # No specific skills required for checking
)
class CheckPendingMessagesActivity(ActivityBase):
    """Activity that checks for pending chat messages and adjusts priority of ReplyToChatActivity."""
    
    def __init__(self):
        super().__init__()

    async def execute(self, shared_data) -> ActivityResult:
        try:
            logger.info("Checking for pending messages")
            
            # Initialize the being and get recent activities
            being = DigitalBeing()
            being.initialize()
            logger.info(f"Memory contents: {being.memory.short_term_memory}")  # Log raw memory
            
            all_entries = being.memory.get_recent_activities(limit=20)
            logger.info(f"Found {len(all_entries)} recent entries to check")
            logger.info(f"Entries after get_recent_activities: {all_entries}")  # Log transformed entries
            
            # Debug log the entries
            for entry in all_entries:
                logger.info(f"Entry: {entry}")
            
            # Look for pending messages
            has_pending = False
            for entry in reversed(all_entries):
                if (entry["activity_type"] == "UserChatMessage" and 
                    isinstance(entry.get("data"), dict) and
                    entry["data"].get("status") == "pending"):
                    has_pending = True
                    logger.info(f"Found pending message: {entry}")
                    break
                else:
                    logger.info(f"Entry did not match pending criteria: {entry}")
            
            if has_pending:
                # If there are pending messages, increase priority of ReplyToChatActivity
                logger.info("Found pending messages")
                return ActivityResult.success_result({"pending_messages": True})
            else:
                logger.info("No pending messages found")
                return ActivityResult.success_result({"pending_messages": False})
            
        except Exception as e:
            logger.error(f"Error in CheckPendingMessagesActivity: {e}", exc_info=True)
            return ActivityResult.error_result(str(e)) 