import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from framework.activity_decorator import activity, ActivityBase, ActivityResult
from framework.main import DigitalBeing

logger = logging.getLogger(__name__)

@activity(
    name="CheckPendingMessages",
    energy_cost=0.3,
    cooldown=60,  # Check every 2 seconds
    required_skills=[]  # No specific skills required for checking
)
class CheckPendingMessagesActivity(ActivityBase):
    """Activity that monitors chat activity and manages the chat response system."""
    
    def __init__(self):
        super().__init__()

    async def execute(self, shared_data) -> ActivityResult:
        try:
            logger.info("Checking chat activity status")
            
            # Initialize the being
            being = DigitalBeing()
            being.initialize()
            
            # Get recent chat history
            chat_history = being.memory.get_chat_history(limit=5)  # Just check last few messages
            
            if not chat_history:
                logger.info("No chat history found")
                being.configs["activity_constraints"]["activities_config"]["ReplyToChatActivity"]["enabled"] = False
                return ActivityResult.success_result({"active": False, "reason": "no_history"})
            
            # Get the last message
            last_message = chat_history[-1]
            
            # Get sender directly from message since it's not wrapped in data field
            last_msg_sender = last_message.get("sender", "")
            last_msg_time = datetime.fromisoformat(last_message.get("timestamp", "").replace("Z", "+00:00"))
            now = datetime.now(last_msg_time.tzinfo)
            
            # Check if there's recent activity (within last 5 minutes)
            is_recent = (now - last_msg_time) <= timedelta(minutes=5)
            
            # Check if last message was from user
            is_last_from_user = last_msg_sender.lower() == "user"
            
            # Enable chat activity if:
            # 1. There's recent activity AND
            # 2. The last message was from a user
            should_enable = is_recent and is_last_from_user
            
            being.configs["activity_constraints"]["activities_config"]["ReplyToChatActivity"]["enabled"] = should_enable
            
            status_info = {
                "active": should_enable,
                "last_message_age_seconds": (now - last_msg_time).total_seconds(),
                "last_message_from": last_msg_sender,
                "reason": "recent_user_message" if should_enable else (
                    "too_old" if not is_recent else "last_from_being"
                )
            }
            
            logger.info(f"Chat activity status: {status_info}")
            return ActivityResult.success_result(status_info)
            
        except Exception as e:
            logger.error(f"Error in CheckPendingMessagesActivity: {e}", exc_info=True)
            return ActivityResult.error_result(str(e))