#!/usr/bin/env python3
"""Connect & Cultivate: 32 flyers, Oct 23 to Nov 7, two a day (09:15 and 19:15; Nov 7 at 09:15 and 13:30)."""
import json, datetime
DOOR = "cc"
JOIN = "Join us Nov. 7th. *Link in bio.*"
# real meetup photos for testimonies and moments, generic for invites
REAL = ["hob_curtain_group.jpg","hob_laptop_women.jpg","hob_two_men_bar.jpg","hob_coffee_selfie.jpg","hob_lobby_group.jpg","hob_plaid_talk.jpg","hob_home_group.jpg","hob_bar_three.jpg","hob_window_talk.jpg","hob_walk.jpg","hob_rod_selfie.jpg","hob_hug.jpg","hob_gamenight.jpg","hob_curtain_group.jpg","hob_laptop_women.jpg","hob_two_men_bar.jpg","hob_coffee_selfie.jpg","hob_home_group.jpg"]
GEN = ["gen13.jpg","gen07.jpg","gen20.jpg","gen15.jpg","gen09.jpg","gen24.jpg","gen04.jpg","gen18.jpg","gen12.jpg","gen10.jpg","gen27.jpg","gen16.jpg","gen14.jpg","gen25.jpg"]

# (kind, slide fields, caption, threads)
# kind: invite (tribe template), say (testimony), moment (tribe with kicker+body)
I = []  # invites
def inv(lines, cap, th, size=None, pos='center 35%'):
    I.append(dict(kind='invite', t='tribe', lines=lines, pos=pos, caption=cap, threads=th, size=size))

inv(["Being in the room","_changes everything._"],
 "I can't explain it any better than this....\n\nYou can watch every video, read every book, take every course. And then you sit at a table with people who are building the same thing you are and something shifts in twenty minutes that didn't shift in two years.\n\nConnect & Cultivate. Saturday, November 7th, 4pm, Buckhead. House of Brand in person. $35, 60 seats, none at the door. {door}\n\nWhat's the last room you walked into that changed something for you?",
 "being in the room changes everything. Connect & Cultivate, Sat Nov 7, 4pm, Buckhead. House of Brand in person. $35, 60 seats. {door}")
inv(["This is","more than","*networking.*"],
 "I know what you're picturing. Name tags. A bar. Three conversations that go nowhere.\n\nThis is House of Brand in person. Every room has somebody hosting it. There's a corner to shoot content, a floor if you've got a pitch, one house party drink on us, and sixty people who chose to spend a Saturday afternoon building.\n\nNovember 7th. 4pm. Buckhead. $35. {door}\n\nTell me what you need from a room like this and I'll make sure it's there.",
 "this is more than networking. House of Brand in person, Sat Nov 7, 4pm, Buckhead. one house party drink on us. $35, 60 seats. {door}")
inv(["Come find","_your people._"],
 "Somewhere in this city there's a handful of people who get exactly what you're trying to build. You just haven't been in the same room yet.\n\nThat's what November 7th is for. Connect & Cultivate, 4pm, Buckhead, House of Brand in person. $35, 60 seats. {door}\n\nWho's coming with you? Tag them.",
 "come find your people. Connect & Cultivate, Sat Nov 7, 4pm, Buckhead. $35, 60 seats. {door}")
inv(["Your people","are in this city."],
 "Builders. Dreamers. People on their second and third try. People who left the job and people who are still planning it.\n\nThey're here in Atlanta, and on November 7th we're putting sixty of them in one room. Connect & Cultivate, 4pm, Buckhead, $35. {door}\n\nWhat are you building right now? Say it in the comments so your people can find you before Saturday.",
 "your people are in this city. you just haven't met them yet. Sat Nov 7, 4pm, Buckhead. $35, 60 seats. {door}")
inv(["This is a room","you *want*","to be in."],
 "Not every room is worth the drive. This one is.\n\nSixty people, every one of them building something. Somebody hosting every conversation so you're never stuck. A content corner, a pitch floor, bites and a drink. House of Brand, in person, for one afternoon.\n\nSaturday, November 7th, 4pm, Buckhead. $35. {door}\n\nDrop a 🙋🏾 if you're in.",
 "this is a room you want to be in. Connect & Cultivate, Sat Nov 7, 4pm, Buckhead. $35, 60 seats. {door}")
