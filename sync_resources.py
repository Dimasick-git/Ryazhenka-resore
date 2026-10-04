"""Prepare verified release assets; publication requires --publish explicitly."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent

def gh(*args):
    return subprocess.check_output(['gh', *args], cwd=ROOT, text=True, encoding='utf8')

def digest(path):
    with path.open('rb') as source:
        return 'sha256:' + hashlib.file_digest(source, 'sha256').hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    staging = ROOT / 'staging'
    staging.mkdir(exist_ok=True)
    manifest_path = ROOT / 'resources.json'
    old = manifest_path.read_text('utf8') if manifest_path.exists() else '{}'
    manifest = {'upstreams': [], 'assets': []}
    seen = set()
    for source in json.loads(ROOT.joinpath('sources.json').read_text('utf8')):
        release = json.loads(gh('api', f"repos/{source['repository']}/releases/tags/{source['tag']}"))
        available = {a['name']: a for a in release['assets']}
        names = sorted(available) if source['assets'] == '*' else source['assets']
        manifest['upstreams'].append(dict(repository=source['repository'], releaseTag=source['tag'], releaseUrl=release['html_url'], publishedAt=release['published_at']))
        for name in names:
            if name in seen or Path(name).name != name or '/' in name or '\\' in name:
                raise ValueError(f'Invalid or duplicate asset: {name}')
            seen.add(name)
            asset = available[name]  # Missing required archives fail before publication.
            path = staging / name
            expected = asset.get('digest') or ''
            if not path.exists() or not expected or digest(path) != expected:
                temp = path.with_suffix(path.suffix + '.partial')
                request = urllib.request.Request(asset['browser_download_url'], headers={'User-Agent': 'Ryazhenka-Resources'})
                with urllib.request.urlopen(request, timeout=120) as response, temp.open('wb') as out:
                    while chunk := response.read(1024 * 1024): out.write(chunk)
                temp.replace(path)
            actual = digest(path)
            if path.stat().st_size != asset['size'] or (expected and actual != expected):
                raise ValueError(f'Size or SHA-256 mismatch: {name}')
            if name.endswith('.zip'):
                with zipfile.ZipFile(path) as archive:
                    if archive.testzip(): raise ValueError(f'Invalid ZIP: {name}')
                    for member in archive.namelist():
                        if member.startswith(('/', '\\')) or '..' in Path(member).parts:
                            raise ValueError(f'Unsafe ZIP path: {name}')
            manifest['assets'].append(dict(name=name, sourceUrl=asset['browser_download_url'], sourceTag=source['tag'], sourceDigest=expected, sourceUpdatedAt=asset['updated_at'], mirrorDigest=actual, mirrorSize=path.stat().st_size))
    text = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
    manifest_path.write_text(text, 'utf8')
    print(f"Verified {len(manifest['assets'])} archives.")
    if not args.publish: return
    repository = os.environ['GITHUB_REPOSITORY']
    try:
        remote = json.loads(gh('api', f'repos/{repository}/releases/tags/resources'))
    except subprocess.CalledProcessError:
        gh('release', 'create', 'resources', '--repo', repository, '--target', 'main', '--title', 'Ресурсы Ряженки', '--notes', 'Хоумбрю, моды и сохранения. Источники и SHA-256 — в resources.json.')
        remote = {'assets': []}
    remote_assets = {a['name']: a for a in remote['assets']}
    for asset in manifest['assets']:
        existing = remote_assets.get(asset['name'])
        if existing and existing.get('digest') == asset['mirrorDigest']: continue
        gh('release', 'upload', 'resources', str(staging / asset['name']), '--repo', repository, '--clobber')
    # Commit only after every required mirror asset has been uploaded.
    if old != text:
        gh('release', 'edit', 'resources', '--repo', repository, '--title', 'Ресурсы Ряженки', '--notes', 'Хоумбрю, моды и сохранения. Источники и SHA-256 — в resources.json.')
        subprocess.run(['git', 'config', 'user.name', 'Ryazhenka Resources Bot'], cwd=ROOT, check=True)
        subprocess.run(['git', 'config', 'user.email', 'actions@github.com'], cwd=ROOT, check=True)
        subprocess.run(['git', 'add', 'resources.json'], cwd=ROOT, check=True)
        subprocess.run(['git', 'commit', '-m', 'Синхронизировать ресурсы Ultra'], cwd=ROOT, check=True)
        subprocess.run(['git', 'push', 'origin', 'HEAD:main'], cwd=ROOT, check=True)

if __name__ == '__main__': main()
