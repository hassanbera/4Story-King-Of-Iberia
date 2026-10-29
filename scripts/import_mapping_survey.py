"""Create corridor candidates from a local mapping session; no SQL writes."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

from navigation.survey import extract


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('session',type=Path)
    args=parser.parse_args()
    source=args.session/'walk.csv'
    if source.stat().st_size>128*1024*1024:
        raise ValueError('Split large mapping sessions before import')
    snapshot=source.read_bytes()
    result=extract(csv.DictReader(io.StringIO(snapshot.decode('utf-8-sig'))))
    result.update({'formatVersion':1,'sourceSha256':hashlib.sha256(snapshot).hexdigest(),
                   'runtimeModified':False,'requiresReviewBeforeActivation':True})
    target=args.session/'corridor-candidates.json'
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'samples':result['samples'],'candidateSegments':len(result['segments']),
                      'breakReasons':result['breakReasons'],'output':str(target)},indent=2))


if __name__=='__main__':
    main()