inv(["You don't have","to build *alone.*"],
 "I built alone for years and called it discipline. It wasn't. It was just lonely, and it was slow.\n\nHouse of Brand exists so nobody has to do that. On November 7th the house meets in person. Come sit with people who are building too. Connect & Cultivate, 4pm, Buckhead, $35. {door}\n\nWhat's the thing you've been carrying by yourself?",
 "you don't have to build alone. House of Brand in person, Sat Nov 7, 4pm, Buckhead. $35, 60 seats. {door}")
inv(["Trying to grow","your brand?","_Start here._"],
 "Your brand doesn't grow on a feed. It grows in rooms where people remember your name.\n\nNovember 7th is that room. Sixty people paying attention, a corner to shoot content, and a floor to say your idea out loud. Connect & Cultivate, 4pm, Buckhead, $35. {door}\n\nWhat's your brand? One sentence. Go.",
 "trying to grow your brand? start in a room. Connect & Cultivate, Sat Nov 7, 4pm, Buckhead. $35, 60 seats. {door}")
inv(["Come alone.","_Most people do._"],
 "You don't need a plus one. Most people walk in by themselves, and within ten minutes somebody has pulled them into a conversation. That's not luck, that's how we built the afternoon.\n\nConnect & Cultivate. Saturday, November 7th, 4pm, Buckhead. $35. {door}\n\nIf you're coming solo, say so. I'll make sure somebody's looking for you.",
 "come alone. most people do. and nobody stays alone for long. Sat Nov 7, 4pm, Buckhead. $35. {door}")
inv(["Introverts welcome.","_We planned_","_for you._"],
 "If walking into a room of strangers makes your stomach turn, this was built with you in mind.\n\nEvery room has a host. The conversations are set up on purpose. Nobody is going to make you work the room. The room comes to you.\n\nNovember 7th, 4pm, Buckhead. $35. {door}\n\nIntroverts, let me hear from you. 🙋🏾",
 "introverts welcome. we planned for you. every room has a host, nobody works the room. Sat Nov 7, 4pm, Buckhead. $35. {door}")
inv(["Pull up","_a chair._"],
 "That's it. That's the invite.\n\nHouse of Brand, in person. Saturday, November 7th, 4pm, Buckhead. Bites, a drink, sixty people building. $35, none at the door. {door}\n\nSee you there?",
 "pull up a chair. House of Brand in person, Sat Nov 7, 4pm, Buckhead. $35, 60 seats. {door}")
inv(["Not a mixer.","*A table.*"],
 "The difference is simple. At a mixer you stand. At a table you sit down and actually talk.\n\nConnect & Cultivate is a table. Sixty seats, somebody hosting each one, and conversations with a point. Saturday, November 7th, 4pm, Buckhead. $35. {door}\n\nWhen's the last time you left a networking event with somebody you actually called?",
 "not a mixer. a table. Connect & Cultivate, Sat Nov 7, 4pm, Buckhead. $35, 60 seats. {door}")
inv(["Walk in a stranger.","_Walk out_","_with people._"],
 "That's the promise, and it's one we can actually keep because the afternoon is built for it.\n\nHouse of Brand in person. November 7th, 4pm, Buckhead. $35, 60 seats. {door}\n\nWho do you wish you'd met a year ago?",
 "walk in a stranger. walk out with people. Sat Nov 7, 4pm, Buckhead. $35, 60 seats. {door}")
inv(["Say your idea","out loud.","_We'll listen._"],
 "You've been practicing it in the car. In the mirror. In your head at 2am.\n\nOn November 7th there's a floor for it and a room that wants you to land it. Connect & Cultivate, 4pm, Buckhead, $35. {door}\n\nWhat's the idea? Give me one line.",
 "say your idea out loud. we'll listen. there's a floor for it Nov 7. 4pm, Buckhead. $35. {door}")
inv(["House of Brand,","*in person.*"],
 "Every Thursday night we're on a screen. On November 7th the screen comes down.\n\nConnect & Cultivate. 4pm, Buckhead. Bites, a house party drink on us, a content corner, live pitches, and sixty people who are building. $35, none at the door. {door}\n\nBrand Mates, tag somebody who needs to be in the house.",
 "House of Brand, in person. Sat Nov 7, 4pm, Buckhead. $35, 60 seats, none at the door. {door}")

S = []  # testimonies (say) and moments
def say(lines, who, cap, th, role='Brand Mate', size=None):
    S.append(dict(kind='say', t='say', lines=lines, who=who, role=role, caption=cap, threads=th, size=size))
