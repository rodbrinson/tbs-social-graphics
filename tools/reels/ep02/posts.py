"""Episode 2 clip posts: captions per network, schedule, Metricool payloads, and a captions sheet for Rod.

usage: python3 posts.py payloads <day-index 0..5>   -> one JSON line per network for that day
       python3 posts.py sheet <out.md>              -> captions sheet
       python3 posts.py check                       -> length and style checks
"""
import json
import re
import sys

EP = 'https://www.youtube.com/watch?v=YkNW-ihYpQg'
HOST = 'https://raw.githubusercontent.com/rodbrinson/tbs-social-graphics/main/2026-11/reels'
TZ = 'America/New_York'
IG_CTA = 'The full episode is on YouTube. Search @rod.brinson'

# network -> time of day. Weekday slots are last week's; Tuesday's first three moved to the afternoon
# because the morning slots had passed when this was scheduled. Weekend slots follow last Saturday.
WEEKDAY = dict(threads='08:17', facebook='10:07', linkedin='10:52', youtube='16:03', instagram='17:13', tiktok='18:07')
WEEKEND = dict(threads='09:17', facebook='10:07', linkedin='10:52', youtube='16:03', instagram='16:43', tiktok='12:12')
TODAY = dict(threads='14:17', facebook='15:07', linkedin='14:52', youtube='16:03', instagram='17:13', tiktok='18:07')

DAYS = [
    dict(date='2026-11-17', dow='Tue', slots=TODAY, clip=1),
    dict(date='2026-11-18', dow='Wed', slots=WEEKDAY, clip=2),
    dict(date='2026-11-19', dow='Thu', slots=WEEKDAY, clip=3),
    dict(date='2026-11-20', dow='Fri', slots=WEEKDAY, clip=4),
    dict(date='2026-11-21', dow='Sat', slots=WEEKEND, clip=5),
    dict(date='2026-11-22', dow='Sun', slots=WEEKEND, clip=6),
]

