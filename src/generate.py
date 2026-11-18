"""Generate the original worksheet illustrations and their search index."""
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"
INK = "#111111"
BLUE = "#dcecf7"
index = []
width = 760
height = 440


def text(x, y, value, size=32, anchor="mm", bg=False):
    font = ImageFont.truetype(FONT, size, index=3)
    if bg:  # 白底：標籤壓在線上也看得清楚
        l, t, rr, b = draw.textbbox((x, y), str(value), font=font, anchor=anchor)
        draw.rectangle((l-4, t-3, rr+4, b+3), fill="white")
    draw.text((x, y), str(value), font=font, fill=INK, anchor=anchor)


def line(*points, color=INK, weight=3):
    draw.line(points, fill=color, width=weight)


def box(x, y, w, h, fill="white"):
    draw.rectangle((x, y, x+w, y+h), fill=fill, outline=INK, width=3)


def circle(x, y, r, fill="white"):
    draw.ellipse((x-r, y-r, x+r, y+r), fill=fill, outline=INK, width=3)


def point(x, y, r, degrees):
    angle = math.radians(degrees)
    return x + r*math.cos(angle), y - r*math.sin(angle)


def polygon(points, fill=BLUE):
    draw.polygon(points, fill=fill)
    line(*points, points[0])


def make(grade, unit, name, kind, values, tags, desc):
    global draw
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    RENDERERS[kind](*values)
    rel = f"g{grade}/{name}.png"
    target = ROOT / "images" / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, optimize=True)
    keywords = list(dict.fromkeys([unit, *tags]))
    assert 5 <= len(keywords) <= 10, (name, keywords)
    index.append(dict(img=rel, grade=grade, unit=unit, tags=keywords, desc=desc))


