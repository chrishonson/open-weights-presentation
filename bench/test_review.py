"""Regressions for the completed, client-timed comparison and its presentation."""
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import publish_environments as env
from quiz import challenge_questions

ROOT = Path(__file__).resolve().parent.parent


def test_all_deployments_have_the_same_complete_challenge():
    digest = hashlib.sha256(json.dumps([p for _, p, _ in challenge_questions()]).encode()).hexdigest()
    files = [*env.R.glob('mac-venue-*-qa.json'), *env.R.glob('l40s-*.json'), *env.R.glob('openrouter-*.json')]
    count = 0
    for path in files:
        run = json.loads(path.read_text())
        if not run.get('questions'):
            continue
        count += 1
        assert run['status'] == 'complete', path.name
        assert run['settings']['prompt_sha256'] == digest, path.name
        assert [q['n'] for q in run['questions']] == list(range(1, 30)), path.name
        assert len(run['speed_runs']) == 3, path.name
        assert sum(q['correct'] for q in run['questions']) == run['summary']['correct'], path.name
        mean = sum(q['seconds'] for q in run['questions']) / 29
        assert abs(mean - run['summary']['avg_seconds_per_question']) < 1e-8, path.name
    assert count == 11


def test_current_document_outcomes_are_not_conflated():
    table = env.rows()
    lookup = {(r['model'], r['where']): r for r in table}
    # The shared-client run was stopped by macOS; the cell shows the Oct 22 native wait, marked as such.
    assert lookup['Qwen 3.8 27B', 'This Mac']['wait_262k'].endswith(env.NATIVE)
    assert lookup['Qwen 3.8 27B', 'Rented L40S']['wait_262k'] == 'too long'
    assert lookup['Qwen 3.8 27B', 'OpenRouter']['wait_262k'] == '27 s'
    assert lookup['Nemotron 3.5 Lightning', 'This Mac']['wait_262k'] == '13.7 min'
    assert lookup['Claude Haiku 5.5', 'OpenRouter']['wait_262k'] == '7 s'


def test_main_tables_and_notes_follow_the_current_data_and_order():
    html = (ROOT / 'index.html').read_text()
    for kind in ('answers', 'documents'):
        assert env.comparison(env.rows(), kind) in html
    titles = re.findall(r'<section class="slide" data-title="([^"]+)"', html)
    assert titles[titles.index('OpenRouter') + 1] == 'API economics'
    notes = json.loads(re.search(r'function notes\(\) \{\s*return (\{.*?\});', html, re.S).group(1))
    assert set(notes) == set(titles)
    assert all(notes.values())
    assert 'notes()[slides[i].dataset.title]' in html
    assert 'results pending' not in html.lower()


def test_openrouter_slide_matches_the_saved_runs():
    import publish_openrouter as publish
    rows, cost, notes = publish.render()
    html = (ROOT / 'index.html').read_text()
    assert rows in html and cost in html and notes in html
    assert html.count('data-title="OpenRouter"') == 1
