import unittest

from pydantic import ValidationError

from app.agents.contracts.router_decision import RouterDecision
from app.core.constants.agents import Agent
from app.core.constants.flow import Flow


class TestRouterContract(unittest.TestCase):
    def test_should_accept_education_refer_decision(self):
        decision = RouterDecision(
            flow=Flow.REFER,
            intent={
                Agent.FINANCIAL: False,
                Agent.SCHEDULE: False,
                Agent.NOTES: False,
                Agent.FAQ: False,
                Agent.EDUCATION: True,
            },
        )

        self.assertEqual(decision.flow, Flow.REFER)
        self.assertTrue(decision.intent[Agent.EDUCATION])
        self.assertIsNone(decision.answer)

    def test_should_reject_unknown_flow(self):
        with self.assertRaises(ValidationError):
            RouterDecision(flow="UNKNOWN", intent={})


if __name__ == "__main__":
    unittest.main()
