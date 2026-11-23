"""Assemble immutable model payloads and browser sources from stable Git tags."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


def stable_versions(tags):
    return sorted((t for t in tags if re.fullmatch(r'v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', t)),
                  key=lambda t: tuple(map(int, t[1:].split('.'))), reverse=True)


def main():
    versions = stable_versions(git('tag', '--list').splitlines())
    if not versions:
        raise SystemExit('No stable release tags; leaving the published site unchanged.')
    output = ROOT / '_release_site'
    if output.exists():
        shutil.rmtree(output)
    output.mkdir()
    for name in ['assets', '_includes', '_layouts']:
        shutil.copytree(ROOT / name, output / name)
    shutil.copyfile(ROOT / '_config.yaml', output / '_config.yml')
    template = (ROOT / 'index.md').read_text()
    listings = {}
    with tempfile.TemporaryDirectory() as temporary:
        checkout = Path(temporary) / 'snapshot'
        subprocess.run(['git', 'clone', '--quiet', '--no-checkout', str(ROOT), str(checkout)], check=True)
        for version in [*versions, 'latest']:
            subprocess.run(['git', '-C', str(checkout), 'checkout', '--quiet', '--detach', git('rev-parse', ('origin/main' if version == 'latest' else version) + '^{commit}')], check=True)
            subprocess.run(['git', '-C', str(checkout), 'submodule', 'update', '--init', '--recursive'], check=True)
            listing = {}
            for source in sorted(checkout.rglob('*')):
                relative = source.relative_to(checkout)
                if any(part.startswith('.') for part in relative.parts) or not source.is_file():
                    continue
                if source.suffix not in {'.json', '.ttl'} and source.name != 'LICENSE':
                    continue
                target = output / version / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
                if version == versions[0]:
                    for alias in [output, output / 'stable']:
                        target_alias = alias / relative
                        target_alias.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(source, target_alias)
                if source.suffix in {'.json', '.ttl'}:
                    listing.setdefault(str(relative.parent), []).append(dict(path=relative.as_posix(), name=source.name, extension=source.suffix[1:].upper()))
            listings[version] = listing
    listings['stable'] = listings[versions[0]]
    for version in [None, 'stable', 'latest', *versions]:
        selected = version or 'stable'
        page = template.replace('layout: default', f'layout: default\nrelease: {selected}')
        (output / version if version else output).joinpath('index.md').write_text(page)
    data = output / '_data'
    data.mkdir()
    (data / 'releases.json').write_text(json.dumps(dict(versions=versions, listings=listings)))


if __name__ == '__main__':
    main()