def mom(lines, kicker, body, cap, th, size=None):
    S.append(dict(kind='moment', t='tribe', lines=lines, kicker=kicker, body=body, caption=cap, threads=th, size=size))

say(["The meetup was","so amazing. We stayed","45 minutes after","everyone else."], "Natasha",
 "Natasha said this on a Thursday call the week after our last meetup. She and Mahogany stayed almost an hour after everybody left.\n\nThat's the kind of room this is. November 7th we're doing it again, bigger. Connect & Cultivate, 4pm, Buckhead, House of Brand in person. $35, 60 seats. {door}\n\nWho's staying late with us?",
 "\"the meetup was so amazing. we stayed 45 minutes after everyone else.\" Natasha, Brand Mate. next one is Nov 7, 4pm, Buckhead. $35. {door}")
say(["I just wish","we were all in","the same space."], "Mahogany",
 "Mahogany said this on a call in August. We heard her.\n\nNovember 7th, we're all in the same space. Connect & Cultivate, 4pm, Buckhead, House of Brand in person. $35, 60 seats, none at the door. {door}\n\nIf you've ever said this about an online community, this one's for you.",
 "\"I just wish we were all in the same space.\" Mahogany said that in August. Nov 7 we will be. 4pm, Buckhead. $35. {door}")
say(["Talking with her","was like talking","with an old friend."], "Natasha",
 "That's Natasha talking about somebody she met at our last meetup. Not a contact. Not a lead. A friend.\n\nThat's what we're going for on November 7th. Connect & Cultivate, 4pm, Buckhead. $35. {door}\n\nWho was the last person you met that felt like you'd known them for years?",
 "\"talking with her was like talking with an old friend.\" Natasha, about somebody she met at our last meetup. Nov 7, 4pm, Buckhead. $35. {door}")
say(["I needed this today.","I needed all of this."], "Krystal",
 "Krystal said this at the end of a lunchtime workshop. Some days the business is heavy and what you need is a room that gets it.\n\nNovember 7th is that room. Connect & Cultivate, 4pm, Buckhead, House of Brand in person. $35. {door}\n\nWhat do you need from a room right now?",
 "\"I needed this today. I needed all of this.\" Krystal, Brand Mate. come get what you need Nov 7. 4pm, Buckhead. $35. {door}")
say(["Me and the sisters","met last week","without you. We want","to keep being in it."], "Adesanya",
 "Adesanya said this to me on the last night of our 8-week cohort. They met on their own, without me, because they didn't want it to end.\n\nThat's the house. On November 7th you can meet it in person. Connect & Cultivate, 4pm, Buckhead. $35, 60 seats. {door}\n\nTag the people you'd keep meeting with.",
 "\"me and the sisters met last week without you. we want to keep being in it.\" Adesanya, Brand Mate. this is the house. Nov 7, 4pm, Buckhead. $35. {door}")
say(["I'm so glad","that I did not fold."], "Mahogany",
 "Mahogany held her price with a client who was hesitating. She gave them space. Sunday morning the message came in: send me the invoice.\n\nShe told that story to the whole house. That's what the room is for. November 7th, Connect & Cultivate, 4pm, Buckhead. $35. {door}\n\nWhen's the last time you almost folded and didn't?",
 "\"I'm so glad that I did not fold.\" Mahogany held her price and the client said send the invoice. stories like this are why we meet. Nov 7, 4pm, Buckhead. $35. {door}")
say(["I'm definitely","more clear now","than I was when","we started."], "Sherry",
 "Sherry, at the end of eight weeks with the house. Clear is the whole point.\n\nIf you're building something and it still feels foggy, come sit with people who've been where you are. Connect & Cultivate, November 7th, 4pm, Buckhead. $35. {door}\n\nWhat would clear look like for you?",
 "\"I'm definitely more clear now than I was when we started.\" Sherry, Brand Mate. come get clear Nov 7. 4pm, Buckhead. $35. {door}")
say(["People started saying,","oh my God,","I'm not the only one."], "Dalin",
 "Dalin was describing a call where people came on camera one by one and realized they weren't the only ones feeling it.\n\nThat moment happens in person too. Faster. November 7th, Connect & Cultivate, 4pm, Buckhead. $35, 60 seats. {door}\n\nWhat's the thing you thought you were the only one dealing with?",
 "\"people started saying, oh my God, I'm not the only one.\" Dalin, on a House of Brand call. come find out you're not the only one. Nov 7, 4pm, Buckhead. $35. {door}")
