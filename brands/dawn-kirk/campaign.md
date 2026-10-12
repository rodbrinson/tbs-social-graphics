# The Corporate Advantage: social campaign (Oct 12 to 29, 2026)

Status as of Oct 12, 2026: launch post live today 5:15 PM ET, week 1 (Oct 13 to 19) scheduled and verified in Metricool, 31 entries PENDING. Week 2 (Oct 20 to 29) to be built for Rod's Monday Oct 19 approval.

## Door
- Primary, every post: https://dawnskirk.net/corporate-advantage/ (Kit form on the page, Zoom link by email)
- Event: Thu Oct 29, 7 PM ET, Zoom, free, one hour. Tagline "Outside wins begin with inside work." Credential line "HR Executive / Executive Coach."
- Per-network link handling: IG "Link in bio" (Dawn set the bio link Oct 12), hashtags in first comment. FB full URL in caption. LinkedIn no link in body, "Registration link is in the first comment," first comment carries the URL (built into make_schedule via `linkedin_link_in_comment`). Threads URL inline, under 500 chars, lowercase.

## Cadence
- One post a day, 6:45 AM ET. Dawn posts before 7:30 AM or after 5 PM only (Rod, Oct 12: "shes mindful not to appear like she is doing this side work during work hours").
- Launch exception: Oct 12 carousel at 5:15 PM ET.
- Final-day post Oct 29 stays at 6:45 AM (reminder), no evening post.

## Content map
| Date | Post | Format | Photo |
|---|---|---|---|
| Mon Oct 12, 5:15 PM | The promotion was decided before the meeting | Carousel, 9 slides, Microphone | cd_5218 cover, stage_blueprint proof, cd_5214 call |
| Tue Oct 13 | Credibility takes thirty years to build. Decide what you are there to say before you walk in. | Quote, full-bleed | cd_5157 |
| Wed Oct 14 | The Corporate Advantage call card | Call | ros_2440B4A2 |
| Thu Oct 15 | The feedback that stalls careers has no example attached (Can you give me an example?) | Carousel, 9, Microphone | cd_5403 cover, cd_5254 call |
| Fri Oct 16 | Leaders find their own facts. You inspect what you expect. | Quote, white | cd_5341 |
| Sat Oct 17 | Nobody taught me productivity. Raising three kids did. | Quote, full-bleed | cd_5282 |
| Sun Oct 18 | God is in control. That was never permission to sit still. | Quote, white | cd_5427 |
| Mon Oct 19 | Doing your job well is not good enough (network diversification) | Carousel, 9, Microphone | ros_4D863792 cover, cd_5170 call |

Photos used so far (do not repeat): cd_5157, 5170, 5214, 5218, 5254, 5282, 5341, 5403, 5427, ros_2440B4A2, ros_4D863792, stage_blueprint. Still unused in _social_picks: cd_5186, cd_5319, cd_5387, ros_1627AA9D, ros_D275B4BE. More frames available on Rod's Mac (Content Day 313, Roswell 17, Blueprint CR3 84 unprocessed).

## Design standard (brands/dawn-kirk/brand.json in rodbrinson/tbs-social-graphics)
- 1080 x 1350, JPG q86, hosted at raw.githubusercontent.com/rodbrinson/tbs-social-graphics/main/brands/dawn-kirk/2026-10/
- Light theme. Background #F7F9FA, ink #1F2527, teal #80B9C5 (lane line and rules only, never text), mauve #BB7297 (accent word, marker, badge, display size only), slate #686F73 kickers.
- Archivo Black title-case headlines, Barlow Condensed utility, Montserrat body, Playfair Display italic accents.
- Carousels: dashed lane along the bottom, phase carried across slides, mauve marker advancing. Truth and stall slides flip to ink. DK monogram bottom left (white on dark/photo, teal on light). No page numbers.
- Quote cards: standalone template, no lane line, mauve open-quote, name + credential line, DK bottom right. Alternate full-bleed photo and photo-over-white.
- Call cards: mauve badge, headline, title stack, date/time/free row, "Save your seat" line.

## Voice rules learned at the review gate (Rod, Oct 12)
- "you dont have to quote her exact.. just pull from what she has said to create other things that make sense." Fathom calls are source material; the quote bank is in claude/dawn-kirk-quote-bank.md.
- Never post anything that reads as self-protection, venting, insider complaint, or status management, even if verbatim. Rejected example: "If I say what I'm thinking in my head, I will ruin my credibility..." Rod: "she wont be looked at in terms of honor and executive status if she does this."
- Show all sides of Dawn: executive, coach, mom, wife, faith. "The idea is people continue to see her as an executive leader."
- Dawn-only on photos. Business and corporate quotes from well-known names are fine.
- No "not X, it's Y" antithesis. No em dashes.

## Approval
- Rod reviewed one carousel and one quote (Oct 12), approved week 1 in one pass.
- Weekly batches, Rod approves every Monday, until he grants no-approval weekly batches.

## Pipeline
- Repo: rodbrinson/tbs-social-graphics, brand folder brands/dawn-kirk. Photos gitignored (stay on Rod's Mac under Customers/Dawn/_social_picks).
- build.py --brand brands/dawn-kirk, make_schedule.py brands/dawn-kirk 2026-10, make_payloads.py brands/dawn-kirk --skip <sent ids>, then createScheduledPost per payload, verify with getScheduledPosts in 2 to 4 day windows.
- Metricool blogId 6297603, America/New_York. Metricool threw one 502 on a first attempt (Oct 12); retry succeeded.

## Week 2 plan (to build for Oct 19 approval)
- Oct 20 to 29, 10 posts. Dawn's own story carousel (Moment engine) lands Oct 27. Oct 28 and 29 are reminder call cards. Keep one Sunday faith quote (Oct 25). Candidate carousel ideas from the quote bank: documentation ("Just write it all down"), interview order and the 90-second answer, AI-proofing your role ("they're not going to tell you").
- After Oct 29: flip the door to the Aligned Executive Network Coaching Experience; second door the Heartbeat Leadership book.
