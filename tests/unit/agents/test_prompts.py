import unittest
from unittest.mock import patch

from app.agents.prompt.coordinator.router import ROUTER_PROMPT
from app.agents.prompt.specialist.education import EDUCATION_PROMPT
from app.agents.prompt.specialist.faq import FAQ_PROMPT
from app.core.config import config


class TestAgentPrompts(unittest.TestCase):
    def test_should_expose_every_router_intent(self):
        with patch.object(config, "TIMEZONE_REGION", "America/Sao_Paulo"):
            prompt = ROUTER_PROMPT()

        for intent in ("financial", "schedule", "notes", "faq", "education"):
            self.assertIn(f"{intent}: true|false", prompt)

    def test_should_route_financial_education_as_refer(self):
        with patch.object(config, "TIMEZONE_REGION", "America/Sao_Paulo"):
            prompt = ROUTER_PROMPT()

        self.assertIn("O que são juros compostos?", prompt)
        self.assertIn("education: true", prompt)
        self.assertIn("flow = REFER", prompt)

    def test_should_keep_product_faq_separate_from_financial_education(self):
        with patch.object(config, "TIMEZONE_REGION", "America/Sao_Paulo"):
            faq_prompt = FAQ_PROMPT()
            education_prompt = EDUCATION_PROMPT()

        self.assertIn("funcionamento", faq_prompt)
        self.assertIn("do Assessor.AI", faq_prompt)
        self.assertIn("faq_retriever", faq_prompt)
        self.assertIn("education_retriever", education_prompt)
        self.assertIn("Nunca recomendar a compra, venda ou manutenção", education_prompt)


if __name__ == "__main__":
    unittest.main()
