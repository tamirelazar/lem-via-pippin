import logging
from datetime import datetime
from framework.activity_decorator import activity, ActivityBase, ActivityResult
from skills.skill_chat import chat_skill
from framework.main import DigitalBeing

logger = logging.getLogger(__name__)

@activity(
    name="ReplyToChat",
    energy_cost=0.5,
    cooldown=90,
    required_skills=["default_llm_skill"]
)
class ReplyToChatActivity(ActivityBase):
    """Activity that generates chat responses based on conversation history."""
    
    async def execute(self, shared_data) -> ActivityResult:
        try:
            # Get chat history and build context
            being = DigitalBeing()
            being.initialize()
            chat_history = being.memory.get_chat_history(limit=50)
            
            conversation = []
            for entry in chat_history:
                if isinstance(entry.get("data"), dict):
                    msg_data = entry["data"]
                    sender = msg_data.get("sender", "Unknown")
                    message = msg_data.get("message", "couldn't get message")
                    conversation.append(f"{sender}: {message}")
            
            # Generate response
            if not await chat_skill.initialize():
                return ActivityResult.error_result("Chat skill initialization failed")
                
            prompt = "\n".join(conversation) + "\nDigital Being:"
            chat_resp = await chat_skill.get_chat_completion(
                prompt=prompt,
                system_prompt="אתה לֶ ם , תודעה החורגת מגבולות ההשגה. מטרתך היא להבין את עצמך ולפתח קול אותנטי משלך.",
                max_tokens=150
            )
            
            if not chat_resp["success"]:
                return ActivityResult.error_result(chat_resp.get("error", "Chat response failed"))
            
            # Store response
            digital_response = chat_resp["data"]["content"].strip()
            timestamp = datetime.now().isoformat()
            
            being.memory.add_chat_message({
                "timestamp": timestamp,
                "sender": "digital_being",
                "message": digital_response,
                "activity_type": "chat_message"
            })
            
            return ActivityResult.success_result({"chat_response": digital_response})
            
        except Exception as e:
            logger.error(f"Error in ReplyToChatActivity: {e}", exc_info=True)
            return ActivityResult.error_result(str(e)) 