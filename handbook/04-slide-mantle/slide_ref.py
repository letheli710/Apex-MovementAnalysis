"""Reference check of the chapter-04 slide pseudocode (flat ground, W held along the slide, no steering input).

Only the standard library. Implements 04-slide-mantle.md §4.8 literally and prints the R5 golden numbers of §4.8 "验收".
Units: u, s. Run:  py -3 slide_ref.py
"""
import math

MSC = 1.15
P = dict(slideRequiredStartSpeed=200, slideSpeedBoost=150, slideSpeedBoostCap=400, slideDecel=100,
         slideWantToStopDecel=400, slideVelocityDecay=0.7, slideStopSpeed=125, slideMaxStopSpeed=350,
         slideMaxJumpSpeed=350, slideJumpFloorLowFrac=0.85, slideBoostRefundWindow=0.4, slideDuckTransitionTime=0.2,
         slideBoostRearm=2.0, crouchSpeed=80, crouchDeceleration=1500)


class Slide:
    def __init__(self):
        self.sliding = False
        self.boosted = False
        self.s = 0.0
        self.last_boost = 0.0
        self.boost_time = -math.inf
        self.start_time = -math.inf
        self.duck_press_time = -math.inf

    def start(self, now, dt):
        """Duck press edge on the ground, before the move. Returns True when a slide started."""
        if self.sliding or self.s < P['slideRequiredStartSpeed']:
            return False
        boost = now - self.start_time >= P['slideBoostRearm'] - 1e-9
        if boost:
            peak = min(self.s + P['slideSpeedBoost'] * MSC, P['slideSpeedBoostCap'] * MSC)
            self.last_boost = peak - self.s
            self.boost_time = now
            self.s = peak
        self.sliding, self.boosted = True, boost
        self.start_time = now
        self.duck_press_time = now + dt          # the transition starts on the next command
        return True

    def ground(self, duck_held, dt):
        """One grounded command that is not a jump. Returns 'slide', 'end' (slide ended this command) or 'crouch'."""
        if not self.sliding:
            if self.s > P['crouchSpeed'] * MSC:
                self.s = max(P['crouchSpeed'] * MSC, self.s - P['crouchDeceleration'] * dt)
            return 'crouch'
        releasing = not duck_held
        if releasing and self.s <= P['slideMaxStopSpeed']:
            self.sliding = self.boosted = False
            self.s = max(P['crouchSpeed'] * MSC, self.s - P['crouchDeceleration'] * dt)   # this command is a crouched ground move
            return 'end'
        D = P['slideWantToStopDecel'] if releasing else P['slideDecel']
        self.s = max(0.0, (self.s - D * dt) * P['slideVelocityDecay'] ** dt)
        if self.s < P['slideStopSpeed']:
            self.sliding = self.boosted = False
            return 'end'
        return 'slide'

    def jump_speed(self, now):
        """Horizontal speed a slide jump leaves with (before the jump command's air acceleration)."""
        s = self.s
        if self.boosted:
            if now - self.boost_time < P['slideBoostRefundWindow'] and now - self.duck_press_time < P['slideDuckTransitionTime'] - 1e-9:
                s = max(0.0, s - self.last_boost)
            lo, hi = P['slideJumpFloorLowFrac'] * P['slideMaxJumpSpeed'], P['slideMaxJumpSpeed']
            if lo < s < hi:
                s = hi
        return s


def run_slide(fps, jump_after=None, release_after=None, total=3.0):
    dt = 1.0 / fps
    sl = Slide(); sl.s = 299.0
    now = 0.0
    sl.start(now, dt)
    peak = sl.s
    n = 0
    while now < total:
        if jump_after is not None and n == jump_after:
            return dict(pre=sl.s, exit=sl.jump_speed(now), t=now)
        duck = not (release_after is not None and n >= release_after)
        r = sl.ground(duck, dt)
        if r == 'end':
            return dict(peak=peak, end_cmd=n, end_t=now + dt, end_post=sl.s, released_at=release_after)
        n += 1
        now += dt
    return dict(peak=peak, still=sl.s)


if __name__ == '__main__':
    r = run_slide(144)
    print('M2 e5_slide 144 fps: peak %.3f, slide ends after command %d (%.4f s), post %.2f' % (r['peak'], r['end_cmd'], r['end_t'], r['end_post']))
    for k, meas in ((29, '247.77'), (86, '350.005')):
        j = run_slide(144, jump_after=k)
        print('M2 slide jump at %d cmds (%.4f s): pre %.2f -> exit %.2f   (R5 %s)' % (k, j['t'], j['pre'], j['exit'], meas))
    for age, meas in ((0.10, '273'), (0.25, '397'), (0.40, '361.5'), (0.60, '350.0'), (1.00, '236')):
        j = run_slide(120, jump_after=round(age * 120))
        print('M10 slide jump age %.2f s: pre %.1f -> exit %.1f   (R5 %s)' % (age, j['pre'], j['exit'], meas))
    for age, meas in ((0.10, 'ends 19 cmds later at 336'), (0.25, 'ends 11 cmds later at 335'), (0.50, 'ends on the release command'), (1.00, 'ends on the release command')):
        k = round(age * 120)
        r = run_slide(120, release_after=k)
        print('M10 release at %.2f s: ends %d cmds after the release, post %.1f   (R5 %s)' % (age, r['end_cmd'] - k, r['end_post'], meas))
    # slope equilibrium speeds and extra accel
    for th in (5, 10, 15, 20, 25, 30, 40):
        a = 750 * math.sin(math.radians(th)) * math.cos(math.radians(th))
        veq = (a - 100) / -math.log(0.7)
        print('slope %2d deg: extra accel %.1f u/s^2, equilibrium %.0f u/s' % (th, a, veq))
