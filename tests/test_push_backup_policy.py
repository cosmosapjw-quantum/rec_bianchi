from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/push_backup.sh"


def test_backup_branch_and_pr_title_are_not_pinned_to_historical_v045() -> None:
    text = SCRIPT.read_text()
    assert "v045" not in text.lower()
    assert "date -u" in text
    assert "current durable stage" in text.lower()
