import os
from unittest import TestCase
from unittest.mock import patch

from app.core.config import Config, config
from app.workflow.startup import validate_api_keys


class TestStartup(TestCase):
    def tearDown(self):
        config.VALIDATED_GROQ_API_KEYS = None

    def test_should_discover_numbered_groq_keys_in_order(self):
        environment = {
            "GROQ_API_KEY_10": "key-10",
            "GROQ_API_KEY_2": "key-2",
            "GROQ_API_KEY": "key-main",
            "GROQ_API_KEY_BACKUP": "ignored",
        }

        with patch.dict(os.environ, environment, clear=True):
            keys = Config().GROQ_API_KEYS

        self.assertEqual(keys, ["key-main", "key-2", "key-10"])

    def test_should_keep_only_valid_groq_keys(self):
        config.VALIDATED_GROQ_API_KEYS = None
        groq_results = {"invalid-key": ValueError(), "valid-key": None}

        def groq_probe(api_key):
            error = groq_results[api_key]
            if error:
                raise error

        with (
            patch.dict(
                os.environ,
                {"GROQ_API_KEY_2": "invalid-key", "GROQ_API_KEY_10": "valid-key"},
                clear=True,
            ),
            patch.object(config, "GEMINI_API_KEY", "gemini-key"),
        ):
            result = validate_api_keys(
                groq_probe=groq_probe,
                gemini_probe=lambda _: None,
            )

        self.assertEqual(config.VALIDATED_GROQ_API_KEYS, ["valid-key"])
        self.assertEqual(result.invalid_groq_keys, ("GROQ_API_KEY_2",))

    def test_should_fail_when_all_groq_keys_are_invalid(self):
        config.VALIDATED_GROQ_API_KEYS = None
        gemini_was_tested = []

        with (
            patch.dict(os.environ, {"GROQ_API_KEY": "invalid-key"}, clear=True),
            patch.object(config, "GEMINI_API_KEY", "gemini-key"),
        ):
            with self.assertRaisesRegex(RuntimeError, "nenhuma chave Groq"):
                validate_api_keys(
                    groq_probe=lambda _: (_ for _ in ()).throw(ValueError()),
                    gemini_probe=lambda _: gemini_was_tested.append(True),
                )

        self.assertEqual(gemini_was_tested, [True])
