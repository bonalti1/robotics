import sys; sys.path.insert(0,'/home/claude/vex')
from mascot import mascot
D='#1c2340';CR='#fff8ec';Y='#f5c400';R='#e5484d';B='#3e7bfa';G='#22a06b';P='#8a63d2'
def M(x,y,s=1): return f'<g transform="translate({x} {y}) scale({s})">'+mascot().split('>',1)[1].rsplit('</svg>',1)[0]+'</g>'
def flop(x,y,s=1,arm=0,bag=None):
    b=f'<rect x="388" y="70" width="30" height="20" rx="6" fill="{bag}" stroke="{D}" stroke-width="4"/>' if bag else ''
    return f'''<g transform="translate({x} {y}) scale({s})">
<g transform="rotate({-arm} 250 81)"><rect x="250" y="70" width="150" height="22" rx="11" fill="{P}"/>
<circle cx="400" cy="120" r="34" fill="{G}"/><path d="M380 120h40M400 100v40" stroke="#fff" stroke-width="6" stroke-linecap="round"/><rect x="388" y="88" width="24" height="20" fill="{G}"/>{b}</g>
<rect x="70" y="120" width="250" height="120" rx="26" fill="#fff" stroke="{D}" stroke-width="5"/>
<rect x="130" y="70" width="130" height="60" rx="20" fill="{D}"/><circle cx="170" cy="100" r="13" fill="#5ef0ff"/><circle cx="220" cy="100" r="13" fill="#5ef0ff"/>
<circle cx="324" cy="200" r="16" fill="{R}" stroke="{D}" stroke-width="4"/>
<circle cx="120" cy="250" r="30" fill="{D}"/><path d="M120 225v50M95 250h50" stroke="#9aa3c7" stroke-width="5"/>
<circle cx="270" cy="250" r="30" fill="{D}"/><path d="M270 225v50M245 250h50" stroke="#9aa3c7" stroke-width="5"/></g>'''
def bag(x,y,c,s=1): return f'<rect x="{x}" y="{y}" width="{90*s}" height="{56*s}" rx="{18*s}" fill="{c}" stroke="{D}" stroke-width="6"/><path d="M{x+15*s} {y+28*s}h{60*s}" stroke="{D}" stroke-opacity=".25" stroke-width="5" stroke-dasharray="8 8"/>'
def pyramid(x,y,c,s=1,stack=0,cols=None):
    cols=cols or [R]*4
    g=f'<polygon points="{x},{y+300*s} {x+360*s},{y+300*s} {x+280*s},{y+100*s} {x+80*s},{y+100*s}" fill="#ffd4d6" stroke="{c}" stroke-width="10"/><rect x="{x+70*s}" y="{y+86*s}" width="{220*s}" height="{20*s}" rx="8" fill="{c}"/>'
    for i in range(stack): g+=bag(x+135*s,y+(30-56*i)*s,cols[i],s)
    return g
def floorgoal(x,y,c,s=1): return f'<rect x="{x}" y="{y}" width="{260*s}" height="{120*s}" rx="18" fill="#ffd4d6" stroke="{c}" stroke-width="10"/>'
def svg(w,h,body,bg=CR): return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="{bg}"/>{body}</svg>'
def floor(w,h,y=None): y=y or h-180; return f'<rect x="0" y="{y}" width="{w}" height="{h-y}" fill="#d9dde6"/>'
ART={}
ART['01_mascot_hero']=svg(1024,1024,M(212,120,2.0)+'<ellipse cx="512" cy="900" rx="0" ry="0"/>')
ART['02_flop_robot']=svg(1024,1024,floor(1024,1024,800)+flop(80,330,1.9))
ART['03_flop_arm_up_with_bag']=svg(1024,1024,floor(1024,1024,800)+flop(80,330,1.9,arm=35,bag=Y))
ART['04_mascot_and_flop']=svg(1920,1080,floor(1920,1080,880)+M(230,230,1.75)+flop(900,380,2.2))
tiles=''.join(f'<rect x="{160+x*200}" y="{40+y*200}" width="196" height="196" fill="#e9ecf3"/>' for x in range(8) for y in range(5))
fbags=''.join(bag(x,y,c,.9) for x,y,c in [(560,260,Y),(800,420,R),(1040,640,B),(1240,300,Y),(700,700,B),(1340,560,R),(980,180,R),(460,560,Y)])
ART['05_field_topdown']=svg(1920,1080,f'<rect x="140" y="20" width="1640" height="1040" rx="24" fill="{D}"/>{tiles}'+floorgoal(170,420,R,1)[:0]+f'<rect x="176" y="380" width="120" height="320" rx="14" fill="#ffd4d6" stroke="{R}" stroke-width="10"/><rect x="1624" y="380" width="120" height="320" rx="14" fill="#d6e4ff" stroke="{B}" stroke-width="10"/><polygon points="176,250 336,250 306,60 206,60" fill="#ffd4d6" stroke="{R}" stroke-width="10"/><polygon points="1584,1020 1744,1020 1714,830 1614,830" fill="#d6e4ff" stroke="{B}" stroke-width="10"/><rect x="760" y="20" width="24" height="1040" fill="#9aa3c7" opacity=".0"/>'+fbags)
ART['06_beanbags_three']=svg(1920,1080,floor(1920,1080,760)+bag(420,600,R,2.4)+bag(830,600,B,2.4)+bag(1240,600,Y,2.4))
ART['07_scoring_floor_L1_stack']=svg(1920,1080,floor(1920,1080,880)+floorgoal(140,760,R,1.4)+bag(230,770,R,1.4)+pyramid(700,520,R,1.2,1)+pyramid(1300,520,R,1.2,2))
ART['08_pyramid_stack_tall']=svg(1024,1024,floor(1024,1024,860)+pyramid(150,500,R,2.0,3,[R,Y,R]))
ART['09_mascot_pointing_field']=svg(1920,1080,f'<rect x="700" y="120" width="1100" height="760" rx="24" fill="{D}"/>'+''.join(f'<rect x="{720+x*134}" y="{140+y*144}" width="130" height="140" fill="#e9ecf3"/>' for x in range(8) for y in range(5))+bag(900,300,Y,.8)+bag(1300,560,R,.8)+bag(1500,300,B,.8)+M(120,300,1.8))
for k,v in ART.items(): open(f'img/{k}.svg','w').write(v)
print(list(ART))