CLIPS = {
    1: dict(
        name='The Day I Got Laid Off',
        title='I Got Laid Off by Email After 20 Years',
        tiktok_title='Laid off after 20 years',
        threads=(
            "20 years in corporate America... and it ended with an email.\n\n"
            "I already had a business doing six figures on the side, and I STILL had nights staring at the ceiling "
            "wondering how I was gonna make it. I even filled out a few job applications.\n\n"
            "If that's where you are right now, I made this episode for you!\n\n" + EP),
        facebook=(
            "February 6th, 2024. After 20 years in corporate America, I got laid off by email.\n\n"
            "Thank God I already had a business running on the side. But let me keep it real with you... months in, "
            "I was still up at night staring at the ceiling, wondering what the heck I was doing. I even filled out a "
            "few job applications, and I felt sick doing it, because I knew that's not what God had for me.\n\n"
            "If a layoff just hit you, or you can feel one coming, I walk you through seven things to do in this "
            "week's episode!\n\n"
            "Full episode: " + EP),
        linkedin=(
            "On February 6th, 2024, after 20 years in corporate America, I was laid off by email.\n\n"
            "I had a head start most people don't get. My business was already running on the side and doing six "
            "figures. And months later I was still lying awake, wondering how I was going to make it. I even filled "
            "out a few job applications in my lowest moments.\n\n"
            "I'm telling you that because a layoff will shake you, however prepared you think you are. If it just "
            "happened to you, or you can feel it coming, this week's episode walks through seven steps to take, in "
            "order.\n\n" + EP),
        youtube=(
            "20 years in corporate America, and it ended with an email. I already had a six-figure business on the "
            "side and I still had nights staring at the ceiling.\n\n"
            "Watch the full episode: " + EP + "\n\n"
            "#shorts #laidoff #layoffs #careerchange"),
        yt_tags=['laid off', 'layoff', 'laid off after 20 years', 'what to do after a layoff',
                 'corporate to entrepreneur', 'side business', 'Rod Brinson', 'Beyond the Brand'],
        instagram=(
            "20 years in corporate America... over in one email.\n\n"
            "I had a business doing six figures on the side and I STILL had nights staring at the ceiling, wondering "
            "how I was gonna make it. So if you're scared right now, you're in good company. I was scared too!\n\n"
            + IG_CTA),
        ig_tags='#laidoff #layoffs #corporatelife #careerchange #entrepreneurship #sidebusiness #faithandbusiness #beyondthebrand',
        tiktok=(
            "Laid off by email after 20 years. I had a six-figure side business and I was still scared. "
            "Full episode on my YouTube: @rod.brinson #laidoff #layoffs #corporatelife #careerchange #careertok"),
    ),
    2: dict(
        name='Replaced by AI, Then Called Back',
        title='Replaced by AI, Then Asked to Come Back',
        tiktok_title='Replaced by AI, then called back',
        threads=(
            "Fortune just reported on a survey from SHL. About 19% of U.S. workers who said AI replaced them got "
            "asked to come back.\n\n"
            "Companies are cutting, but they're finding out they cut too deep and they're calling people back.\n\n"
            "So hear me... a layoff is a business decision somebody made in a spreadsheet. Your worth didn't get "
            "decided in that meeting. Only God decides that!\n\n" + EP),
        facebook=(
            "I need you to hear this if AI has you nervous about your job.\n\n"
            "Fortune just reported on a survey from a company called SHL. About 19% of U.S. workers who said they "
            "were replaced by AI got asked to come back. Companies are cutting, but they're finding out they cut too "
            "deep.\n\n"
            "A layoff is a business decision that somebody made in a spreadsheet. I had to make one myself when I "
            "went full time with my company, so I know. Your worth didn't get decided in that meeting or in that "
            "email. Your worth can only be decided by God!\n\n"
            "Full episode: " + EP),
        linkedin=(
            "Fortune recently reported on a survey from SHL. About 19% of U.S. workers who said they were replaced "
            "by AI were later asked to come back.\n\n"
            "Companies are cutting, and some are finding out they cut too deep.\n\n"
            "I've been on both sides of this. I was laid off after 20 years in corporate America, and I had to make "
            "a layoff in my own company when I went full time. It is a business decision that somebody makes in a "
            "spreadsheet. Your worth was never on that spreadsheet.\n\n"
            "If a layoff is on your mind right now, this week's episode gives you seven steps to take: " + EP),
        youtube=(
            "Fortune reported on an SHL survey: about 19% of U.S. workers who said AI replaced them got asked to "
            "come back. A layoff is a business decision. Your worth didn't get decided in that meeting.\n\n"
            "Watch the full episode: " + EP + "\n\n"
            "#shorts #ai #layoffs #futureofwork"),
        yt_tags=['AI replacing jobs', 'replaced by AI', 'AI layoffs', 'layoffs 2026', 'laid off', 'future of work',
                 'Rod Brinson', 'Beyond the Brand'],
        instagram=(
            "About 19% of U.S. workers who said AI replaced them got asked to come back. That's from an SHL survey "
            "Fortune just reported on.\n\n"
            "Companies are cutting, and they're finding out they cut too deep. So hear me... a layoff is a business "
            "decision somebody made in a spreadsheet. Your worth can only be decided by God!\n\n"
            + IG_CTA),
        ig_tags='#ai #artificialintelligence #layoffs #laidoff #futureofwork #careerchange #knowyourworth #beyondthebrand',
        tiktok=(
            "About 19% of workers who said AI replaced them got asked to come back. A layoff doesn't decide your "
            "worth. Full episode on my YouTube: @rod.brinson #ai #layoffs #laidoff #futureofwork #careertok"),
    ),
    3: dict(
        name="Step 1: Don't Sign Anything Today",
        title="Laid Off? Don't Sign Your Severance Yet",
        tiktok_title="Don't sign your severance yet",
        threads=(
            "If you just got laid off and that severance paper is sitting in your email... don't sign it today.\n\n"
            "They're gonna want it back fast, and you're allowed to slow down and ask questions. You can even "
            "counter. I asked for more myself, and the worst they can do is say no.\n\n"
            "I'm not a lawyer, so get an employment attorney to look at it first!\n\n"
            "All seven steps: " + EP),
        facebook=(
            "Step one if you get laid off... don't sign anything today.\n\n"
            "When they hand you that severance agreement, they're gonna want it back pretty fast. You get to slow "
            "down. If you're 40 or older, federal law gives you at least 21 days to look it over, and 45 if it's a "
            "group layoff. That's the Older Workers Benefit Protection Act.\n\n"
            "You're allowed to ask questions too. Can my health coverage run longer? Can my end date move? I asked "
            "for more money and more benefits myself. The worst they can do is say no!\n\n"
            "I'm not a lawyer, so have an employment attorney look at yours. The other six steps are in the full "
            "episode: " + EP),
        linkedin=(
            "If a severance agreement lands in your inbox, the first step is simple. Don't sign it today.\n\n"
            "They will want it back quickly, and you are allowed to slow down. If you're 40 or older, federal law "
            "gives you at least 21 days to review it, 45 days in a group layoff, and 7 days to change your mind "
            "after you sign. That comes from the Older Workers Benefit Protection Act.\n\n"
            "You can also ask questions and counter. I asked for more money and more benefits when it happened to "
            "me. The worst they can do is say no.\n\n"
            "I'm not a lawyer, so have an employment attorney review yours before you sign. This is step one of "
            "seven in this week's episode: " + EP),
        youtube=(
            "Step 1 after a layoff: don't sign anything today. You're allowed to slow down, ask questions and "
            "counter. I'm not a lawyer, so have an employment attorney look at it.\n\n"
            "Watch the full episode for all 7 steps: " + EP + "\n\n"
            "#shorts #severance #laidoff #layoffs"),
        yt_tags=['severance package', 'severance negotiation', 'dont sign severance', 'laid off',
                 'what to do after a layoff', 'layoff advice', 'Rod Brinson', 'Beyond the Brand'],
        instagram=(
            "Laid off? Don't sign that severance paper today.\n\n"
            "They're gonna want it back fast, and you get to slow down. If you're 40 or older, federal law gives "
            "you at least 21 days to look it over. You can ask questions and you can counter... I asked for more "
            "myself. The worst they can do is say no!\n\n"
            "I'm not a lawyer, so get an employment attorney to look at yours. All seven steps are in the full "
            "episode on YouTube. Search @rod.brinson"),
        ig_tags='#severance #laidoff #layoffs #knowyourrights #careeradvice #corporatelife #jobloss #beyondthebrand',
        tiktok=(
            "Laid off? Don't sign the severance today. You can slow down, ask questions and counter. Not legal "
            "advice, so talk to an attorney. Full episode on my YouTube: @rod.brinson "
            "#severance #laidoff #layoffs #careeradvice #careertok"),
    ),
    4: dict(
        name='The Company That Laid Me Off Hired My Company',
        title='The Company That Laid Me Off Hired My Company',
        tiktok_title='They hired my company',
        threads=(
            "The same company that laid me off hired MY company.\n\n"
            "A lady I connected with before I left went quiet on me for six months. Then she liked one of my posts, "
            "I DM'd her right then, and a 20-minute Zoom turned into them needing the same kind of work I used to "
            "do for them as an employee.\n\n"
            "My W-2 turned into a 1099!\n\n"
            "The whole story: " + EP),
        facebook=(
            "The same company that laid me off hired MY company. Did y'all hear that?\n\n"
            "I made a connection with a lady there before I left, and I stayed connected to her. She went quiet for "
            "six months. Then one day she liked something I posted on LinkedIn, so I DM'd her right then. A "
            "20-minute Zoom call turned into her asking if my company knew how to use Canva.\n\n"
            "Come to find out, the whole organization was moving to Canva and they needed people trained and "
            "templates built. That's the same kind of work I did for them when I was on payroll. My W-2 turned "
            "into a 1099!\n\n"
            "Full episode: " + EP),
        linkedin=(
            "The company that laid me off later hired my company.\n\n"
            "Before I left, I had built a relationship with a colleague there, and I stayed in touch after the "
            "layoff. She went quiet for six months. Then she liked one of my LinkedIn posts, I sent her a message, "
            "and a 20-minute Zoom call turned into a question about whether my team knew Canva.\n\n"
            "The organization was moving to Canva company-wide. They needed people trained and templates built, "
            "the same kind of work I had done for them as an employee. My W-2 turned into a 1099, and I became an "
            "official vendor.\n\n"
            "I was only posting to keep growing my brand, and she saw it. Stay connected to your people. The full "
            "story is in this week's episode: " + EP),
        youtube=(
            "A contact went quiet for six months. Then one LinkedIn post and one DM turned my W-2 into a 1099.\n\n"
            "Watch the full episode: " + EP + "\n\n"
            "#shorts #laidoff #entrepreneurship #networking"),
        yt_tags=['laid off', 'start a business after layoff', 'corporate to entrepreneur', 'W2 to 1099',
                 'networking', 'LinkedIn', 'Rod Brinson', 'Beyond the Brand'],
        instagram=(
            "The same company that laid me off hired MY company.\n\n"
            "A lady I stayed connected to after I left went quiet for six months. Then she liked one of my posts, "
            "I DM'd her right then, and a 20-minute Zoom turned into real work... the same kind of work I did for "
            "them as an employee. My W-2 turned into a 1099!\n\n"
            "The full story is on YouTube. Search @rod.brinson"),
        ig_tags='#laidoff #layoffs #entrepreneurship #networking #personalbrand #corporatelife #w2to1099 #beyondthebrand',
        tiktok=(
            "The company that laid me off hired MY company. My W-2 turned into a 1099. Full story on my YouTube: "
            "@rod.brinson #laidoff #entrepreneur #networking #personalbrand #careertok"),
    ),
    5: dict(
        name='Your Title Belongs to Them',
        title='Your Job Title Belongs to Them. Your Skill Belongs to You.',
        tiktok_title='Your title belongs to them',
        threads=(
            "Your title belongs to them, but your skill belongs to you.\n\n"
            "If you managed the team, that's leadership. If you were the one everybody came to for spreadsheets, "
            "somebody will pay you for that.\n\n"
            "Most people walk out of corporate with way more than they think they have!\n\n" + EP),
        facebook=(
            "What do people come to you for right now?\n\n"
            "Your title belongs to them, but your skill belongs to you. If you managed the team, that's leadership. "
            "If you were the one everybody came to for spreadsheets... somebody will pay you for that.\n\n"
            "Most people walk out of corporate with way more than they think they have. They never had to say it "
            "out loud because the company was saying it for them!\n\n"
            "Full episode: " + EP),
        linkedin=(
            "Your title belongs to the company. Your skill belongs to you.\n\n"
            "Most of us can't see our own skill set in work we've been doing for years. If you managed a team, "
            "that's leadership. If you were the person who fixed the problems nobody else could fix, that's "
            "consulting.\n\n"
            "Most people walk out of corporate with far more than they think they have. They never had to say it "
            "out loud, because the company was saying it for them.\n\n"
            "So write it down. What do people come to you for right now? That's step five in this week's episode: "
            + EP),
        youtube=(
            "Managed a team? That's leadership. The one everybody came to for spreadsheets? Somebody will pay you "
            "for that. You're walking out of corporate with more than you think.\n\n"
            "Watch the full episode: " + EP + "\n\n"
            "#shorts #careerchange #transferableskills #laidoff"),
        yt_tags=['transferable skills', 'career change', 'laid off', 'job title', 'start a business after layoff',
                 'corporate to entrepreneur', 'Rod Brinson', 'Beyond the Brand'],
        instagram=(
            "Your title belongs to them, but your skill belongs to you.\n\n"
            "If you managed the team, that's leadership. If you were the one everybody came to for spreadsheets, "
            "somebody will pay you for that. You're walking out of corporate with way more than you think you "
            "have... you just never had to say it out loud!\n\n"
            + IG_CTA),
        ig_tags='#careerchange #transferableskills #knowyourworth #laidoff #corporatelife #entrepreneurship #personalbrand #beyondthebrand',
        tiktok=(
            "Your title belongs to them. Your skill belongs to you, and somebody will pay you for it. "
            "Full episode on my YouTube: @rod.brinson #careerchange #laidoff #knowyourworth #corporatelife #careertok"),
    ),
    6: dict(
        name='The Pit Was the Middle of the Story',
        title='Your Layoff Is the Middle of Your Story',
        tiktok_title='The layoff is the middle',
        threads=(
            "Genesis 50:20. \"You intended to harm me, but God intended it for good.\"\n\n"
            "The pit was the middle of Joseph's story... and the layoff is the middle of yours.\n\n"
            "If God can do it with Joseph, He can definitely do it with you!\n\n" + EP),
        facebook=(
            "His brothers threw him in a pit and sold him. Years later they stood in front of him, scared he was "
            "about to pay them back.\n\n"
            "And Joseph told them, \"You intended to harm me, but God intended it for good.\" That's Genesis "
            "50:20.\n\n"
            "The pit was the middle of Joseph's story, and the layoff is the middle of yours. If God can do it with "
            "Joseph, He can definitely do it with you!\n\n"
            "Full episode: " + EP),
        linkedin=(
            "If you just got laid off, I want you to remember Joseph.\n\n"
            "His brothers threw him in a pit and sold him. Years later, when they stood in front of him afraid, he "
            "told them, \"You intended to harm me, but God intended it for good.\" That is Genesis 50:20.\n\n"
            "The pit was the middle of Joseph's story, and the layoff is the middle of yours.\n\n"
            "If you're in the middle right now, this week's episode gives you seven practical steps to take next: "
            + EP),
        youtube=(
            "Genesis 50:20. The pit was the middle of Joseph's story, and the layoff is the middle of yours.\n\n"
            "Watch the full episode: " + EP + "\n\n"
            "#shorts #faith #laidoff #encouragement"),
        yt_tags=['Genesis 50:20', 'Joseph', 'faith after job loss', 'laid off', 'Christian entrepreneur',
                 'encouragement', 'Rod Brinson', 'Beyond the Brand'],
        instagram=(
            "The pit was the middle of Joseph's story... and the layoff is the middle of yours.\n\n"
            "\"You intended to harm me, but God intended it for good.\" Genesis 50:20.\n\n"
            "If God can do it with Joseph, He can definitely do it with you!\n\n"
            + IG_CTA),
        ig_tags='#genesis5020 #faith #laidoff #layoffs #godsplan #encouragement #christianentrepreneur #beyondthebrand',
        tiktok=(
            "The pit was the middle of Joseph's story. The layoff is the middle of yours. Genesis 50:20. "
            "Full episode on my YouTube: @rod.brinson #faith #laidoff #genesis5020 #encouragement #christiantiktok"),
    ),
}

