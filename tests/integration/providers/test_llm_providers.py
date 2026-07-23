import unittest

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_groq import ChatGroq

from tests.integration.helpers import (
    discover_api_keys,
    integration_tests_enabled,
    require_environment,
)


@unittest.skipUnless(
    integration_tests_enabled(),
    "Testes de integração desabilitados.",
)
class TestLLMProviders(unittest.TestCase):
    def test_should_invoke_gemini_and_generate_embedding(self):
        api_key = require_environment("GEMINI_API_KEY")["GEMINI_API_KEY"]
        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=api_key,
            request_timeout=15,
            retries=0,
        )
        embedding_model = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-2-preview",
            google_api_key=api_key,
        )

        response = model.invoke("Responda apenas OK.")
        vector = embedding_model.embed_query("integration test")

        self.assertTrue(response.content.strip())
        self.assertGreater(len(vector), 100)
        self.assertTrue(all(isinstance(value, float) for value in vector[:10]))

    def test_should_invoke_every_configured_groq_key(self):
        api_keys = discover_api_keys("GROQ_API_KEY")
        if not api_keys:
            self.skipTest("Configure ao menos uma GROQ_API_KEY.")

        for position, api_key in enumerate(api_keys, start=1):
            with self.subTest(key_position=position):
                response = ChatGroq(
                    model="llama-3.3-70b-versatile",
                    temperature=0,
                    groq_api_key=api_key,
                    timeout=15,
                    max_retries=0,
                ).invoke("Responda apenas OK.")

                self.assertTrue(response.content.strip())


if __name__ == "__main__":
    unittest.main()
