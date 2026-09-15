# Offline Pronunciation Download — product and UI states

## Placement and interaction model

Add one **Offline audio** item to the existing home menu, near Install. It opens a dedicated in-app screen using the current screen header, Back/Home, history, focus-return, manual scroll-restoration, reduced-motion, and modal-drawer contracts.

Do not place a 52 MB prompt in study, Listening, Verb Patterns, global search, completion screens, or the install prompt. Ordinary playback remains lazy and unchanged for learners who never open this screen.

The first implementation needs one card headed **Pronunciation audio**, one short explanation, one size line, one status/progress area, and at most one primary plus one secondary/destructive action. Native buttons are sufficient.

## State model

The UI is a projection of `{capability, manifest, reconciliation, queue, lastFailure}`. Cache reconciliation, not a persisted completed flag, determines counts.

| State | Meaning | Suggested visible content | Available action |
|---|---|---|---|
| Unsupported / unavailable | No usable Cache Storage, active service worker, or manifest | “Offline audio isn’t available in this browser right now. Pronunciation still works normally when available online.” | Retry check where meaningful; ordinary Back/Home |
| Checking cache | Capability exists; actual cache is being reconciled | “Checking downloaded pronunciation audio…”; indeterminate progress semantics | no download/remove action until settled |
| Not downloaded | 0 of current total valid | “Download all pronunciation audio so it works without an internet connection.” / “About 52 MB” | **Download audio** |
| Partially downloaded | 1…total−1 valid; no active queue | “Download incomplete” / “1,842 of 3,621 available offline” | **Continue download**; **Remove offline audio** as secondary/destructive |
| Downloading | queue active | “Downloading pronunciation audio” / “1,842 of 3,621” / “51%” | **Pause** |
| Pausing | no new work; up to 3 in flight | “Pausing after current downloads…” | button disabled briefly; no focus move |
| Paused / interrupted | scheduling stopped normally or by lifecycle | same truthful partial count; optional “You can continue any time.” | **Continue download** |
| Complete | final reconciliation equals active manifest | “Pronunciation audio available offline” / “3,621 pronunciations downloaded” | **Remove offline audio** |
| Update available | active manifest grew; old valid files remain | “3,621 of 3,680 available offline” / “59 new pronunciations available” | **Update offline audio**; Remove secondary |
| Network failure | bounded fetch failure stopped scheduling | “Download paused because the audio couldn’t be reached. 1,842 of 3,621 are available offline.” | **Continue download** |
| Quota/storage failure | worker recovery failed, then reconciled | “There isn’t enough browser storage to finish. 1,842 of 3,621 are still available offline.” | **Try again** after freeing space; Remove secondary |
| Bad individual response | one or more URLs failed validation | “Download incomplete. 3,620 of 3,621 are available offline. One pronunciation couldn’t be downloaded.” | **Try again** |
| Removing | confirmed cache deletion in progress | “Removing downloaded pronunciation audio…” | controls disabled; do not focus elsewhere |
| Removal complete | worker acknowledged delete and reconciliation is zero | “Downloaded pronunciation audio removed. Pronunciations will be saved again as you play them online.” | **Download audio** |
| Removal failed | actual cache could not be deleted/reconciled | “Downloaded audio couldn’t be removed. Nothing else was changed.” | **Try again** |

“Interrupted” is not a separate durable storage state. On entry, reconcile and render partial/not-downloaded/complete. Session-only reason text can explain why scheduling stopped.

## Recommended first-release copy

Initial:

```text
Pronunciation audio

Download all pronunciation audio so it works without an internet connection.

About 52 MB

[ Download audio ]
```

Downloading:

```text
Downloading pronunciation audio

1,842 of 3,621
51%

[ Pause ]
```

Paused/interrupted:

```text
Download incomplete

1,842 of 3,621 available offline

[ Continue download ]
```

Complete:

```text
✓ Pronunciation audio available offline

3,621 pronunciations downloaded

[ Remove offline audio ]
```

Update:

