"""Publish the completed hosted runs into the deck; no network calls."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def replace_section(text, name, content):
    start, end = f'<!-- {name}:start -->', f'<!-- {name}:end -->'
    before, rest = text.split(start, 1)
    _, after = rest.split(end, 1)
    return before + start + '\n' + content + '\n' + end + after


def render():
    rows, notes = [], []
    total_cost = 0
    models = [
        ('gemma4-26b', 'Gemma 4 26B', 'DeepInfra'),
        ('qwen38-27b', 'Qwen 3.8 27B', 'DeepInfra'),
        ('haiku55', 'Claude Haiku 5.5', 'Anthropic'),
    ]
    for slug, name, provider in models:
        run = json.loads((ROOT / f'bench/results/openrouter-{slug}.json').read_text())
        assert run['status'] == 'complete' and len(run['questions']) == 29 and len(run['speed_runs']) == 3
        requests = [run['smoke'], *run['questions'], *run['speed_runs']]
        assert all(r['metadata']['provider'] == provider for r in requests)
        rc = sum(q['correct'] for q in run['questions'])
        s = run['summary']
        assert rc == s['correct']
        quant = run['endpoint']['quantization']
        precision = 'API' if quant == 'unknown' else quant.upper()
        sec = f"{s['avg_seconds_per_question']:.1f} s"
        first = f"{s['median_time_to_first_text_s']:.2f} s"
        cost = s['reported_cost_usd']
        total_cost += cost
        question_cost = sum(q['usage']['cost'] for q in run['questions'])
        rows.append(f'<tr><td><b>{name}</b></td><td>{provider}</td><td>{precision}</td><td>${question_cost:.4f}</td></tr>')
        notes.append(f'{name}: hosted {rc}/29; average answer {sec}, median first text {first}; question-only cost ${question_cost:.6f}. Timings include network. Output rate {s["median_completion_tokens_per_total_second"]:.1f} tokens per total request second.')
    cost_note = f'All three hosted runs cost ${total_cost:.3f} in total, including smoke tests and speed measurements.'
    return '\n'.join(rows), cost_note, ' '.join(notes)


def main():
    rows, cost_note, notes = render()
    p = ROOT / 'index.html'
    text = replace_section(p.read_text(), 'hosted-rows', rows)
    text = replace_section(text, 'hosted-cost', cost_note)
    # Notes are text within an HTML template so they remain inspectable in the source.
    text = replace_section(text, 'hosted-notes', notes + ' Both open-weight models hit the output cap on Q16. Gemma also failed coding Q25 and Q28. Haiku 5.5 failed logic Q9. All requests used pinned providers with no retries or fallbacks. Qwen had a nonzero endpoint health status at preflight but all requests completed. These are deployment comparisons with different precision and engines, not isolated hardware measurements.')
    p.write_text(text)


if __name__ == '__main__':
    main()
