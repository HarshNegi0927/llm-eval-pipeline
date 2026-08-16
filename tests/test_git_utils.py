"""Tests detect_changed_prompt_versions against a real (throwaway) git
repo — this is the one place in the project that shells out to git, so
it's worth testing against actual git behavior rather than mocking
subprocess.
"""
import subprocess

from src.git_utils import detect_changed_prompt_versions


def _run(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def _init_repo(repo):
    repo.mkdir()
    _run(["git", "init", "-b", "main"], repo)
    _run(["git", "config", "user.email", "test@test.com"], repo)
    _run(["git", "config", "user.name", "Test"], repo)


def test_detects_a_newly_added_prompt_version(tmp_path):
    repo = tmp_path / "repo"
    _init_repo(repo)

    prompts_dir = repo / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "v1.yaml").write_text("version_id: v1\n")
    _run(["git", "add", "."], repo)
    _run(["git", "commit", "-m", "initial"], repo)

    _run(["git", "checkout", "-b", "feature"], repo)
    (prompts_dir / "v2.yaml").write_text("version_id: v2\n")
    _run(["git", "add", "."], repo)
    _run(["git", "commit", "-m", "add v2"], repo)

    versions = detect_changed_prompt_versions("main", repo_dir=repo)

    assert versions == ["v2"]


def test_returns_empty_list_when_no_prompts_changed(tmp_path):
    repo = tmp_path / "repo"
    _init_repo(repo)

    (repo / "README.md").write_text("hello")
    _run(["git", "add", "."], repo)
    _run(["git", "commit", "-m", "initial"], repo)

    _run(["git", "checkout", "-b", "feature"], repo)
    (repo / "README.md").write_text("hello world")
    _run(["git", "add", "."], repo)
    _run(["git", "commit", "-m", "update readme"], repo)

    versions = detect_changed_prompt_versions("main", repo_dir=repo)

    assert versions == []


def test_detects_multiple_changed_prompt_versions(tmp_path):
    repo = tmp_path / "repo"
    _init_repo(repo)

    prompts_dir = repo / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "v1.yaml").write_text("version_id: v1\n")
    _run(["git", "add", "."], repo)
    _run(["git", "commit", "-m", "initial"], repo)

    _run(["git", "checkout", "-b", "feature"], repo)
    (prompts_dir / "v2.yaml").write_text("version_id: v2\n")
    (prompts_dir / "v3.yaml").write_text("version_id: v3\n")
    _run(["git", "add", "."], repo)
    _run(["git", "commit", "-m", "add v2 and v3"], repo)

    versions = sorted(detect_changed_prompt_versions("main", repo_dir=repo))

    assert versions == ["v2", "v3"]


def test_ignores_changes_outside_prompts_directory(tmp_path):
    repo = tmp_path / "repo"
    _init_repo(repo)

    prompts_dir = repo / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "v1.yaml").write_text("version_id: v1\n")
    _run(["git", "add", "."], repo)
    _run(["git", "commit", "-m", "initial"], repo)

    _run(["git", "checkout", "-b", "feature"], repo)
    (repo / "src_notes.txt").write_text("unrelated change")
    _run(["git", "add", "."], repo)
    _run(["git", "commit", "-m", "unrelated"], repo)

    versions = detect_changed_prompt_versions("main", repo_dir=repo)

    assert versions == []
