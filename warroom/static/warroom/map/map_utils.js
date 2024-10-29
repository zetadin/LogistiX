// fmod function from https://gist.github.com/wteuber/6241786
Math.fmod = function (a,b) { return Number((a - (Math.floor(a / b) * b)).toPrecision(8)); };


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

//fetch terrain types
async function fetch_RuleSet() {
    var rules_JSON;
    try{
        const rules_response = await fetch(RuleSet_url);
        rules_JSON = await rules_response.json();
    }
    catch(error){
        console.log("Could not fetch or parse rules: "+error);
    }
    return(rules_JSON);
}  

//update map based on JSON
function update_map() {
    hexes={}
    Promise.all([
        fetch_RuleSet(),
        fetch_map_data()
    ]).then(results=>{
        const rules_JSON=results[0];
        const terains_JSON=rules_JSON.terrains;

        const map_JSON=results[1][0];

        // loop through chunks
        for(var c = 0; c<map_JSON.chunks.length; c++) {
           
        
            // loop through hexes in chunk
            for(var h = 0; h<map_JSON.chunks[c].hexes.length; h++) {
                const hex_JSON = map_JSON.chunks[c].hexes[h];
                const hex_ter = terains_JSON[hex_JSON.terrain];
                var hex = new Hex(hex_JSON.x, hex_JSON.y);
                hex.color = hex_ter.color;
                hex.iconURL = "/static/" + hex_ter.IconURL;
                hex.terrain = hex_JSON.terrain;

                if("river_dir" in hex_JSON.improvements){
                    hex.river_dir = parseInt(hex_JSON.improvements.river_dir)
                    // console.log("Found river at", hex_JSON.x, hex_JSON.y, "going in direction", hex_JSON.improvements.river_dir)
                    // hex.debug_text = `${hex_JSON.improvements.river_dir}`;
                }

                // lake generation debug
                // hex.debug_text = `${hex_JSON.improvements.water_body_id},${hex_JSON.improvements.traversed_n}`;
                // hex.debug_text = `${hex_JSON.improvements.x},${hex_JSON.improvements.y}`;

                // hexes.push(hex);
                hexes[String(hex_JSON.x)+"_"+String(hex_JSON.y)]=hex;
            }
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