NETS = ['threads', 'facebook', 'linkedin', 'youtube', 'instagram', 'tiktok']


def payload(day, net):
    c = CLIPS[day['clip']]
    hhmm = day['slots'][net]
    info = {
        'autoPublish': True,
        'draft': False,
        'text': c[net],
        'firstCommentText': c['ig_tags'] if net == 'instagram' else '',
        'media': [f"{HOST}/ep02-clip{day['clip']:02d}.mp4"],
        'mediaAltText': [],
        'providers': [{'network': net}],
        'publicationDate': {'dateTime': f"{day['date']}T{hhmm}:00", 'timezone': TZ},
        'shortener': False,
        'smartLinkData': {'ids': []},
        'hasNotReadNotes': False,
        'descendants': [],
    }
    if net == 'threads':
        info['threadsData'] = {'allowedCountryCodes': []}
    elif net == 'facebook':
        info['facebookData'] = {'type': 'REEL', 'title': c['title']}
        info['videoCoverMilliseconds'] = 1500
    elif net == 'linkedin':
        info['linkedinData'] = {'type': 'post', 'previewIncluded': True, 'publishImagesAsPDF': False}
        info['videoCoverMilliseconds'] = 1500
    elif net == 'youtube':
        info['youtubeData'] = {'title': c['title'], 'type': 'short', 'privacy': 'public', 'tags': c['yt_tags'],
                               'category': 'EDUCATION', 'madeForKids': False, 'isAiGeneratedContent': False}
    elif net == 'instagram':
        info['instagramData'] = {'type': 'REEL', 'showReelOnFeed': True, 'isAiGenerated': False}
        info['videoCoverMilliseconds'] = 1500
    elif net == 'tiktok':
        info['tiktokData'] = {'privacyOption': 'PUBLIC_TO_EVERYONE', 'title': c['tiktok_title'],
                              'disableComment': False, 'disableDuet': False, 'disableStitch': False,
                              'commercialContentThirdParty': False, 'commercialContentOwnBrand': False,
                              'autoAddMusic': False, 'photoCoverIndex': 0, 'isAigc': False}
        info['videoCoverMilliseconds'] = 1500
    return f"{day['date']}T{hhmm}:00-05:00", info


