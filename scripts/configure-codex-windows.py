from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / '.codex'
divisions = json.loads((ROOT / 'divisions.json').read_text(encoding='utf-8'))['divisions']
generated = ROOT / 'integrations' / 'codex' / 'agents'
installed = ROOT / '.codex' / 'agents'
generated.mkdir(parents=True, exist_ok=True)
installed.mkdir(parents=True, exist_ok=True)

def get_field(frontmatter, field):
    lines = frontmatter.splitlines()
    for i, line in enumerate(lines):
        if line.startswith(field + ': '):
            value = line[len(field) + 2:]
            for next_line in lines[i + 1:]:
                if re.match(r'^[ \t]+[^ \t]', next_line):
                    value += ' ' + next_line.lstrip(' \t')
                else:
                    break
            value = value.strip(' \t')
            if len(value) >= 2 and value[0] == value[-1] == '"':
                value = value[1:-1].replace('\\"', '"').replace('\\\\', '\\')
            elif len(value) >= 2 and value[0] == value[-1] == "'":
                value = value[1:-1].replace("''", "'")
            return value
    raise ValueError(f'Missing frontmatter field: {field}')

def quote(value):
    return json.dumps(value, ensure_ascii=False).replace(chr(127), '\\u007F')

catalog = []
seen = set()
for division in divisions:
    for path in sorted((ROOT / division).rglob('*.md')):
        original = path.read_text(encoding='utf-8')
        match = re.match(r'^---\n(.*?)\n---\n(.*)$', original, re.S)
        if not match:
            continue
        frontmatter, body = match.groups()
        body = body.rstrip('\n')
        name = get_field(frontmatter, 'name')
        description = get_field(frontmatter, 'description')
        slug = re.sub('[^a-z0-9]+', '-', name.lower()).strip('-')
        assert slug not in seen, f'Slug collision: {slug}'
        seen.add(slug)
        text = f'name = {quote(name)}\ndescription = {quote(description)}\ndeveloper_instructions = {quote(body)}\n'
        parsed = tomllib.loads(text)
        assert parsed == {'name': name, 'description': description, 'developer_instructions': body}
        output = (generated / (slug + '.toml'))
        output.write_bytes(text.encode('utf-8'))
        destination = installed / output.name
        assert not destination.exists() or destination.read_bytes() == output.read_bytes(), f'Existing customized agent left unchanged: {destination}'
        destination.write_bytes(output.read_bytes())
        assert tomllib.loads(destination.read_text(encoding='utf-8')) == parsed
        catalog.append({'name': name, 'slug': slug, 'division': division, 'description': description, 'source': path.relative_to(ROOT).as_posix(), 'profile': destination.relative_to(ROOT).as_posix(), 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})

assert catalog, 'No source agents found'
config_path = ROOT / '.codex' / 'config.toml'
if not config_path.exists():
    config_path.write_text('[agents]\nmax_concurrent_threads_per_session = 3\n', encoding='utf-8')
tomllib.loads(config_path.read_text(encoding='utf-8'))
(ROOT / 'AGENCY-CATALOG.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding='utf-8')
rows = ['# Agency Agents: local catalog', '', '| Agent | Division | Source |', '| --- | --- | --- |']
rows.extend('| ' + agent['name'].replace('|', '\\|') + ' | ' + agent['division'] + ' | [' + Path(agent['source']).name + '](' + agent['source'] + ') |' for agent in catalog)
(ROOT / 'AGENCY-CATALOG.md').write_text('\n'.join(rows) + '\n', encoding='utf-8')
report = {'installed': len(catalog), 'scope': 'project', 'profiles_directory': str(installed), 'conversion': 'Windows Python equivalent of upstream convert_codex using the same three fields and unmodified body', 'validation': 'All TOML profiles parsed; name, description and body round-tripped against source; installed files equal generated files.', 'divisions': dict(Counter(agent['division'] for agent in catalog)), 'live_codex_invocation_verified': False}
(BASE / 'install-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
