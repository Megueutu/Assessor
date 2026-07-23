import os
import subprocess
import sys
import unittest
from pathlib import Path
from uuid import uuid4

from tests.integration.helpers import (
    discover_api_keys,
    require_environment,
    workflow_tests_enabled,
)


@unittest.skipUnless(
    workflow_tests_enabled(),
    "Smoke test do workflow desabilitado.",
)
class TestAssessorFlow(unittest.TestCase):
    def test_should_answer_direct_message_through_complete_graph(self):
        environment = require_environment(
            "GEMINI_API_KEY",
            "MONGODB_DB",
        )
        mongodb_uri = (
            os.getenv("MONGODB_URI", "").strip()
            or os.getenv("MONGODB_LOCAL", "").strip()
        )
        if not mongodb_uri:
            self.skipTest("Configure MONGODB_URI ou MONGODB_LOCAL.")

        groq_keys = discover_api_keys("GROQ_API_KEY")
        if not groq_keys:
            self.skipTest("Configure ao menos uma GROQ_API_KEY.")

        project_root = Path(__file__).resolve().parents[3]
        process_environment = os.environ.copy()
        process_environment.update({
            "GEMINI_API_KEY": environment["GEMINI_API_KEY"],
            "GROQ_API_KEY": groq_keys[0],
            "MONGODB_URI": mongodb_uri,
            "MONGODB_DB": environment["MONGODB_DB"],
            "FAQ_PDF_PATH": os.getenv(
                "FAQ_PDF_PATH",
                str(project_root / "data/documents/faq.pdf"),
            ),
            "EDUCATION_DOCUMENTS_PATH": os.getenv(
                "EDUCATION_DOCUMENTS_PATH",
                str(project_root / "data/documents/education"),
            ),
            "TIMEZONE_REGION": os.getenv("TIMEZONE_REGION", "America/Sao_Paulo"),
        })
        for position, api_key in enumerate(groq_keys[1:], start=1):
            process_environment[f"GROQ_API_KEY_{position}"] = api_key

        script = (
            "from app.workflow.flow import assessor_flow;"
            f"answer=assessor_flow('Olá', '{uuid4().hex}');"
            "assert isinstance(answer, str) and answer.strip();"
            "print('workflow-smoke: ok')"
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=project_root,
            env=process_environment,
            capture_output=True,
            text=True,
            timeout=120,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("workflow-smoke: ok", result.stdout)


if __name__ == "__main__":
    unittest.main()