```text
Offline pronunciation update available

3,621 of 3,680 available offline
59 new pronunciations available

[ Update offline audio ]
```

Storage caveat, shown as quiet supporting text rather than alarm copy:

```text
Your browser or device may remove downloaded website data when storage is low or site data is cleared. You can return here to check or download it again.
```

The checkmark is decorative reinforcement only; the text must carry complete meaning. Never say “permanently downloaded”, “always available”, or “downloads in the background”.

## Specific cold-offline pronunciation feedback

Current behavior for a manifest-mapped but uncached clip offline is:

1. `Audio(file)` fails after the network/cache miss;
2. browser speech synthesis is attempted;
3. if it speaks, the shared status says “Using your device's voice.”;
4. if unavailable/failing, the status says “Audio couldn't play. Check your connection, then try again.”

The existing message is intentionally network-neutral enough for online decode/server failures, but after this feature exists a more specific state can help when the app knows the canonical clip is absent from the reconciled cache:

> This pronunciation isn't downloaded for offline use.

Possible supporting action: “Connect to the internet and try again, or download pronunciation audio from Offline audio.”

Do not implement this in Phase 0. In Phase 2/3, preserve speech-synthesis fallback: if the device voice successfully speaks, do not replace that useful result with a terminal offline error. Do not rely on `navigator.onLine`; actual cache absence plus failed clip attempt is stronger evidence.

## Accessibility contract

- Use native `<button type="button">` controls; no clickable divs.
- Use native `<progress max="3621" value="1842">` or an equivalent element with `role="progressbar"`, `aria-valuemin="0"`, `aria-valuemax`, and `aria-valuenow`.
- Keep the numeric visible text separate and exact; percent is supplemental and rounded down or normally rounded consistently.
- The progress accessible name should be “Downloading pronunciation audio”; its value text can be “1,842 of 3,621, 51 percent”.
- One persistent `role="status" aria-live="polite" aria-atomic="true"` region should announce meaningful state changes.
- Do not announce all 3,621 increments. Update visible progress at a throttled cadence (for example every 10 files or ~1 second), and announce milestones such as start, each 10%, paused, failure, complete, and removed.
- Never move focus as progress changes, on pause completion, failure, or completion. The activated button retains focus if it remains; when its label/action changes, keep the same DOM control where practical.
- A confirmed destructive Remove can use the existing accessible modal/dialog pattern. Initial focus belongs on Cancel; Escape/cancel leaves cache untouched; focus returns to Remove.
- State must be expressed with heading/message/count/icon, not color alone.
- Respect the existing `prefers-reduced-motion` contract. Progress width may update without decorative animation; do not add pulsing/spinning requirements.
- Ensure 44px touch targets, large-text wrapping, high contrast, logical DOM/tab order, portrait/landscape safe areas, and no horizontal scrolling.
- VoiceOver must hear a stable screen heading, progress name/value, Pause/Continue state, errors, and completion without repeated chatter.

## State-transition rules

```text
open screen -> checking -> unsupported | not downloaded | partial | complete | update
not downloaded/partial/update -> downloading
downloading -> pausing -> partial
downloading -> network/storage/bad-response partial
downloading -> final checking -> complete | partial/update
partial/failure/update -> downloading
partial/complete/update -> confirm remove -> removing -> not downloaded | removal failed
manifest changes -> checking -> update or complete for the new active set
```

Any stale message from a prior session/queue must fail a generation-token check. Remove invalidates the active queue before deletion. A late acknowledgement cannot restore progress or complete state.

## Product invariants

- “Available offline” is all current canonical files valid in `popolsku-audio`.
- Percent is `valid present / current unique manifest total`, never scheduled/sent requests.
- A successful network fetch alone does not advance durable progress.
- Partial work is useful and retained.
- New releases add a delta; they do not reset or force full redownload.
- Remove clears all saved pronunciation, including naturally warmed clips, and says so before confirmation.
- Ordinary audio, fallback, Retry, Listening, Verb Patterns, search, content identity, and learning progress remain independent.
