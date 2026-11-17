# Reel tooling: long-form episode to daily clips

What turns a Beyond the Brand episode into the week's captioned reels and their Metricool posts.
The cloud workspace is wiped between sessions, so this folder is the copy that survives. Start each
new episode by copying the latest `epNN/` folder and changing the tables at the top of `caps.py` and `posts.py`.

The spec these scripts implement lives in the project doc `social/clip-engine.md`. Rod approved it on the
Episode 1 reels (Nov 9, 2026).

## Per episode, in order

1. **Source.** Rod's Mac: `Documents/BD/Rod Brinson/Podcast Episodes`.
   - `Final Videos/` holds the finished episode. `Final Clips/` holds the clean 9:16 cuts with Rod's thumbnail end card.
   - Stage the clips into the workspace as `wm/src/c1.mp4 ... c6.mp4`, then `ffmpeg -vn -ac 1 -ar 16000` each to `wm/aud/cN.wav`.
2. **Transcribe** with word times: `python3 -I tx.py <model_dir> <stub_dir> aud/cN.wav tx/cN.jsonl`.
   - Model: faster-whisper small, int8, from npm `@skillninja/shortmovie-telop-model-p0..p3` (cat the four parts into `model.bin`).
   - `pip install --break-system-packages --no-deps faster-whisper ctranslate2 tokenizers huggingface_hub tqdm`, plus an empty `av/__init__.py` stub.
3. **Check the words against YouTube's own transcript** of the episode (open the watch page, Show transcript). Two listeners catch what one misses.
   Put every fix in `EDITS` in `caps.py`. `probe.py` re-listens to a short slice when the two disagree.
4. **Find the episode's own cards** in each clip: `python3 cards.py src/cN.mp4`. Where a card shows the exact words he is reading
   (a step title, a scripture), list that stretch under `mute` so the captions don't repeat the card.
5. **Captions and hook card:** `python3 caps.py c1 ... c6` writes `ass/cN.ass` and `ass/cN_hook.png`. Read every page it prints.
6. **Render:** `python3 render.py c1 ... c6`. About two minutes of render per minute of clip on two cores.
   - To change only the sound on reels that are already rendered: `python3 render.py --swap-audio RENDERED_DIR OUT_DIR c1 ... c6`.
     The picture is copied, so it takes under a minute for all six.
7. **Check:** `frames.py` for contact sheets, loudness near -14.4 LUFS, true peak under -0.2 dBFS.
   `verify_swap.py OLD_DIR NEW_DIR` confirms a sound swap left the picture alone and shows how quiet the pauses are.
8. **Host:** copy to `2026-MM/reels/epNN-clipNN.mp4`, commit, push. Metricool copies the file when the post is created.
   - Replacing a reel under the same name: the `main` raw link stays cached for about five minutes, so give Metricool the commit link.
     `REELS_REF=<commit sha> python3 posts.py payloads <day>` does that.
9. **Posts:** `python3 posts.py check`, then `python3 posts.py payloads <day>` prints the `date` and `info` for each
   `createScheduledPost` call (blogId 6295498). `python3 posts.py sheet out.md` writes the captions sheet for Rod.
   - To change a post that is already scheduled, use `updateScheduledPost` with the post's current `id` and `uuid` from
     `getScheduledPosts` and the same `info`. The update replaces the whole post and gives it a new id.

## The look (measured from the Episode 1 reels)

- Hook card: white, black Anton, 12px corners, type as large as fits 900px wide, card top at y=112, on screen 0 to 5 seconds. Cover frame at 1.5s.
- Captions: Anton 118 (ASS size), white, 7px black outline, the spoken word in orange `#f16b2e`. Key words in Instrument Serif italic 150, teal `#00adb2`.
  Up to three words a page, broken on natural phrase edges. Bottom edge at y=1380 so they clear the episode's cards, which start at y=1400.
- Progress bar: 14px orange over a dark track at the bottom edge. Everything added fades out with the clip's own crossfade into the end card.
- Music: none. Rod on Nov 17, 2026, after seeing the Episode 2 reels: "i dont liek the music anymore. lets do these clips without the music".
  `USE_MUSIC = False` in `render.py`. The old bed is still in the code behind that switch: Inspiring Hip-Hop Ambient (Nicolas T),
  -25 LUFS before ducking, sidechain 3:1 keyed by his voice.
- Loudness: his voice at about -14.4 LUFS integrated, limiter at -1 dBFS.

## Notes

- GitHub rejects files over 100MB. The render settings keep a 2:15 clip near 70MB.
- This repo is carrying about 250MB of new video a week. Metricool also accepts Google Drive links, which would take the video out of git.
