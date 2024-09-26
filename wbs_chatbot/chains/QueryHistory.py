import os
import json


class QueryHistory:
    def __init__(self, chat_model=None):
        self.file_path = os.path.join(os.path.dirname(__file__), 'data', 'query_history.json')
        self.history = self._load_history()
        self.chat_model = chat_model

    def _load_history(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = f.read().strip()
                if not data:
                    return []
                return json.loads(data)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_query(self, user_query, ai_response):
        self.history.append({"query": user_query, "response": ai_response})
        self._save_history()

    def _save_history(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=4)

    def get_previous_queries(self, user_query, analyze_with_ai=False):
        matching_queries = [entry for entry in self.history if user_query.lower() in entry['query'].lower()]

        if analyze_with_ai and self.chat_model:
            # Create a prompt to analyze matching queries
            prompt = (
                    f"Analyze the following past queries and their responses for trends and relevant context:\n\n" +
                    "\n".join(
                        [f"Query: {entry['query']}\nResponse: {entry['response']}\n" for entry in matching_queries])
            )

            response = self.chat_model.invoke(prompt)
            return response.content.strip()

        return matching_queries
