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
async function update_map() {
    var temp_map = new Map(0,0,init=false);
    fetch_map_data().then((result)=>{
        const map_JSON=result[0];
        console.log(map_JSON);

        for(var h = 0; h<map_JSON.hexes.length; h++) {
            const hex_JSON = map_JSON.hexes[h];
            var hex = new Hex(hex_JSON.x, hex_JSON.y);
            hex.color = hex_JSON.terrain.color;
            temp_map.hexes.push(hex);
        }

    map = temp_map;
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
