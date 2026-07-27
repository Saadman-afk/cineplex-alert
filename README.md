# Spider-Man Ticket Alert (Cineplex BD)

Watches https://ticket.cineplexbd.com/home every 5 minutes and emails + push-notifies
you the instant "Spider-Man: Brand New Day" tickets go bookable. Runs entirely
free on GitHub Actions — no server, no subscription, works even if your Mac is off.

## Setup (takes ~10 minutes, one time)

### 1. Create the GitHub repo
- Go to github.com → New repository → name it e.g. `cineplex-alert`.
- **Make it Public.** (Public repos get unlimited free Actions minutes. Private
  repos only get ~2000 free min/month, and checking every 5 min would use
  more than that.) There's no sensitive info in this code — your email/app
  password go in encrypted Secrets, not in the code itself.
- Upload all the files in this folder to the repo (drag-and-drop on the GitHub
  web UI works fine, or use git — see below).

### 2. Get a Gmail "app password" (so the script can send email as you)
- Go to https://myaccount.google.com/apppasswords (needs 2-Step Verification
  turned on for your Google account first).
- Create an app password named "cineplex-alert", copy the 16-character code.

### 3. Install ntfy on your phone (free instant push notifications)
- Install the "ntfy" app (App Store / Play Store).
- In the app, subscribe to a topic — pick something random and hard to guess,
  e.g. `sadman-spiderman-4821`. Anyone who knows this exact topic name could
  send you notifications, so don't use something obvious like "spiderman".

### 4. Add secrets to your GitHub repo
Repo → Settings → Secrets and variables → Actions → New repository secret.
Add these four:

| Name | Value |
|---|---|
| `GMAIL_USER` | your Gmail address |
| `GMAIL_APP_PASSWORD` | the 16-character app password from step 2 |
| `TO_EMAIL` | the email address you want alerts sent to (can be same as above) |
| `NTFY_TOPIC` | the topic name you picked in step 3 |

### 5. Turn it on
- Go to the repo's "Actions" tab → you should see "Check Spider-Man Tickets" →
  click "Enable workflow" if prompted.
- Click "Run workflow" (workflow_dispatch) once to test it manually. Check the
  run's logs — it'll print a line like:
  `Status: not_listed_yet` (normal, before tickets go live)
  `Status: listed_but_not_bookable` (movie page exists, no Buy button yet)
  `Status: bookable` (tickets are live — you should get an email + push)
- If the test run finishes green with no errors, you're done. It'll now check
  automatically every 5 minutes.

## Notes / limitations
- GitHub auto-disables scheduled workflows after 60 days with no repo
  activity — not a concern for the next few days, just don't forget about it
  long-term.
- The script detects "bookable" by looking for text like "Buy Ticket" or
  "Book Now" near the movie title. If Cineplex's site uses different wording,
  or splits city/theater selection into a separate step, the very first
  real-world test (once tickets actually drop) is the true test. If it
  misses the alert, send me what the Action log printed and I'll tune the
  detection logic.
- To stop getting alerts after you've bought your ticket, just disable the
  workflow (Actions tab → "..." → Disable workflow), or delete the repo.

## Uploading the files via git (alternative to drag-and-drop)
```bash
cd cineplex-alert
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/cineplex-alert.git
git push -u origin main
```