say(["It's been","life-changing for me."], "Adesanya",
 "Adesanya's words, not mine. She said it wasn't bells and whistles, it was a couple of things that hit her right in the gut.\n\nThat's what happens when you stop building by yourself. Connect & Cultivate, November 7th, 4pm, Buckhead. House of Brand in person. $35. {door}\n\nCome see for yourself.",
 "\"it's been life-changing for me.\" Adesanya, Brand Mate. House of Brand in person, Nov 7, 4pm, Buckhead. $35. {door}")
say(["We need this.","I need this more","than ever today."], "Krystal",
 "Krystal said this walking into a game night. Not a workshop. A game night.\n\nBecause sometimes what you need from a community is to laugh with people who get it. November 7th has both. Connect & Cultivate, 4pm, Buckhead. $35. {door}\n\nWhat do you need more than ever right now?",
 "\"we need this. I need this more than ever today.\" Krystal, walking into a House of Brand game night. Nov 7, 4pm, Buckhead. $35. {door}")
say(["You invested","in yourselves."], "Dalin",
 "Dalin, our guest coach, said this to the house: you didn't invest in Rod, you invested in yourselves.\n\n$35 and a Saturday afternoon. That's the investment. Connect & Cultivate, November 7th, 4pm, Buckhead. 60 seats. {door}\n\nWhen's the last time you spent money on yourself and not the business?",
 "\"you invested in yourselves.\" Dalin, guest coach, to the house. $35 and a Saturday. Nov 7, 4pm, Buckhead. {door}", role="Guest coach")

mom(["Two people forgot","to eat dinner."], "True story", "Our last game night, MJ vs Prince, ran so long nobody noticed the time. It ended in a tie and went to a round 21.",
 "That's a real thing that happened in the house. A Tuesday game night that was supposed to be an hour. Twenty rounds, a tiebreaker, and two people who forgot to eat.\n\nWe do business. We also do this. November 7th is both. Connect & Cultivate, 4pm, Buckhead. $35. {door}\n\nMJ or Prince? Wrong answers only.",
 "true story: our last game night ran so long two people forgot to eat dinner. MJ vs Prince, 20 rounds, tiebreaker. this is the house. Nov 7, 4pm, Buckhead. $35. {door}")
mom(["They met in the house.","Now they're","publishing a book."], "True story", "Myron announced on a Thursday call that he's publishing his first book with Mahogany, who runs a publishing company. Both Brand Mates.",
 "Myron got on a call and told us he's publishing his first book. His publisher? Mahogany. They met in House of Brand.\n\nThat's what happens when builders are in the same room. November 7th, come be in it. Connect & Cultivate, 4pm, Buckhead. $35. {door}\n\nWho do you need to meet?",
 "true story: Myron and Mahogany met in the house. now he's publishing his first book with her. come meet your person Nov 7. 4pm, Buckhead. $35. {door}", size=86)
mom(["$400 saved","in four minutes."], "True story", "Sherry came to a roundtable overwhelmed by a registration service. Four minutes and one link later, she had her answer and kept her money.",
 "This is what a Thursday night looks like in the house. Somebody comes in stuck, somebody else drops the link, and four minutes later the problem is gone.\n\nNow imagine that at a table. November 7th, Connect & Cultivate, 4pm, Buckhead. $35, 60 seats. {door}\n\nWhat's the thing you've been overpaying for because you didn't know who to ask?",
 "true story: $400 saved in four minutes on a Thursday call. that's what a room full of builders does. Nov 7, 4pm, Buckhead. $35. {door}")
mom(["There's a win wall.","Bring something for it."], "In the house", "Brand Mates post their wins and the whole house gives them their flowers. Come get yours.",
 "In the house we've got a win wall. You post it, everybody gives you your flowers. It's one of my favorite things we do.\n\nOn November 7th the win wall is live and in person. Bring a win, any size. Connect & Cultivate, 4pm, Buckhead. $35. {door}\n\nWhat's a win you haven't told anybody about yet?",
 "there's a win wall in the house. you post it, everybody gives you your flowers. Nov 7 it's in person. 4pm, Buckhead. $35. {door}")
mom(["One house party","drink is on us."], "The vibe", "Bites, a specialty drink with your ticket, music, and sixty people building. A house party with a point.",
 "Let me tell you what the afternoon actually feels like. It's a house party. There's a specialty drink with your ticket, bites to pick at, and a room full of people who are building something.\n\nThe difference is every conversation has a point. Connect & Cultivate, November 7th, 4pm, Buckhead. $35. {door}\n\nWhat should the house drink be? Taking suggestions.",
 "one house party drink is on us. bites, music, sixty people building. a house party with a point. Nov 7, 4pm, Buckhead. $35. {door}")
