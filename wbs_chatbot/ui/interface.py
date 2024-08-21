import os
import streamlit as st
from wbs_chatbot.chains.chat_rag_chain import ProductRecommender
import re
import base64


def load_image_as_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


def main():
    recommender = ProductRecommender()

    st.set_page_config(page_title="Neptun", page_icon=":loudspeaker:", layout="centered")
    st.header("Прашај го Neptun :loudspeaker:")
    st.markdown("<hr style='margin-top: 0'>", unsafe_allow_html=True)

    bubble_css = """
        <style>
        .chat-bubble {
            padding: 10px;
            border-radius: 15px;
            margin: 10px;
            max-width: 80%;
            display: inline-block;
        }
        .user-bubble {
            text-align: right;
            align-self: flex-end;
            border-bottom-right-radius: 0;
            margin-left: 10px;
            background-color: #33383D;
        }
        .bot-bubble {
            align-self: flex-start;
            text-align: left;
            border-bottom-left-radius: 0;
            background-color: #284150;
        }
        .chat-container {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }
        .user-container {
            justify-content: flex-end;
            width: 100%;
        }
        .bot-container {
            justify-content: flex-start;
            width: 100%;
        }
        .avatar-container {
            width: 60px;
            height: 60px;
        }
        .chat-content {
            display: flex;
            align-items: center;
            justify-content: flex-end;
        }
        </style>
        """

    st.markdown(bubble_css, unsafe_allow_html=True)

    # Get the directory where the script is running
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct absolute paths to your avatars
    user_avatar_path = os.path.join(script_dir, "user_avatar.png")
    bot_avatar_path = os.path.join(script_dir, "bot_avatar.png")

    # Convert images to base64
    user_avatar = load_image_as_base64(user_avatar_path)
    bot_avatar = load_image_as_base64(bot_avatar_path)

    # session state for storing chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # welcome message only once when the chat history is empty
    if not st.session_state.chat_history:
        st.session_state.chat_history.append(
            {"question": None, "response": "Добредојдовте! Како можам да ви помогнам?"})

    for chat in st.session_state.chat_history:
        if chat["question"]:
            st.markdown('<div class="chat-container user-container">', unsafe_allow_html=True)
            st.markdown(
                f'<div class="chat-content"><div class="chat-bubble user-bubble">{chat["question"]}</div><img src="data:image/png;base64,{user_avatar}" width="60" style="margin-left:10px;" /></div>',
                unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        if chat["response"]:
            st.markdown('<div class="chat-container bot-container">', unsafe_allow_html=True)
            st.markdown(
                f'<div><img src="data:image/png;base64,{bot_avatar}" width="60" style="margin-right:10px;" /><div class="chat-bubble bot-bubble">{chat["response"]}</div></div>',
                unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    prompt = st.chat_input("Прашај тука ...")

    if prompt:
        # Display the user's question immediately
        st.session_state.chat_history.append({"question": prompt, "response": ""})
        st.markdown('<div class="chat-container user-container">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="chat-content"><div class="chat-bubble user-bubble">{prompt}</div><img src="data:image/png;base64,{user_avatar}" width="60" style="margin-left:10px;" /></div>',
            unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Get recommended products
        try:
            recommended_products = recommender.recommend_products(prompt, "neptun-products")
            clean_recommended_products = [re.sub(r'\*\*', '', product) for product in recommended_products]
            formatted_response = "<br>".join(
                clean_recommended_products) if clean_recommended_products else "No products found."
        except Exception as e:
            formatted_response = f"An error occurred: {e}"

        # update response in the chat history
        st.session_state.chat_history[-1]["response"] = formatted_response

        # display response
        st.markdown('<div class="chat-container bot-container">', unsafe_allow_html=True)
        st.markdown(
            f'<div><img src="data:image/png;base64,{bot_avatar}" width="60" style="margin-right:10px;" /><div class="chat-bubble bot-bubble">{formatted_response}</div></div>',
            unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
