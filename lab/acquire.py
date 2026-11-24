#!/usr/bin/env python3
"""Reproduce the immutable snapshots in a new directory. Never overwrite exports."""
import argparse, pathlib, subprocess, tarfile, tempfile
P=pathlib.Path
URL='https://git.drupalcode.org/project/drupal.git'
BASE='29b0a0b2256eb5ed27df6ec5e4e4e33142a717e8'
HEAD='fe4adb4f942385912bb3244b570afa475cadf3bd'
def run(*args): subprocess.run(args,check=True)
def main():
    p=argparse.ArgumentParser();p.add_argument('--before',default=BASE);p.add_argument('--after',default=HEAD);a=p.parse_args()
    if any(P(x).exists() for x in ('before','after')): p.error('Existing before/after directory: refusing to overwrite. Use a fresh directory.')
    if not P('drupal.git').exists(): run('git','init','--bare','drupal.git')
    for label,sha in [('before',a.before),('after',a.after)]:
        run('git','--git-dir=drupal.git','fetch','--depth=1',URL,sha+':refs/heads/'+label)
        actual=subprocess.check_output(['git','--git-dir=drupal.git','rev-parse','refs/heads/'+label],text=True).strip()
        if actual!=sha: raise RuntimeError('Commit mismatch')
        with tempfile.TemporaryFile() as f:
            subprocess.run(['git','--git-dir=drupal.git','archive',actual,'core/themes/default_admin'],stdout=f,check=True);f.seek(0)
            with tarfile.open(fileobj=f) as t: t.extractall(label,filter='data')
if __name__=='__main__': main()