def fmt_time(hhmm):
    h, m = map(int, hhmm.split(':'))
    return f"{(h - 1) % 12 + 1}:{m:02d} {'AM' if h < 12 else 'PM'}"


def sheet(path):
    label = dict(threads='Threads', facebook='Facebook', linkedin='LinkedIn', youtube='YouTube Shorts',
                 instagram='Instagram', tiktok='TikTok')
    out = ['# Episode 2 clip posts: captions and schedule', '',
           'Episode: Laid Off? Don\'t Sign Anything Until You Watch This  ', EP, '',
           'One clip a day, Tuesday Nov 17 through Sunday Nov 22, 2026. All times Eastern.', '']
    for d in DAYS:
        c = CLIPS[d['clip']]
        out += [f"## {d['dow']} Nov {int(d['date'][-2:])}: {c['name']}", '',
                f"Title on YouTube Shorts and Facebook: **{c['title']}**  ", f"TikTok cover title: {c['tiktok_title']}", '']
        for n in sorted(NETS, key=lambda n: d['slots'][n]):
            out += [f"### {label[n]}, {fmt_time(d['slots'][n])}", '']
            out += ['> ' + line if line else '>' for line in c[n].split('\n')]
            if n == 'instagram':
                out += ['', f"First comment: {c['ig_tags']}"]
            if n == 'youtube':
                out += ['', 'Tags: ' + ', '.join(c['yt_tags'])]
            out.append('')
    open(path, 'w').write('\n'.join(out))


