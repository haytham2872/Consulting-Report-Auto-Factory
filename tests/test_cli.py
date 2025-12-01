from typer.testing import CliRunner

from consulting_auto_factory import cli


def test_show_plan_monkeypatched(monkeypatch):
    runner = CliRunner()

    class DummyPlan:
        def model_dump(self):
            return {"title": "Test Plan", "objectives": [], "steps": []}

    monkeypatch.setattr(cli, "plan_only", lambda *args, **kwargs: DummyPlan())
    result = runner.invoke(cli.app, ["show-plan"])
    assert result.exit_code == 0
    assert "Test Plan" in result.output


def test_run_command_stub(monkeypatch):
    runner = CliRunner()

    def fake_run_pipeline(*args, **kwargs):
        return None

    monkeypatch.setattr(cli, "run_pipeline", fake_run_pipeline)
    result = runner.invoke(
        cli.app,
        [
            "run",
            "--input-dir",
            "data/input",
            "--brief-path",
            "config/business_brief.txt",
            "--reports-dir",
            "reports",
        ],
    )
    assert result.exit_code == 0
    assert "Reports written" in result.output
