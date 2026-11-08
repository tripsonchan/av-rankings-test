# av-rankings-test — one-off GitHub Actions fetch test

One-off test only. Read-only: opens 6 public ranking pages, records HTTP
status / title / Turnstile indicators / extracted entries into
`fetch-result.json`. No login, no playback, no video download, no paid
service, no proxy, no schedule.

## Run once

1. Actions tab → "Test fetch rankings (one-off)" → Run workflow → Run workflow.
2. Wait for the run to finish, open it, download the `fetch-result` artifact
   and read `fetch-result.json`.
3. Pass/fail (agreed before the run): if ≥2 of the 6 pages are 403 or still
   show Turnstile, the route is unstable — stop. Only if all 6 return 200,
   no Turnstile, and the extracted top codes match the 2026-11-08 baseline
   does it count as working.

Baseline top codes (2026-11-08): MissAV weekly DLDSS-578, new DLDSS-570,
actress 瀬户环奈; Jable weekly DLDSS-555, new SNOS-483, actress 仲間あずみ.
