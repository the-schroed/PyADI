"""FastAPI demo: serve ADI images from quaternion input, with a control UI."""
from io import BytesIO

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, StreamingResponse

from adi.frames import rpy_deg
from adi.render.pillow_backend import render_sphere

app = FastAPI(title="ADI Demo")


@app.get("/", response_class=HTMLResponse)
def index():
    return """<!doctype html>
<html><head><title>ADI</title></head>
<body>
<h1>ADI Controls</h1>
<label>Roll <input id="roll" type="range" min="-180" max="180" value="20"> <input id="rolln" type="number" min="-180" max="180" value="20"></label><br>
<label>Pitch <input id="pitch" type="range" min="-90" max="90" value="-10"> <input id="pitchn" type="number" min="-90" max="90" value="-10"></label><br>
<label>Yaw <input id="yaw" type="range" min="-180" max="180" value="30"> <input id="yawn" type="number" min="-180" max="180" value="30"></label><br>
<label>Size <input id="size" type="range" min="200" max="800" value="400"> <input id="sizen" type="number" min="200" max="800" value="400"></label><br>
<label>Grid <input id="grid" type="range" min="5" max="45" value="15"> <input id="gridn" type="number" min="5" max="45" value="15"></label><br>
<img id="adi" src="/adi.png" width="400">
<script>
function sync(sliderId,numId){
  const s=document.getElementById(sliderId), n=document.getElementById(numId);
  s.addEventListener('input',()=>{n.value=s.value;update();});
  n.addEventListener('input',()=>{s.value=n.value;update();});
}
function update(){
  const r=document.getElementById('roll').value;
  const p=document.getElementById('pitch').value;
  const y=document.getElementById('yaw').value;
  const s=document.getElementById('size').value;
  const g=document.getElementById('grid').value;
  document.getElementById('adi').src=`/adi_rpy.png?roll=${r}&pitch=${p}&yaw=${y}&size=${s}&grid=${g}&t=${Date.now()}`;
}
sync('roll','rolln');sync('pitch','pitchn');sync('yaw','yawn');sync('size','sizen');sync('grid','gridn');
update();
</script>
</body></html>"""


@app.get("/adi.png")
def adi_image(
    w: float = Query(1.0),
    x: float = Query(0.0),
    y: float = Query(0.0),
    z: float = Query(0.0),
    size: int = Query(400),
    grid: int = Query(60),
):
    roll, pitch, yaw = rpy_deg([w, x, y, z])
    img = render_sphere(roll, pitch, yaw, size=size, grid=grid)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@app.get("/animate", response_class=HTMLResponse)
def animate():
    return """<!doctype html>
<html><head><title>ADI Animate</title></head>
<body>
<h1>ADI 1 Hz Simulation</h1>
<img id="adi" src="/adi_rpy.png" width="400">
<script>
let t=0;
setInterval(()=>{
  const roll=30*Math.sin(2*Math.PI*0.1*t);
  const pitch=20*Math.sin(2*Math.PI*0.07*t+1);
  const yaw=15*Math.sin(2*Math.PI*0.05*t+2);
  document.getElementById('adi').src=`/adi_rpy.png?roll=${roll.toFixed(2)}&pitch=${pitch.toFixed(2)}&yaw=${yaw.toFixed(2)}&size=400&grid=30&t=${Date.now()}`;
  t+=1;
},1000);
</script>
</body></html>"""


@app.get("/adi_rpy.png")
def adi_rpy(
    roll: float = Query(0.0),
    pitch: float = Query(0.0),
    yaw: float = Query(0.0),
    size: int = Query(400),
    grid: int = Query(15),
):
    img = render_sphere(roll, pitch, yaw, size=size, grid=grid)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
