# Rejected: client ran at about 18.7 fps

The client window was not in front, so `not_focus_sleep` paced the client to about 18.7 fps
(measured from `PlatformTime()` between the schedule's start and end lines). The frame-indexed
schedule ("forward for 432 frames") therefore ran for about 23 s instead of 3 s, and the
player left the platform (end z ≈ −20).

Kept as evidence for the fix: `not_focus_sleep 0` in `hsd_client.cfg`, plus the runner's
frame-rate check (`hsd_trial.py check_pacing`, ±3 % of 144 fps). Not used for any result.
