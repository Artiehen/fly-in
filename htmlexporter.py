import json


class HTMLExporter:

    def __init__(self, hubs, connections, frames):
        self.hubs = hubs
        self.connections = connections
        self.frames = frames

    def export(self, filename="simulation.html"):
        hubs_data = {}

        for name, hub in self.hubs.items():

            hubs_data[name] = {
                "x": hub.x,
                "y": hub.y,
                "kind": hub.kind,
                "zone": hub.zone
            }

        connections_data = []

        for c in self.connections:

            connections_data.append(
                {
                    "from": c.from_hub,
                    "to": c.to_hub
                }
            )

        xs = [
            h["x"]
            for h in hubs_data.values()
        ]

        ys = [
            h["y"]
            for h in hubs_data.values()
        ]

        bounds_data = {

            "min_x": min(xs),
            "max_x": max(xs),

            "min_y": min(ys),
            "max_y": max(ys)

        }
        # -------------------------
        # HTML template
        # -------------------------

        html = r"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>
Drone Simulation
</title>


<style>

body {

    background:#202020;
    color:white;

    font-family:Arial;
    text-align:center;

}


canvas {

    background:#111;

    border:2px solid white;

}


button {

    margin:5px;

    padding:8px 15px;

    font-size:16px;

}

</style>

</head>


<body>


<h1>
Drone Simulation
</h1>


<canvas id="canvas"
        width="1000"
        height="800">
</canvas>


<br>


<button onclick="play()">
Play
</button>


<button onclick="pause()">
Pause
</button>


<button onclick="nextFrame()">
Next
</button>


<h3 id="turn">
Turn: 0
</h3>



<script>


const hubs =
{{HUB_DATA}};


const edges =
{{EDGE_DATA}};


const frames =
{{FRAME_DATA}};


const bounds =
{{BOUND_DATA}};



const canvas =
document.getElementById("canvas");


const ctx =
canvas.getContext("2d");



let frame = 0;

let timer = null;



// -------------------------
// Scaling and centering
// -------------------------

const mapWidth =
bounds.max_x - bounds.min_x;


const mapHeight =
bounds.max_y - bounds.min_y;



const scale =
Math.min(

    (canvas.width - 150) /
    Math.max(mapWidth,1),

    (canvas.height - 150) /
    Math.max(mapHeight,1)

);



const offsetX =
(
    canvas.width -
    mapWidth * scale
) / 2;



const offsetY =
(
    canvas.height -
    mapHeight * scale
) / 2;



function transform(x,y)
{

    return [

        offsetX +
        (x - bounds.min_x)
        * scale,


        canvas.height -
        offsetY -
        (y - bounds.min_y)
        * scale

    ];

}



// -------------------------
// Draw
// -------------------------

function draw()
{

    ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    );



    // Draw connections

    ctx.strokeStyle = "gray";

    ctx.lineWidth = 2;


    edges.forEach(edge => {

        let a =
        hubs[edge.from];


        let b =
        hubs[edge.to];


        let p1 =
        transform(a.x,a.y);


        let p2 =
        transform(b.x,b.y);


        ctx.beginPath();

        ctx.moveTo(
            p1[0],
            p1[1]
        );


        ctx.lineTo(
            p2[0],
            p2[1]
        );


        ctx.stroke();


    });



    // Draw hubs

    for(let name in hubs)
    {

        let hub =
        hubs[name];


        let pos =
        transform(
            hub.x,
            hub.y
        );


        if(hub.kind === "start")

            ctx.fillStyle =
            "lime";


        else if(hub.kind === "end")

            ctx.fillStyle =
            "red";


        else

            ctx.fillStyle =
            "white";



        ctx.beginPath();


        ctx.arc(
            pos[0],
            pos[1],
            12,
            0,
            Math.PI*2
        );


        ctx.fill();



        ctx.fillStyle =
        "yellow";


        ctx.fillText(
            name,
            pos[0]-10,
            pos[1]-18
        );


    }



    // Draw drones

    let drones =
    frames[frame];


    let colors =
    [
        "cyan",
        "orange",
        "lime",
        "pink",
        "magenta",
        "gold",
        "deepskyblue",
        "violet"
    ];


    let index = 0;


    let occupied = {};



    for(let drone in drones)
    {

        let hubName =
        drones[drone];


        let hub =
        hubs[hubName];


        let pos =
        transform(
            hub.x,
            hub.y
        );



        if(!occupied[hubName])
            occupied[hubName]=0;



        let angle =
        occupied[hubName]
        *
        Math.PI/4;



        pos[0] +=
        Math.cos(angle)*18;


        pos[1] +=
        Math.sin(angle)*18;



        occupied[hubName]++;



        ctx.fillStyle =
        colors[index %
        colors.length];


        ctx.beginPath();


        ctx.arc(
            pos[0],
            pos[1],
            7,
            0,
            Math.PI*2
        );


        ctx.fill();



        ctx.fillStyle =
        "white";


        ctx.fillText(
            drone,
            pos[0]+10,
            pos[1]
        );


        index++;

    }



    document.getElementById("turn")
    .innerHTML =
    "Turn: " + frame;

}



// -------------------------
// Controls
// -------------------------

function nextFrame()
{

    if(frame < frames.length-1)

        frame++;


    draw();

}



function play()
{

    if(timer)
        return;


    timer =
    setInterval(
        function()
        {

            if(frame >= frames.length-1)
            {

                pause();

                return;

            }


            frame++;

            draw();


        },
        700
    );

}



function pause()
{

    clearInterval(timer);

    timer=null;

}



draw();


</script>


</body>

</html>
"""

        # -------------------------
        # Insert Python data
        # -------------------------

        html = html.replace(
            "{{HUB_DATA}}",
            json.dumps(hubs_data)
        )

        html = html.replace(
            "{{EDGE_DATA}}",
            json.dumps(connections_data)
        )

        html = html.replace(
            "{{FRAME_DATA}}",
            json.dumps(self.frames)
        )

        html = html.replace(
            "{{BOUND_DATA}}",
            json.dumps(bounds_data)
        )
        # -------------------------
        # Write file
        # -------------------------
        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(html)

        print(
            f"Created {filename}"
        )
