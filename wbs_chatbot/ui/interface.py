import streamlit as st
from wbs_chatbot.chains.chat_rag_chain import ProductRecommender
import re


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
            margin-right: 0px;
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
            flex-direction: column;
        }
        </style>
        """

    st.markdown(bubble_css, unsafe_allow_html=True)

    # session state for storing chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # welcome message only once when the chat history is empty
    if not st.session_state.chat_history:
        st.session_state.chat_history.append({"question": None, "response": "Добредојдовте! Како можам да ви помогнам ?"})

    for chat in st.session_state.chat_history:
        if chat["question"]:
            st.markdown(
                f'<div class="chat-container"><div class="chat-bubble user-bubble">{chat["question"]}</div></div>',
                unsafe_allow_html=True)
        if chat["response"]:
            st.markdown(
                f'<div class="chat-container"><div class="chat-bubble bot-bubble">{chat["response"]}</div></div>',
                unsafe_allow_html=True)

    prompt = st.chat_input("Прашај тука ...")

    if prompt:
        # Display the user's question immediately
        st.session_state.chat_history.append({"question": prompt, "response": ""})
        st.markdown(
            f'<div class="chat-container"><div class="chat-bubble user-bubble">{prompt}</div></div>',
            unsafe_allow_html=True)

        # Get recommended products
        try:
            recommended_products = recommender.recommend_products(prompt, "neptun-products")
            clean_recommended_products = [re.sub(r'\*\*', '', product) for product in recommended_products]
            formatted_response = "<br>".join(clean_recommended_products) if clean_recommended_products else "No products found."
        except Exception as e:
            formatted_response = f"An error occurred: {e}"

        # update response in the chat history
        st.session_state.chat_history[-1]["response"] = formatted_response

        # display response
        st.markdown(
            f'<div class="chat-container"><div class="chat-bubble bot-bubble">{formatted_response}</div></div>',
            unsafe_allow_html=True)


if __name__ == "__main__":
    main()