mom(["Nothing worth building","was ever built","by one person."], "Rod Brinson", "I say this on every call. On November 7th I get to say it to your face.",
 "I say this to the house every week and I'll keep saying it. Nothing worth building has ever been built by one person alone.\n\nNovember 7th, come build next to somebody. Connect & Cultivate, 4pm, Buckhead, House of Brand in person. $35, 60 seats. {door}\n\nWho's been in your corner?",
 "nothing worth building was ever built by one person alone. come build next to somebody. Nov 7, 4pm, Buckhead. $35. {door}")
mom(["13 of them went","to a concert together","the next day."], "True story", "After our last meetup, a group of ladies who'd just met went to a Tasha Cobbs concert together the following night.",
 "After the last meetup, thirteen ladies who had just met went to a concert together the next night. Some of them had never been in the same room before Saturday.\n\nThat's not networking. That's your people. November 7th, Connect & Cultivate, 4pm, Buckhead. $35. {door}\n\nWho are you bringing?",
 "true story: after our last meetup, 13 ladies who'd just met went to a concert together the next night. that's your people. Nov 7, 4pm, Buckhead. $35. {door}")

# ---- schedule: Oct 23 .. Nov 7, AM = invite, PM = real; last day flips
days = [datetime.date(2026,10,23)+datetime.timedelta(d) for d in range(16)]
posts = []; ii = si = 0; ri = gi = 0
HT_INV = "#connectandcultivate #houseofbrand #atlantaentrepreneurs #buildyourbrand #networkingatlanta"
HT_SAY = "#houseofbrand #connectandcultivate #brandmates #atlantaevents #findyourpeople"
# order real items: alternate say / moment, keep Mahogany 'same space' early
real_order = [S[1],S[0],S[11],S[2],S[12],S[3],S[13],S[4],S[14],S[5],S[15],S[6],S[16],S[7],S[17],S[8]]
left = [x for x in S if x not in real_order]  # S[9], S[10]
for n, day in enumerate(days):
    last = (n == 15)
    am_slot, pm_slot = ("09:15", "13:30") if last else ("09:15", "19:15")
    # AM
    if ii < len(I):
        it = I[ii]; ii += 1; photo = GEN[gi % len(GEN)]; gi += 1
        sl = dict(t='tribe', photo=photo, pos=it['pos'], lines=it['lines'])
        if it.get('size'): sl['size'] = it['size']
        if last: sl['join'] = "*Today.* Doors at 4pm. Link in bio."
        posts.append(dict(id=f"d{n+1:02d}-am", date=str(day), slot=am_slot, kind="invite", door=DOOR, slides=[sl], caption=it['caption'], threads=it['threads'], hashtags=HT_INV))
    else:
        it = left.pop(0); photo = REAL[ri % len(REAL)]; ri += 1
        sl = {k: v for k, v in it.items() if k not in ('kind','caption','threads','size')}; sl['photo'] = photo; sl['pos'] = 'center 35%'
        if it.get('size'): sl['size'] = it['size']
        if last: sl['join'] = "*Today.* Doors at 4pm. Link in bio."
        posts.append(dict(id=f"d{n+1:02d}-am", date=str(day), slot=am_slot, kind=it['kind'], door=DOOR, slides=[sl], caption=it['caption'], threads=it['threads'], hashtags=HT_SAY))
    # PM
    it = real_order[n]; photo = REAL[ri % len(REAL)]; ri += 1
    sl = {k: v for k, v in it.items() if k not in ('kind','caption','threads','size')}; sl['photo'] = photo; sl['pos'] = 'center 35%'
    if it.get('size'): sl['size'] = it['size']
    if last: sl['join'] = "*Today.* Doors at 4pm. Link in bio."
    posts.append(dict(id=f"d{n+1:02d}-pm", date=str(day), slot=pm_slot, kind=it['kind'], door=DOOR, slides=[sl], caption=it['caption'], threads=it['threads'], hashtags=HT_SAY))

json.dump({"campaign": "Connect & Cultivate 2026-11-07", "posts": posts}, open('content.json', 'w'), indent=1, ensure_ascii=False)
print(len(posts), 'posts;', len(I), 'invites;', len(S), 'real')
