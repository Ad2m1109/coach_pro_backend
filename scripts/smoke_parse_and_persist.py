"""Smoke test: parse example CSVs (from AI model repo) and persist to DB.

Run this script from the backend project root after setting DB env vars.
"""
import os
import sys
from database import get_db
from analysis_engine import parse_and_persist_results

AI_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'football-analyset-ai-model-main'))
PLAYER_CSV = os.path.join(AI_REPO, 'player_metrics.csv')
BALL_CSV = os.path.join(AI_REPO, 'ball_metrics.csv')

if not os.path.exists(PLAYER_CSV) or not os.path.exists(BALL_CSV):
    print('Sample CSVs not found in', AI_REPO)
    sys.exit(1)

# We'll create a temporary output dir and copy the CSVs there
import tempfile, shutil
with tempfile.TemporaryDirectory() as tmpdir:
    shutil.copy(PLAYER_CSV, os.path.join(tmpdir, 'player_metrics.csv'))
    shutil.copy(BALL_CSV, os.path.join(tmpdir, 'ball_metrics.csv'))

    # Get DB connection from get_db generator
    gen = get_db()
    conn = next(gen)
    try:
        summary = parse_and_persist_results(tmpdir, conn, match_id='')
        print('Persist summary:', summary)
    finally:
        try:
            next(gen)
        except StopIteration:
            pass

print('Smoke test completed')