BANNED = ['—', '–', "here's the thing", 'the secret', 'let that sink in', 'game-changer', 'game changer', 'leverage',
          'utilize', 'unlock', 'elevate', 'seamless', 'delve', "it's not ", 'not just', 'no fluff']


def check():
    bad = 0
    for k, c in CLIPS.items():
        for n in NETS:
            t = c[n]
            low = t.lower()
            for b in BANNED:
                if b in low:
                    print(f'clip {k} {n}: banned phrase {b!r}')
                    bad += 1
            if n == 'threads' and len(t) > 500:
                print(f'clip {k} threads too long: {len(t)}')
                bad += 1
            if n in ('threads', 'facebook', 'linkedin', 'youtube') and EP not in t:
                print(f'clip {k} {n}: missing episode link')
                bad += 1
            if n in ('instagram', 'tiktok') and ('@rod.brinson' not in t or 'http' in t):
                print(f'clip {k} {n}: link rule broken')
                bad += 1
        if len(c['title']) > 70:
            print(f'clip {k} title long: {len(c["title"])}')
            bad += 1
        print(f"clip {k}: threads {len(c['threads'])} chars, fb {len(c['facebook'])}, li {len(c['linkedin'])}, "
              f"yt {len(c['youtube'])}, ig {len(c['instagram'])}, tt {len(c['tiktok'])}, title {len(c['title'])}")
    print('problems:', bad)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'payloads':
        d = DAYS[int(sys.argv[2])]
        for n in NETS:
            date, info = payload(d, n)
            print(json.dumps({'date': date, 'net': n, 'info': json.dumps(info, ensure_ascii=False)}, ensure_ascii=False))
    elif cmd == 'sheet':
        sheet(sys.argv[2])
    elif cmd == 'check':
        check()