def board(labels, values):
    size = min(135, 660//len(labels))
    left = (width-size*len(labels))//2
    for i, (label, value) in enumerate(zip(labels, values)):
        x = left + i*size
        box(x, 100, size, 85, BLUE)
        box(x, 185, size, 135)
        text(x+size/2, 143, label, 30)
        text(x+size/2, 252, value, 45)


def grouped(rows, cols, label, trays=False):
    step = min(70, 570/cols, 280/rows)
    left = (width-cols*step)/2
    top = (360-rows*step)/2
    for y in range(rows):
        if trays:
            box(left-8, top+y*step+4, cols*step+16, step-8, BLUE)
        for x in range(cols):
            circle(left+(x+.5)*step, top+(y+.5)*step, min(20, step*.23),
                   "white" if trays else BLUE)
    text(380, 399, label)


def grid(cols, rows, cells, caption):
    step = min(65, 610/cols, 320/rows)
    left = (width-cols*step)/2
    top = (370-rows*step)/2
    for y in range(rows):
        for x in range(cols):
            box(left+x*step, top+y*step, step, step, BLUE if (x,y) in cells else "white")
    text(380, 405, caption)


def ruler(n, mm, item, unknown):
    left = 75
    top = 240
    step = 600/n
    end = left + mm*step/10
    if item == "鉛筆":
        polygon([(left, 145), (end-25, 145), (end, 160),
                 (end-25, 175), (left, 175)])
    elif item == "線段":
        line((left,160),(end,160))
        circle(left,160,5,INK)
        circle(end,160,5,INK)
    else:
        box(left, 145, end-left, 32, BLUE)
    for x in (left, end):
        line((x,180),(x,top), color="#888888")
    box(left,top,600,95)
    for i in range(n*10+1):
        x = left+i*step/10
        line((x,top),(x,top+(39 if i%10==0 else 25 if i%5==0 else 15)))
        if i%10 == 0:
            text(x,top+66,i//10,28)
    text(380,90,f"{item}　{'？' if unknown else mm}毫米")
    text(380,375,"公分")


def clock(hour, minute, unknown):
    x,y,r = 380,195,156
    circle(x,y,r)
    for i in range(1,61):
        angle = 90-i*6
        line(point(x,y,r-3,angle),point(x,y,r-(15 if i%5==0 else 8),angle))
        if i%5==0:
            text(*point(x,y,r-33,angle),i//5,28)
    line((x,y),point(x,y,78,90-(hour+minute/60)*30),weight=9)
    line((x,y),point(x,y,114,90-minute*6),weight=5)
    circle(x,y,5,INK)
    text(x,395,"？時？分" if unknown else f"{hour}時{minute:02d}分")


def sector(degrees, radius, unknown, style):
    x,y,r = 380,185,145
    bounds = (x-r,y-r,x+r,y+r)
    if style == "diameter":
        circle(x,y,r)
        line((x-r,y),(x+r,y))
        circle(x,y,5,INK)
        text(x,385,f"直徑 {'？' if unknown else radius*2}公分")
        return
    if style == "protractor":
        draw.arc(bounds,180,360,fill=INK,width=3)
        for a in range(0,181,5):
            line(point(x,y,r,a),point(x,y,r-(13 if a%15==0 else 7),a))
            if a%30==0:
                text(*point(x,y,r+27,a),a,28)
    if degrees == 360 and style == "angle":
        draw.arc((x-85,y-85,x+85,y+85),20,350,fill=INK,width=3)
        polygon([(x+87,y-27),(x+74,y-36),(x+91,y-43)])
        line((x,y),(x+r,y))
        circle(x,y,5,INK)
        text(x,385,"？°" if unknown else "360°")
        return
    if style == "angle" or style == "protractor":
        line((x,y),point(x,y,r,0))
        line((x,y),point(x,y,r,degrees))
        draw.arc((x-45,y-45,x+45,y+45),360-degrees,360,fill=INK,width=3)
        text(x,385,f"{'？' if unknown else degrees}°")
    else:
        draw.pieslice(bounds,360-degrees,360,fill=BLUE,outline=INK,width=3)
        text(x,371,f"半徑 {radius}公分　　圓心角 {'？' if unknown else degrees}°")
    circle(x,y,5,INK)


def fraction(den, num, shape, caption):
    if shape == "pie":
        for i in range(den):
            draw.pieslice((250,46,510,306), i*360/den-90, (i+1)*360/den-90,
                          fill=BLUE if i<num else "white",outline=INK,width=3)
    elif shape == "equivalent":
        for row, factor in enumerate((1,2,4)):
            for i in range(den*factor):
                step = 480/(den*factor)
                box(90+i*step,55+100*row,step,60,BLUE if i<num*factor else "white")
            text(650,85+100*row,f"{num*factor}/{den*factor}")
    else:
        step = 600/den
        for i in range(den):
            box(80+i*step,145,step,100,BLUE if i<num else "white")
    text(380,389,caption)


def timeline(labels, start, stop, caption):
    step = 595/(len(labels)-1)
    left,y = 82,235
    line((left,y),(left+595,y))
    for i,label in enumerate(labels):
        x = left+i*step
        line((x,y-12),(x,y+12))
        text(x,y+46,label,30)
    a,b = left+start*step,left+stop*step
    line((a,y-18),(a,y-80),(b,y-80),(b,y-18),weight=4)
    polygon([(b,y-18),(b-10,y-36),(b+10,y-36)])
    text((a+b)/2,y-118,caption)


def chart(labels, values, tick, unit, kind, second=None):
    left,top,right,bottom = 120,75,680,340
    maximum = max(values + (second or []))
    levels = math.ceil(maximum/tick)
    if kind == "horizontal":
        step = (bottom-top)/len(values)
        for i, (label,value) in enumerate(zip(labels,values)):
            y = top+i*step
            text(left-12,y+step/2,label,29,"rm")
            box(left,y+step*.2,(right-left)*value/(levels*tick),step*.6,BLUE)
        for i in range(levels+1):
            text(left+i*(right-left)/levels,bottom+27,i*tick,28)
        line((left,top),(left,bottom),(right,bottom))
        text(650,405,unit)
        return
    step = (right-left)/len(values)
    def coordinates(series):
        return [(left+(i+.5)*step,bottom-v*(bottom-top)/(levels*tick))
                for i,v in enumerate(series)]
    for i in range(levels+1):
        y = bottom-i*(bottom-top)/levels
        line((left,y),(right,y),color="#aaaaaa")
        text(left-12,y,i*tick,28,"rm")
    line((left,top),(left,bottom),(right,bottom))
    text(left,36,unit,29)
    for i,label in enumerate(labels):
        text(left+(i+.5)*step,bottom+38,label,28)
    pts = coordinates(values)
    if kind == "bar":
        for x,y in pts:
            box(x-step*.30,y,step*.60,bottom-y,BLUE)
    else:
        line(*pts,weight=4)
        for x,y in pts:
            circle(x,y,7,BLUE)
        if second:
            pts = coordinates(second)
            for a,b in zip(pts,pts[1:]):
                for j in range(0,10,2):
                    line(tuple(a[k]+(b[k]-a[k])*j/10 for k in (0,1)),
                         tuple(a[k]+(b[k]-a[k])*(j+1)/10 for k in (0,1)))
            for x,y in pts:
                box(x-6,y-6,12,12,BLUE)


def shape(style, base, tall, unknown, grid_on):
    x0,y0 = 185,325
    scale = min(52, 450/(base+2), 240/tall)
    b,h = base*scale,tall*scale
    offset = scale*2
    if grid_on:
        for i in range(base+3):
            x = x0+i*scale
            line((x,y0-h),(x,y0),color="#a5a5a5",weight=1)
        for i in range(tall+1):
            y = y0-i*scale
            line((x0,y),(x0+b+2*scale,y),color="#a5a5a5",weight=1)
    vertices = {
        "triangle": [(x0,y0),(x0+b,y0),(x0+offset,y0-h)],
        "right": [(x0,y0),(x0+b,y0),(x0,y0-h)],
        "rectangle": [(x0,y0),(x0+b,y0),(x0+b,y0-h),(x0,y0-h)],
        "parallelogram": [(x0,y0),(x0+b,y0),(x0+b+offset,y0-h),(x0+offset,y0-h)],
        "trapezoid": [(x0,y0),(x0+b,y0),(x0+b-offset/2,y0-h),(x0+offset,y0-h)],
        "l": [(x0,y0),(x0+b,y0),(x0+b,y0-h/2),(x0+b/2,y0-h/2),
              (x0+b/2,y0-h),(x0,y0-h)],
    }[style]
    if grid_on:
        line(*vertices,vertices[0],weight=5)
    else:
        polygon(vertices)
    xx = x0+offset if style in ("triangle","trapezoid","parallelogram") else x0
    if xx != x0:
        for y in range(round(y0-h),y0,16):
            line((xx,y),(xx,min(y+8,y0)))
        line((xx,y0-14),(xx+14,y0-14),(xx+14,y0))
    text(x0+b/2,376,f"{base}公分")
    text(xx+12 if xx != x0 else x0-12,y0-h/2,f"{'？' if unknown else tall}公分",28,"lm" if xx != x0 else "rm",bg=xx != x0)
    if style == "trapezoid":
        text(x0+(b+offset/2)/2,y0-h-25,f"{base-3}公分",28)
    if style == "l":
        # 右下台階的寬標在台階上方的外面、缺口的高標在缺口旁邊，兩個不重疊
        text(x0+b*.75,y0-h/2+24,f"{base//2}公分",28,bg=True)
        text(x0+b/2+10,y0-h*.78,f"{tall//2}公分",28,"lm",bg=True)


def comparison(a,b,unit,unknown):
    scale = 480/max(a,b)
    for row,n in enumerate((a,b)):
        y = 105+row*140
        text(96,y+30,("甲","乙")[row])
        box(155,y,n*scale,60,BLUE if row else "white")
        text(155+n*scale/2,y+97,f"{'？' if unknown and row else n}{unit}")


def tree(a,b,c):
    for p,q in [((380,70),(230,195)),((380,70),(530,195)),
                ((530,195),(430,330)),((530,195),(630,330))]:
        line(p,q)
    for x,y,value in [(380,70,a*b*c),(230,195,a),(530,195,b*c),
                      (430,330,b),(630,330,c)]:
        circle(x,y,34,BLUE)
        text(x,y,value)


def ratio(a,b,first,second,unknown):
    for row,(n,label) in enumerate(((a,first),(b,second))):
        y = 136+row*145
        text(130,y,label)
        for i in range(n):
            x = 246+i*61
            if label in ("果汁","水"):
                polygon([(x-19,y-25),(x+19,y-25),(x+14,y+25),(x-14,y+25)],
                        BLUE if not row else "white")
            else:
                circle(x,y,22,BLUE if not row else "white")
        text(660,y,"？" if unknown and row else n)


def scale_pair(w,h,style,unknown,shrink=False):
    scales = ((65,2),(405,1)) if shrink else ((65,1),(405,2))
    for left,k in scales:
        s = 25
        top = 320
        for x in range(w*k+1):
            line((left+x*s,top-h*k*s),(left+x*s,top),color="#aaaaaa",weight=1)
        for y in range(h*k+1):
            line((left,top-y*s),(left+w*k*s,top-y*s),color="#aaaaaa",weight=1)
        right = left+w*k*s
        high = top-h*k*s
        pts = [(left,top),(right,top),(left,high)]
        if style == "rectangle":
            pts.insert(2,(right,high))
        if style == "l":
            pts[2:2] = [(right,(top+high)/2),((left+right)/2,(top+high)/2),
                        ((left+right)/2,high)]
        line(*pts,pts[0],weight=5)
        text(left+w*k*s/2,380,"原圖" if left==65 else "？倍" if unknown
             else "1/2倍" if shrink else "2倍")


RENDERERS = dict(board=board, grouped=grouped, grid=grid, ruler=ruler,
                 clock=clock, sector=sector, fraction=fraction, timeline=timeline,
                 chart=chart, shape=shape, comparison=comparison, tree=tree,
                 ratio=ratio, scale_pair=scale_pair)


def labeled_polygon(sides, labels, corners=False):
    pts = [point(380,206,151,90-i*360/sides) for i in range(sides)]
    polygon(pts)
    for i,label in enumerate(labels):
        a,b = pts[i],pts[(i+1)%sides]
        x,y = a if corners else ((a[0]+b[0])/2,(a[1]+b[1])/2)
        factor = .6 if corners else 1.28
        text(380+(x-380)*factor,206+(y-206)*factor,label,30,bg=not corners)


def gauge(capacity, amount, cup):
    if cup:
        box(290,70,210,300)
        box(290,370-amount*300/capacity,210,amount*300/capacity,BLUE)
        for i in range(6):
            y = 370-i*60
            line((290,y),(325,y))
            text(272,y,i*capacity//5,28,"rm")
        text(565,370,"毫升")
    else:
        circle(380,202,165)
        for i in range(11):
            a = 225-i*27
            line(point(380,202,145,a),point(380,202,157,a))
            if i % 2 == 0:  # 數字隔一格標一次，才不會擠在一起
                text(*point(380,202,112,a),i*capacity//10,28)
        line((380,202),point(380,202,95,225-amount*270/capacity),weight=6)
        text(380,390,"公克")


def table(labels, values):
    for i,(label,value) in enumerate(zip(["項目",*labels],["人數",*values])):
        x = 155+i*112
        box(x,125,112,70,BLUE)
        box(x,195,112,100)
        text(x+56,160,label)
        text(x+56,245,value)


def money(values):
    step = min(145,680/len(values))
    for i,value in enumerate(values):
        x = (width-step*len(values))/2+step*(i+.5)
        if value in (1, 5, 10, 50):  # 真的有的硬幣才畫成圓形
            circle(x,200,53,BLUE)
        else:  # 紙鈔或價錢標籤
            box(x-62,145,124,110,BLUE)
        text(x,200,f"{value}元",30)


def interval(count, gap, unknown):
    step = 585/(count-1)
    for i in range(count):
        x = 85+i*step
        line((x,200),(x,260),weight=5)
        circle(x,182,18,BLUE)
        if i:
            text(x-step/2,293,f"{'？' if unknown else gap}公尺",28)
    line((85,260),(670,260))


def dashed(a, b, n=16):
    for k in range(0, n, 2):
        line((a[0]+(b[0]-a[0])*k/n, a[1]+(b[1]-a[1])*k/n), (a[0]+(b[0]-a[0])*(k+1)/n, a[1]+(b[1]-a[1])*(k+1)/n), weight=2)


def price_tags(values):
    step = min(160,680/len(values))
    for i,value in enumerate(values):
        x = (width-step*len(values))/2+step*(i+.5)
        draw.polygon([(x-60,150),(x+42,150),(x+64,200),(x+42,250),(x-60,250)],fill=BLUE,outline=INK,width=3)
        circle(x+38,200,6)
        text(x-8,200,f"{value}元",30)


def solid(sides, pyramid, net):
    if net:
        if sides == 3:
            polygon([(380,142),(290,298),(470,298)])
            polygon([(380,142),(290,298),(200,142)])
            polygon([(380,142),(470,298),(560,142)])
            polygon([(290,298),(470,298),(380,424)])
        else:
            for x,y in [(325,140),(215,140),(435,140),(545,140),(325,30),(325,250)]:
                box(x,y,110,110,BLUE)
        return
    if sides == 0:
        draw.ellipse((235,70,525,170),fill=BLUE,outline=INK,width=3)
        draw.arc((235,260,525,360),0,180,fill=INK,width=3)
        line((235,120),(235,310))
        line((525,120),(525,310))
        return
    if pyramid:
        pts = [(380+150*math.cos(math.tau*i/sides+math.pi/2+math.pi/sides+(0.35 if sides == 4 else 0)),
                320+55*math.sin(math.tau*i/sides+math.pi/2+math.pi/sides+(0.35 if sides == 4 else 0))) for i in range(sides)]
        apex = (380,64)
        draw.polygon(pts,fill=BLUE)
        for i in range(sides):
            j = (i+1)%sides
            if (pts[i][1]+pts[j][1])/2 < 320-1: dashed(pts[i],pts[j])
            else: line(pts[i],pts[j])
        for p in pts:
            if p[1] < 320-1 and min(q[0] for q in pts)+1 < p[0] < max(q[0] for q in pts)-1: dashed(p,apex)
            else: line(p,apex)
        return
    # 角柱：直立的柱體，上下底面是 sides 邊形（斜看），側邊是鉛直線；看不到的邊畫虛線
    cy, tall = 345, 210
    pts = [(380+140*math.cos(math.tau*i/sides+math.pi/2+math.pi/sides+(0.35 if sides == 4 else 0)),
            cy+55*math.sin(math.tau*i/sides+math.pi/2+math.pi/sides+(0.35 if sides == 4 else 0))) for i in range(sides)]
    upper = [(x,y-tall) for x,y in pts]
    xs = [p[0] for p in pts]
    for i in range(sides):
        j = (i+1)%sides
        if (pts[i][1]+pts[j][1])/2 >= cy-1:  # 前面的側面塗色
            draw.polygon([pts[i],pts[j],upper[j],upper[i]],fill=BLUE)
    draw.polygon(upper,fill=BLUE)
    line(*upper,upper[0])
    for i in range(sides):
        j = (i+1)%sides
        if (pts[i][1]+pts[j][1])/2 < cy-1: dashed(pts[i],pts[j])
        else: line(pts[i],pts[j])
        silhouette = min(xs)+1 >= pts[i][0] or pts[i][0] >= max(xs)-1
        if pts[i][1] < cy-1 and not silhouette: dashed(pts[i],upper[i])
        else: line(pts[i],upper[i])


def map_view(scale, distance, unknown):
    places = [(145,305,"學校"),(370,115,"圖書館"),(610,305,"公園")]
    line((145,305),(610,305),(370,115),(145,305),color="#777777",weight=4)
    for x,y,name in places:
        box(x-13,y-13,26,26,BLUE)
        text(x,y-40,name)
    text(375,340,f"{'？' if unknown else distance}公分",28)
    text(380,400,f"比例尺 1:{scale}")


def short_division(a,b,p):
    # 一直除到兩數互質為止（最後一列是互質的兩數）
    steps, x, y = [], a, b
    d = p
    while d:
        steps.append((d, x, y)); x, y = x//d, y//d
        d = next((k for k in range(2, min(x, y)+1) if x % k == 0 and y % k == 0), 0)
    rows = len(steps)+1
    top, gap = 60, min(95, 300/rows)
    box(205,top-10,350,gap*rows+20,BLUE)
    for i,(d,u,v) in enumerate(steps):
        yy = top+gap*i+gap/2
        text(255,yy,d,40)
        line((300,yy-gap/2+8),(300,yy+gap/2-4),(520,yy+gap/2-4))
        text(360,yy,u,40); text(465,yy,v,40)
    yy = top+gap*len(steps)+gap/2
    text(360,yy,x,40); text(465,yy,y,40)


def sticks(n, square):
    for row in range(1,4):
        left,y = 185,70+125*(row-1)
        text(90,y+28,f"第{row}個")
        for i in range(row+n):
            x=left+i*57
            if square:
                box(x,y,57,57,BLUE)
            else:
                polygon([(x,y+57),(x+57,y+57),(x+28.5,y+8)])


def combinations(a,b):
    for i in range(a):
        x = 145+i*470/max(1,a-1)
        line((380,75),(x,175))
        for j in range(b):
            x2=x+(j-(b-1)/2)*51
            line((x,175),(x2,300))
            circle(x2,300,20,BLUE)
            text(x2,300,j+1,27)
        circle(x,175,24,BLUE)
        text(x,175,chr(65+i),28)
    text(380,52,"選擇")


def curved_perimeter(style, size, unknown):
    x,y,r = 380,210,115
    if style == "semicircle":
        draw.pieslice((x-r,y-r,x+r,y+r),180,360,fill=BLUE,outline=INK,width=3)
    else:
        left,right = 275,485
        draw.rectangle((left,y-r,right,y+r),fill=BLUE)
        draw.pieslice((left-r,y-r,left+r,y+r),90,270,fill=BLUE)
        draw.pieslice((right-r,y-r,right+r,y+r),270,450,fill=BLUE)
        draw.arc((left-r,y-r,left+r,y+r),90,270,fill=INK,width=3)
        draw.arc((right-r,y-r,right+r,y+r),270,450,fill=INK,width=3)
        line((left,y-r),(right,y-r))
        line((left,y+r),(right,y+r))
        line((left,y-r),(left,y+r),color="#777777")
        text(380,57,f"{size}公分")
    text(x,380,f"直徑 {'？' if unknown else size}公分")


def parallel_lines(spacing, perpendicular):
    for y in (150,150+spacing):
        line((165,y),(595,y))
    if perpendicular:
        line((380,70),(380,370))
        for y in (150,150+spacing):
            line((380,y-18),(398,y-18),(398,y))


def tally(labels, values):
    for i,(label,value) in enumerate(zip(labels,values)):
        y=95+110*i
        text(160,y,label)
        for j in range(value):
            x=260+120*(j//5)
            strokes = [((x,y-25),(x+50,y-25)),((x+25,y-25),(x+25,y+25)),
                       ((x+25,y),(x+49,y)),((x+5,y-6),(x+5,y+25)),
                       ((x-4,y+25),(x+54,y+25))]
            line(*strokes[j%5],weight=4)



RENDERERS.update(labeled_polygon=labeled_polygon,gauge=gauge,table=table,money=money,price_tags=price_tags,
                 interval=interval,solid=solid,map=map_view,short=short_division,
                 curved_perimeter=curved_perimeter,parallel_lines=parallel_lines,tally=tally,
                 sticks=sticks,combinations=combinations)


def pair(grade,unit,slug,kind,values,tags,desc, unknown_position=None):
    for unknown in (False,True):
        args = list(values)
        if unknown_position is not None:
            args.insert(unknown_position,unknown)
        else:
            args[-1] = "？" if unknown else args[-1]
        make(grade,unit,f"{slug}-{'unknown' if unknown else 'given'}",kind,args,
             tags,desc+("，其中一項以問號標示" if unknown else ""))


def generate():
    for grade, unit, labels in [
        (3,"10000 以內的數",["千位","百位","十位","個位"]),
        (4,"一億以內的數",["千萬","百萬","十萬","萬位","千位","百位","十位","個位"])
    ]:
        for i in range(5 if grade==3 else 3):
            digits = [str((2*i+3*j+1)%10) for j in range(len(labels))]
            n = "".join(digits)
            make(grade,unit,f"place-value-{i+1}","board",(labels,digits),
                 ["定位板","位值","千位","個位",n],f"定位板上的數字為 {n}")
    for i, values in enumerate([(1000,100,10,1),(500,100,50,5),(100,50,10,5,1),
                                (1000,500,100),(50,10,10,1)]):
        make(3,"10000 以內的數",f"money-{i+1}","money",(values,),
             ["錢幣","紙鈔","面額","元",*[f"{v}元" for v in sorted(set(values))]],
             "不同面額的錢幣與紙鈔排列")
    for i,(step,start,stop) in enumerate([(10,0,4),(10,5,2),(100,1,5),(100,5,0)]):
        pair(3,"加法和減法",f"number-line-{i+1}","timeline",
             ([i*step for i in range(6)],start,stop,str(abs(stop-start)*step)),
             ["數線","跳格","刻度",str(step),str(stop*step)],"數線上標示跳格的起點與終點")
    for g,unit,style in [(3,"乘法",False),(3,"乘法",True),(3,"除法",True),
                         (4,"乘法、除法",True),(5,"倍數與因數",False),
                         (5,"公倍數與公因數",True)]:
        sizes = [(1,12),(2,6),(3,4),(4,3)] if unit=="倍數與因數" else [(3,4),(4,5),(4,6),(5,7),(6,8)]
        for r,c in sizes:
            prefix = ("division" if unit=="除法" else "common-factors" if unit=="公倍數與公因數"
                      else "trays" if style else "array")
            description = f"{r}排，每排{c}個圓點"
            for unknown in (False,True):
                caption = f"每盤 {'？' if unknown else c}個" if style else f"{r} × {'？' if unknown else c}"
                make(g,unit,f"{prefix}-{r}x{c}-{'unknown' if unknown else 'given'}",
                     "grouped",(r,c,caption,style),
                     ["點陣" if not style else "分盤","排列",f"{r}排",f"{c}個",f"{r}×{c}"],description)
    for i,(n,mm,item) in enumerate([(8,45,"鉛筆"),(8,37,"橡皮擦"),(8,65,"緞帶"),
                                   (10,73,"鉛筆"),(10,52,"線段"),(10,66,"線段")]):
        pair(3,"公分和毫米",f"ruler-{i+1}","ruler",(n,mm,item),
             ["直尺","毫米","刻度",item,f"{mm}毫米"],f"直尺上的{item}從 0 刻度對齊",3)
    for g,unit,style,angles in [(3,"角","angle",[35,60,90,125]),
                                (4,"角度","protractor",[30,45,60,75,90,105,120,150]),
                                (4,"角度","angle",[90,180,360]),
                                (5,"扇形","sector",[30,45,60,90,120,180,240,270,300,330]),
                                (6,"圓周長與扇形周長","sector",[45,60,90,120,135,150,180])]:
        for i,a in enumerate(angles):
            r = 6+i%5*2
            pair(g,unit,f"{style}-{a}-r{r}","sector",(a,r,style),
                 ["量角器" if style=="protractor" else "扇形" if style=="sector" else "旋轉角",
                  "角度","頂點",f"{a}度",f"{r}公分",*(["圓心角","半徑","弧"] if style=="sector" else ["量角"] if style=="protractor" else [])],
                 f"扇形，半徑 {r} 公分、圓心角 {a} 度" if style=="sector" else f"以兩條射線標出 {a} 度的角",2)
    for g,unit in [(3,"圓"),(6,"圓周長與扇形周長")]:
        for r in (5,7,8,9,10,12):
            pair(g,unit,f"circle-diameter-{2*r}","sector",(90,r,"diameter"),
                 ["圓形","圓心","直徑","半徑",f"{2*r}公分"],"圓形及通過圓心的直徑",2)
    for g,unit,style,specs in [
        (3,"分數","pie",[(2,1),(3,1),(4,3),(5,2),(6,5),(8,3),(10,7)]),
        (3,"分數","bar",[(4,3),(6,1),(8,5),(9,4)]),
        (4,"分數","bar",[(3,2),(4,1),(5,3),(6,5),(7,2),(8,3),(9,8),(10,3)]),
        (5,"擴分與約分","equivalent",[(2,1),(3,1),(3,2),(4,1),(4,3),(5,2)]),
        (5,"乘以幾分之一","bar",[(4,1),(6,1),(8,1),(10,1)]),
        (6,"分數除法","bar",[(4,3),(5,2),(6,5),(7,3),(8,5),(10,7)])
    ]:
        for d,n in specs:
            pair(g,unit,f"{style}-{n}-over-{d}","fraction",(d,n,style,f"{n}/{d}"),
                 ["分數條" if style!="pie" else "圓形","等分","塗色",f"{n}/{d}",f"{d}等分"],
                 f"圖形平分成 {d} 份，塗色 {n} 份")
    for g in (3,4):
        for hour,minute in ([(2,0),(6,0),(8,30),(3,15),(10,40),(11,55)] if g==3
                            else [(13,0),(18,30),(22,15)]):
            pair(g,"時間",f"clock-{hour}-{minute}","clock",(hour,minute),
                 ["時鐘","鐘面","時針",f"{hour}時",f"{minute}分"],"鐘面上的時針與分針",2)
        for start in (7,14):
            pair(g,"時間",f"time-line-{start}","timeline",
                 ([f"{start+i}:00" for i in range(5)],0,3,"3小時"),
                 ["時間線","經過時間","小時",f"{start}:00",f"{start+3}:00"],"時間線上的起訖時刻")
    for i in range(3):
        for cup in (False,True):
            cap = (500+250*i) if cup else (500+500*i)
            n = cap*(i+2)//5
            make(3,"容量、重量",f"{'cup' if cup else 'scale'}-{cap}","gauge",(cap,n,cup),
                 ["量杯" if cup else "秤面","刻度","毫升" if cup else "公克",str(cap),
                  f"{n}{'毫升' if cup else '公克'}"],"量杯液面與刻度" if cup else "秤面指針與刻度")
        make(3,"統計表",f"table-{i+1}","table",(["甲","乙","丙","丁"],[i+3,i+5,i+2,i+6]),
             ["統計表格","表格","人數","項目",str(i+5)],"四個項目的人數統計表")
    for w,h in [(3,3),(4,3),(5,4),(6,5),(6,6),(8,6),(4,4),(5,5),(6,4),(7,5)]:
        cells = [(x,y) for x in range(w-1) for y in range(h) if x==0 or y<h-1]
        make(3,"周長與面積",f"grid-area-{h}x{w}-shade{len(cells)}","grid",
             (w,h,cells,"每格 1 平方公分"),
             ["方格紙","方格","面積","塗色","平方公分",f"{h}×{w}"],f"{h}×{w} 方格紙，塗色 {len(cells)} 格")
        make(3,"周長與面積",f"grid-perimeter-{h}x{w}","grid",
             (w,h,cells,"每格邊長 1 公分"),
             ["方格紙","周長","邊長","公分",f"{h}×{w}"],"方格紙上用著色呈現圖形的邊界")
    for n in [7,15,22,35,42,56,70,85]:
        cells = [(k%10,k//10) for k in range(n)]
        pair(4,"小數",f"hundred-grid-{n}","grid",(10,10,cells,f"{n/100:g}"),
             ["百格板","方格紙","塗色",f"{n/100:g}","百分位"],f"百格板塗色 {n} 格")
    for i in range(3):
        labels = [f"{(10+i*20+j)/100:.2f}" for j in range(6)]
        pair(4,"小數",f"decimal-line-{i+1}","timeline",(labels,1,4,labels[4]),
             ["數線","百分位","刻度","二位小數",labels[4]],"小數數線及標出的兩點")
    for grade,unit,styles,sizes in [
        (4,"周長與面積",["rectangle","l"],[(4,4),(6,4),(8,6),(10,6),(8,8)]),
        (4,"三角形",["triangle","right"],[(4,3),(6,4),(8,5),(7,6)]),
        (4,"四邊形",["parallelogram","trapezoid","rectangle"],[(5,3),(6,4),(8,6)]),
        (5,"面積",["triangle","parallelogram","trapezoid"],[(5,3),(6,4),(8,5),(10,6)]),
    ]:
        for style in styles:
            name = dict(rectangle="長方形",l="L形",triangle="三角形",right="直角三角形",
                        parallelogram="平行四邊形",trapezoid="梯形")[style]
            for base,tall in sizes:
                for on_grid in ((True,False) if grade==5 else (grade==4 and unit=="周長與面積",)):
                    pair(grade,unit,f"{style}-{base}x{tall}-{'grid' if on_grid else 'plain'}",
                         "shape",(style,base,tall,on_grid),
                         [name if name!=unit else "圖形","方格紙" if on_grid else "圖形高度",
                          "邊長","底和高",f"{base}公分",f"{tall}公分"],
                         f"{name}標示底邊與高度",3)
    for n in (3,4):
        for unknown in (False,True):
            values = ["60°"]*3 if n==3 else ["90°"]*4
            if unknown:
                values[0]="？°"
            make(5,"平面圖形",f"interior-{n}-{'unknown' if unknown else 'given'}",
                 "labeled_polygon",(n,values,True),
                 ["三角形" if n==3 else "正方形","內角","角度","頂點","60度" if n==3 else "90度"],
                 "正三角形的內角" if n==3 else "正方形的內角")
    for g,unit,kinds in [(4,"長條圖",["bar","horizontal"]),(5,"折線圖",["line","bar"])]:
        for kind in kinds:
            for i in range(4):
                values = [4+2*i,8,12,6+2*i]
                second = [8,10,8+2*i,4] if kind=="line" and i%2 else None
                labels = ["週一","週二","週三","週四"] if kind!="horizontal" else ["甲","乙","丙","丁"]
                make(g,unit,f"{kind}-chart-{i+1}","chart",(labels,values,2,"人數（人）",kind,second),
                     ["統計圖","刻度","人數","每格2人","座標軸",str(values[0])],
                     "以每格 2 人為刻度的統計圖")
    for sides,pyramid,net in [(3,False,False),(4,False,False),(5,False,False),(6,False,False),
                              (0,False,False),(3,True,False),(4,True,False),(3,True,True),(4,False,True)]:
        name = ("三角錐" if sides==3 else "四角錐") if pyramid else {
            0:"圓柱",3:"三角柱",4:"四角柱",5:"五角柱",6:"六角柱"}[sides]
        make(5,"立體形體",f"solid-{sides}-{int(pyramid)}-{int(net)}","solid",
             (sides,pyramid,net),[name,"展開圖" if net else "立體圖","頂點","邊","面"],
             f"{name}的"+("展開圖" if net else "示意圖"))
    for i,values in enumerate([(35,50,80),(12,24,48),(15,30,60)]):
        make(5,"整數四則",f"prices-{i+1}","price_tags",(values,),
             ["價牌","買東西","元","價格",*[f"{v}元" for v in values]],"三件物品的價格")
    for a,b,c in [(2,2,2),(2,3,3),(3,2,2),(2,3,5),(3,3,5),(2,5,7)]:
        make(6,"最大公因數與最小公倍數",f"factor-tree-{a*b*c}","tree",(a,b,c),
             ["質因數","因數分解","樹狀圖","分解",str(a*b*c)],"以樹狀圖分解整數")
    for a,b,p in [(12,18,2),(18,24,3),(16,20,4),(30,45,5)]:
        make(6,"最大公因數與最小公倍數",f"short-division-{a}-{b}","short",(a,b,p),
             ["短除法","公因數","公倍數",str(a),str(b)],"兩數短除法的第一步")
    for a,b in [(2,4),(3,5),(3,6),(4,8),(5,7),(6,8),(4,10),(6,12)]:
        pair(6,"兩量關係",f"comparison-{a}-{b}","comparison",(a,b,"人"),
             ["線段圖","基準量","比較量",f"{a}人",f"{b}人"],"兩班人數的線段比較",3)
    for a,b in [(1.5,0.5),(2.4,0.8),(3.6,1.2),(4.8,1.6)]:
        pair(6,"小數除法",f"rope-{int(a*10)}-{int(b*10)}","comparison",(a,b,"公尺"),
             ["繩子","線段圖","平分",f"{a}公尺",f"{b}公尺"],"兩段繩子的長度",3)
    for first,second,prefix in [("藍球","白球","balls"),("果汁","水","drink")]:
        for a,b in [(2,3),(3,2),(4,5),(5,3)]:
            pair(6,"比與比值",f"{prefix}-{a}-{b}","ratio",(a,b,first,second),
                 ["比值","數量",first,second,f"{a}:{b}"],"兩種物品的數量對照",4)
    for style in ("rectangle","triangle","l"):
        for w,h in [(3,2),(4,4),(5,3)]:
            pair(6,"放大、縮小與比例尺",f"scale-{style}-{w}x{h}","scale_pair",(w,h,style),
                 ["方格紙","原圖","放大圖","2倍",f"{w}×{h}"],"方格紙上的原圖和二倍放大圖",3)
    for scale,distance in [(1000,3),(2000,4),(5000,6)]:
        pair(6,"放大、縮小與比例尺",f"map-{scale}","map",(scale,distance),
             ["地圖","比例尺","學校","圖書館",f"1:{scale}",f"{distance}公分"],
             "標有三處地點與比例尺的地圖",2)
    for i,gap in enumerate([2,3,4,5,6]):
        pair(6,"怎樣解題",f"interval-{i+1}","interval",(i%3+4,gap),
             ["間隔","種樹","距離","公尺",f"{gap}公尺","照片","排成一列","每兩"],"等距排列的樹（或一列照片）與間隔距離",2)
    for n in (0,1,2):
        for square in (False,True):
            make(6,"怎樣解題",f"sticks-{n}-{int(square)}","sticks",(n,square),
                 ["火柴棒","數形規律","正方形" if square else "三角形","排列",f"{n+1}個"],
                 "火柴棒排列的前三個圖形")
    for a,b in [(2,2),(2,3),(2,4),(3,2),(3,3)]:
        make(6,"怎樣解題",f"combinations-{a}-{b}","combinations",(a,b),
             ["組合","樹狀圖","選擇",f"{a}種",f"{b}個"],"用樹狀圖列出兩階段的選擇")
    for i in range(3):
        make(3,"統計表",f"tally-{i+1}","tally",(["甲","乙","丙"],[3+i,5+i,8+i]),
             ["畫記","統計","人數","記號",f"{5+i}人"],"以畫記記錄三個項目的人數")
        make(4,"四邊形",f"line-relations-{i+1}","parallel_lines",(70+i*22,i!=0),
             ["垂直","平行","直線","直角","90度"],"兩條平行線與垂直線的示意圖" if i else "兩條平行線")
    for style,name in [("semicircle","半圓"),("stadium","跑道形")]:
        for size in (8,10,14,20):
            pair(6,"圓周長與扇形周長",f"{style}-{size}","curved_perimeter",(style,size),
                 [name,"弧長","直徑","公分",f"{size}公分"],f"{name}與半圓的直徑",2)
    for den in (2,3,4,6,8):
        pair(5,"扇形",f"fraction-of-circle-{den}","fraction",(den,1,"pie",f"1/{den}"),
             ["圓形","等分","塗色",f"1/{den}",f"{den}等分"],f"圓形的 {den} 等分中有一份塗色")
    for size in (6,8,10):
        make(4,"三角形",f"equilateral-{size}","labeled_polygon",(3,[f"{size}公分"]*3),
             ["正三角形","等邊三角形","邊長","等長",f"{size}公分"],"正三角形的三邊等長")
    for style,name in [("rectangle","長方形"),("triangle","三角形"),("l","L形")]:
        for w,h in [(3,2),(4,4),(5,3)]:
            pair(6,"放大、縮小與比例尺",f"shrink-{style}-{w}x{h}","scale_pair",(w,h,style,True),
                 ["方格紙","原圖","縮小圖","1/2倍",name,f"{w*2}×{h*2}"],"方格紙上的原圖和二分之一倍縮小圖",3)
    target = ROOT / "data" / "index.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(index,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


if __name__ == "__main__":
    generate()
