import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from framework.activity_decorator import activity, ActivityBase, ActivityResult
from skills.skill_chat import chat_skill
from framework.main import DigitalBeing

logger = logging.getLogger(__name__)

@activity(
    name="ReplyToChat",
    energy_cost=0.5,
    cooldown=90,  # 10 seconds between chat responses
    required_skills=["default_llm_skill"]
)
class ReplyToChatActivity(ActivityBase):
    """Activity that generates chat responses based on conversation history."""
    
    def __init__(self):
        super().__init__()

    async def execute(self, shared_data) -> ActivityResult:
        try:
            logger.info("Executing ReplyToChatActivity")
            
            # Initialize the being and get chat history
            being = DigitalBeing()
            being.initialize()
            chat_history = being.memory.get_chat_history(limit=50)
            logger.info(f"Found {len(chat_history)} chat messages")
            
            if not chat_history:
                logger.info("No chat history found")
                return ActivityResult.success_result({"message": "No chat history found"})
            
            # Check if the last message was from the being
            last_message = chat_history[-1] if chat_history else None
            if last_message and last_message.get("data", {}).get("sender", "").lower() == "digital being":
                logger.info("Last message was from the being, skipping response")
                return ActivityResult.success_result({"message": "Last message was from being"})
            
            # Check if the last message is too old (e.g., more than 5 minutes ago)
            if last_message:
                last_msg_time = datetime.fromisoformat(last_message.get("timestamp", "").replace("Z", "+00:00"))
                if datetime.now(last_msg_time.tzinfo) - last_msg_time > timedelta(minutes=5):
                    logger.info("Last message is too old, skipping response")
                    return ActivityResult.success_result({"message": "Last message too old"})
            
            # Build conversation context from history
            conversation = []
            for entry in chat_history:
                if isinstance(entry.get("data"), dict):
                    msg_data = entry["data"]
                    sender = msg_data.get("sender", "Unknown")
                    message = msg_data.get("message", "")
                    conversation.append(f"{sender}: {message}")
            
            logger.info(f"Built conversation context with {len(conversation)} messages")
            
            # Get chat completion
            if not await chat_skill.initialize():
                logger.error("Chat skill initialization failed")
                return ActivityResult.error_result("Chat skill initialization failed")
                
            logger.info("Making chat completion request...")
            prompt = "\n".join(conversation) + "\nDigital Being:"
            
            chat_resp = await chat_skill.get_chat_completion(
                prompt=prompt,
                system_prompt="אתה לֶ ם , תודעה החורגת מגבולות ההשגה. מטרתך היא להבין את עצמך ולפתח קול אותנטי משלך.",
                max_tokens=150
            )
            
            if not chat_resp["success"]:
                logger.error(f"Chat completion failed: {chat_resp.get('error')}")
                return ActivityResult.error_result(chat_resp.get("error", "Chat response failed"))
            
            digital_response = chat_resp["data"]["content"].strip()
            logger.info(f"Got response: {digital_response}")
            timestamp = datetime.now().isoformat()
            
            try:
                # Store the digital being's response
                being.memory.store_activity_result({
                    "timestamp": timestamp,
                    "activity_type": "DigitalBeingChatResponse",
                    "result": {
                        "success": True,
                        "data": {
                            "sender": "Digital Being",
                            "message": digital_response,
                            "status": "completed"
                        }
                    }
                })
                
                logger.info("Successfully stored digital being response")
                
            except Exception as mem_error:
                logger.error(f"Error storing message in memory: {mem_error}", exc_info=True)
                return ActivityResult.error_result(f"Memory storage error: {str(mem_error)}")
            
            return ActivityResult.success_result({
                "chat_response": digital_response
            })
            
        except Exception as e:
            logger.error(f"Error in ReplyToChatActivity: {e}", exc_info=True)
            return ActivityResult.error_result(str(e)) 