//fetch map data from the server
async function fetch_map_data() {
    var map_JSON;
    try{
        const map_response = await fetch(map_url);
        map_JSON = await map_response.json();
    }
    catch(error){
        console.log("Could not fetch or parse map data: "+error);
    }
    return(map_JSON);
}  

//update map based on JSON
function update_map() {
    hexes=[]
    fetch_map_data().then((result)=>{
        const map_JSON=result[0];
        // console.log(map_JSON);

        for(var h = 0; h<map_JSON.hexes.length; h++) {
            const hex_JSON = map_JSON.hexes[h];
            var hex = new Hex(hex_JSON.x, hex_JSON.y);
            hex.color = hex_JSON.terrain.color;
            hex.iconURL = hex_JSON.terrain.iconURL;

            if("river_dir" in hex_JSON.improvements){
                hex.river_dir = parseInt(hex_JSON.improvements.river_dir)
                console.log("Found river at", hex_JSON.x, hex_JSON.y, "going in direction", hex_JSON.improvements.river_dir)
            }

            // lake generation debug
            // hex.debug_text = `${hex_JSON.improvements.water_body_id},${hex_JSON.improvements.traversed_n}`;
            // hex.debug_text = `${hex_JSON.improvements.x},${hex_JSON.improvements.y}`;

            hexes.push(hex);
        }

    map.hexes = hexes;
    });
}


//Mouse detection based on https://stackoverflow.com/a/24384882
//Function to get the mouse position
function getMousePos(canvas, event) {
    var rect = canvas.getBoundingClientRect();
    return {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
    };
}
//Function to check whether a point is inside a rectangle
function isInside(pos, rect){
    return pos.x > rect.x && pos.x < rect.x+rect.width && pos.y < rect.y+rect.height && pos.y > rect.y
}
