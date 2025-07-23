import gradio as gr
from run_agent import process_user_query
import asyncio


def add_user_message(message: str, history: list):
    """
    Add user message to chat history immediately

    :param message: user message
    :param history: chat history
    :return: updated chat history
    """
    if not message.strip():
        return history, ""
    
    # Add user message with empty bot response
    history.append([message, None])
    return history, ""


def get_bot_response(history: list):
    """
    Get bot response for the last user message

    :param history: chat history
    :return: updated chat history
    """
    if not history or history[-1][1] is not None:
        return history
    
    # Get the last user message
    user_message = history[-1][0]
    
    try:
        # Run the async function
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Get the response
        response = loop.run_until_complete(process_user_query(user_message))
        
        # Update with actual response
        history[-1][1] = response
        
        return history
        
    except Exception as e:
        error_message = f"I encountered an error: {str(e)}. Please try again."
        # Update with error response
        history[-1][1] = error_message
        return history


def clear_chat():
    """Clear the chat history and restore welcome message"""
    return get_welcome_message(), ""


def get_welcome_message():
    """Get the initial welcome message"""
    return [[
        None, 
        "Hello! I'm your AI travel assistant. I can help you with:\n\n"
        "🌤️ **Weather information** - Get current conditions and forecasts\n"
        "🏨 **Hotel bookings** - Find and book accommodations\n"
        "📍 **Places to visit** - Discover attractions and points of interest\n"
        "🗓️ **Trip planning** - Create detailed itineraries\n\n"
        "What would you like to know about your travel plans?"
    ]]


# Create the Gradio interface
with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue"), title="AI Travel Assistant") as ui:
    gr.Markdown("# ✈️ AI Travel Assistant 🌍")

    with gr.Row():
        with gr.Column(scale=3):
            # Main chat interface
            chatbot = gr.Chatbot(
                value=get_welcome_message(),
                height=600,
                show_copy_button=True,
                avatar_images=(
                    "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
                    "https://cdn-icons-png.flaticon.com/512/2990/2990507.png"
                ),
                bubble_full_width=False,
                show_label=False
            )

            # Message input
            msg = gr.Textbox(
                placeholder="Ask me about weather, hotels, places to visit, or trip planning...",
                container=False,
                scale=7,
                show_label=False,
                lines=1
            )

            with gr.Row():
                submit_btn = gr.Button("Send ✈️", variant="primary", scale=2)
                clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary", scale=1)

        with gr.Column(scale=1):
            with gr.Accordion("🎯 Available Services", open=True):
                gr.Markdown("""
                ✅ **Booking Services**  
                Find and book accommodations, get detailed information including photos, reviews, and booking URLs

                ✅ **Weather Services**  
                Get weather forecasts and conditions for any destination

                ✅ **Places & Attractions**  
                Discover points of interest and tourist attractions

                ✅ **Trip Planning**  
                Create detailed itineraries and travel plans
                """)

            with gr.Accordion("💡 Quick Tips", open=True):
                gr.Markdown("""
                **Example queries:**
                - "What's the weather in Tokyo next week?"
                - "Find hotels in Paris under $200/night"
                - "What are the top attractions in Rome?"
                - "Plan a 3-day trip to Barcelona"
                - "I need help booking a family vacation"
                - "What should I pack for a trip to Iceland?"
                """)

    # Set up event handlers
    # Send button functionality
    submit_btn.click(
        add_user_message,
        inputs=[msg, chatbot],
        outputs=[chatbot, msg],
        queue=True
    ).then(
        get_bot_response,
        inputs=[chatbot],
        outputs=[chatbot],
        queue=True
    )

    # Enable Enter key to send message
    msg.submit(
        add_user_message,
        inputs=[msg, chatbot],
        outputs=[chatbot, msg],
        queue=True
    ).then(
        get_bot_response,
        inputs=[chatbot],
        outputs=[chatbot],
        queue=True
    )

    # Clear chat button
    clear_btn.click(
        clear_chat,
        outputs=[chatbot, msg],
        queue=False
    )


if __name__ == "__main__":
    ui.launch()
