from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "extract_note_signals_v1.py"
SPEC = importlib.util.spec_from_file_location("extract_note_signals_v1", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class NoteSignalExtractionTests(unittest.TestCase):
    def test_detects_hardship_income_and_collections(self) -> None:
        note = (
            "Customer reported financial hardship after reduced income. "
            "Previous payment arrangement broke and collections review was requested."
        )
        signals = MODULE.extract_signals_from_text(note)

        self.assertEqual(signals["hardship_signal"], 1)
        self.assertEqual(signals["income_shock_signal"], 1)
        self.assertEqual(signals["arrangement_break_signal"], 1)
        self.assertEqual(signals["collections_signal"], 1)

    def test_no_keyword_note_has_zero_score(self) -> None:
        note = "Account contact completed. Routine queue follow-up set for next billing cycle."
        signals = MODULE.extract_signals_from_text(note)
        score = MODULE.compute_note_signal_score(signals)

        self.assertEqual(sum(signals.values()), 0)
        self.assertEqual(score, 0.0)


if __name__ == "__main__":
    unittest.main()
