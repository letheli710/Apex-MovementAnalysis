# Rough check for B5 (2026-11-13): R-301 ADS punch recovery with heat hold 0.08 s, fade 0.05 s,
# cold ADS k115 d20, hot k0 d60. Compares the analytic spring step with the fixed-step path
# (0x140a7b850) and prints peak time / time to half peak. Not fitted to data.
import math
def kd(t):  # t since last shot; heat 1 -> hold 0.08, fade 0.05
    h = 1.0 if t<0.08 else max(0.0, 1-(t-0.08)/0.05)
    k = 115 + (0-115)*h; d = 20 + (60-20)*h
    return k,d
def analytic(x,v,k,d,dt):
    disc = d*d-4*k
    if abs(disc)<=1e-3:
        a=d*0.5; c=x*a+v; e=math.exp(-0.5*d*dt); xn=c*dt+x
        return xn*e,(c-xn*a)*e
    if disc<0:
        w=math.sqrt(-disc)/2; a=d/2
        c1=x; c2=(v+a*x)/w; e=math.exp(-a*dt)
        xn=e*(c1*math.cos(w*dt)+c2*math.sin(w*dt))
        vn=e*(-a*(c1*math.cos(w*dt)+c2*math.sin(w*dt))+(-c1*w*math.sin(w*dt)+c2*w*math.cos(w*dt)))
        return xn,vn
    s=math.sqrt(disc); r1=(-d+s)/2; r2=(-d-s)/2
    A=(v-r2*x)/(r1-r2); B=x-A
    return A*math.exp(r1*dt)+B*math.exp(r2*dt), A*r1*math.exp(r1*dt)+B*r2*math.exp(r2*dt)
def legacy(x,v,k,d,dt=0.0166):
    x=x+v*dt; v=v*math.exp(-d*dt); v=v-k*x*dt; return x,v
def run(step, dt, x0=5.7, v0=30.0, T=1.2):
    t=0; x=x0; v=v0; xs=[]
    while t<T:
        k,d=kd(t); x,v=step(x,v,k,d,dt) if step is analytic else step(x,v,k,d,dt); t+=dt; xs.append((t,x))
    pk=max(xs,key=lambda p:p[1]); 
    half=next(tt for tt,xx in xs if tt>pk[0] and xx<=pk[1]/2)
    return pk[0],half-pk[0]
for v0 in (0,20,60):
  for dt in (1/144,1/60,1/20):
    print('v0',v0,'dt %.4f'%dt,'analytic peak/50%%: %.3f %.3f'%run(analytic,dt,v0=v0),' legacy: %.3f %.3f'%run(legacy,dt,v0=v0))
print('--- t50 from last shot')
def run2(dt,v0,hold=0.08,fade=0.05,x0=5.7,T=1.5):
    def kd2(t):
        h = 1.0 if t<hold else max(0.0, 1-(t-hold)/fade)
        return 115*(1-h), 20+40*h
    t=0;x=x0;v=v0;xs=[]
    while t<T:
        k,d=kd2(t); x,v=analytic(x,v,k,d,dt); t+=dt; xs.append((t,x))
    pk=max(xs,key=lambda p:p[1]); return pk[0], next(tt for tt,xx in xs if tt>pk[0] and xx<=pk[1]/2)
for v0 in (0,10,30,60,120):
    print(v0, ['%.3f/%.3f'%run2(1/144,v0,h) for h in (0.08,0.12)])
