class QueryHistory:
    def __init__(self):
        self.history = []

    def save_query(self, user_query, ai_response):
        self.history.append({"query": user_query, "response": ai_response})

    def get_previous_queries(self, user_query):
        return [entry for entry in self.history if user_query.lower() in entry['query'].lower()]
