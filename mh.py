from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import re
import json

class MentalHealthChatbot:
    def __init__(self):
        self.model_name = "facebook/opt-350m"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=False  # Changed this setting
        )        
        # Load predefined responses and crisis resources
        self.crisis_resources = {
            "emergency": "If you're having thoughts of self-harm, please call emergency services (911) or contact the following:",
            "suicide_prevention": "National Suicide Prevention Lifeline: 988",
            "crisis_text": "Crisis Text Line: Text HOME to 741741",
        }
        
        # Define safety protocols and triggers
        self.crisis_keywords = [
            "suicide", "kill", "die", "harm", "hurt myself",
            "end it all", "give up", "no point"
        ]
        
        # Load therapeutic conversation templates
        self.conversation_templates = {
            "greeting": "Hi, I'm here to listen and support you. How are you feeling today?",
            "validation": "I hear that you're feeling {emotion}. That must be really difficult.",
            "exploration": "Could you tell me more about what's making you feel this way?",
            "coping": "Would you like to explore some coping strategies together?"
        }
        
        # Define therapeutic techniques
        self.techniques = {
            "breathing": "Let's try a simple breathing exercise: Breathe in for 4 counts, hold for 4, exhale for 4.",
            "grounding": "Can you name 5 things you can see, 4 things you can touch, 3 things you can hear?",
            "reframing": "Let's try to look at this situation from a different perspective."
        }

    def preprocess_input(self, user_input):
        """Clean and normalize user input"""
        text = user_input.lower().strip()
        return text

    def check_crisis_indicators(self, text):
        """Check for crisis keywords and return appropriate resources"""
        for keyword in self.crisis_keywords:
            if keyword in text:
                return True, self.format_crisis_response()
        return False, None

    def format_crisis_response(self):
        """Format crisis resources and emergency contact information"""
        response = [
            self.crisis_resources["emergency"],
            self.crisis_resources["suicide_prevention"],
            self.crisis_resources["crisis_text"],
            "\nWhile I'm here to listen, it's important to reach out to professional help in crisis situations."
        ]
        return "\n".join(response)

    def generate_response(self, user_input, conversation_history):
        """Generate appropriate therapeutic response using Llama model"""
        # Preprocess input
        processed_input = self.preprocess_input(user_input)
        
        # Check for crisis indicators
        crisis_detected, crisis_response = self.check_crisis_indicators(processed_input)
        if crisis_detected:
            return crisis_response
        
        # Prepare prompt with conversation history and therapeutic context
        prompt = self.prepare_therapeutic_prompt(processed_input, conversation_history)
        
        # Generate response using Llama model
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        outputs = self.model.generate(
            inputs["input_ids"],
            max_length=512,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Post-process response to ensure therapeutic value
        processed_response = self.post_process_response(response)
        return processed_response

    def prepare_therapeutic_prompt(self, user_input, conversation_history):
        """Prepare context-aware therapeutic prompt"""
        system_prompt = """You are a supportive and empathetic listener trained to help people with mental health challenges. 
        Focus on validation, active listening, and suggesting healthy coping strategies. 
        Never provide medical advice or diagnosis. Always encourage professional help when needed."""
        
        conversation_context = "\n".join(conversation_history[-5:])  # Keep last 5 exchanges for context
        
        return f"{system_prompt}\n\nConversation history:\n{conversation_context}\n\nUser: {user_input}\nAssistant:"

    def post_process_response(self, response):
        """Ensure response maintains therapeutic value and safety"""
        # Remove any potential harmful suggestions
        response = re.sub(r'you should|you must|you need to', 'you might consider', response)
        
        # Add appropriate disclaimers when needed
        if any(word in response.lower() for word in ['anxiety', 'depression', 'diagnosis']):
            response += "\n\nPlease note: This is supportive listening only. For professional help, please consult a licensed mental health professional."
        
        return response

    def suggest_coping_strategy(self, emotion):
        """Suggest appropriate coping strategies based on emotional state"""
        strategies = {
            "anxiety": self.techniques["breathing"],
            "overwhelmed": self.techniques["grounding"],
            "negative thoughts": self.techniques["reframing"]
        }
        return strategies.get(emotion, self.techniques["breathing"])

def main():
    chatbot = MentalHealthChatbot()
    conversation_history = []
    
    print("Mental Health Support Chat (Type 'exit' to end)")
    print("Note: This is a supportive tool and not a replacement for professional help.")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            break
            
        response = chatbot.generate_response(user_input, conversation_history)
        conversation_history.extend([user_input, response])
        print("\nBot:", response)

if __name__ == "__main__":
    main()