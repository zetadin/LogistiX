// fmod function from https://gist.github.com/wteuber/6241786
Math.fmod = function (a,b) { return Number((a - (Math.floor(a / b) * b)).toPrecision(8)); };

// argmax from https://gist.github.com/engelen/fbce4476c9e68c52ff7e5c2da5c24a28?permalink_comment_id=3202905#gistcomment-3202905
function argMax(array) { return [].reduce.call(array, (m, c, i, arr) => c > arr[m] ? i : m, 0); }


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
    let hexes={}
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
            for(let h = 0; h<map_JSON.chunks[c].hexes.length; h++) {
                const hex_JSON = map_JSON.chunks[c].hexes[h];
                const hex_ter = terains_JSON[hex_JSON.terrain];
                var hex = new Hex(hex_JSON.x, hex_JSON.y);
                hex.color = hex_ter.color;
                hex.iconURL = "/static/" + hex_ter.IconURL;
                hex.terrain = hex_JSON.terrain;
                hex.control = Array.from(hex_JSON.control, parseFloat);
                hex.controller = argMax(hex.control);
                if(hex.control[hex.controller]<0.70){
                    hex.controller = -1;
                }


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

            // loop through Facilities in chunk
            if('facilities' in map_JSON.chunks[c]){
                for(let f = 0; f<map_JSON.chunks[c].facilities.length; f++) {
                    const fac_JSON = map_JSON.chunks[c].facilities[f];
                    var fac = new Facility(fac_JSON.x, fac_JSON.y);
                    fac.iconURL = "/static/" + rules_JSON.facilities[fac_JSON.type].IconURL;
                    fac.type = fac_JSON.type;
                    fac.owned = (fac_JSON.owned === undefined) ? 0 : fac_JSON.owned; // 0 if undefined in JSON
                    fac.name = fac_JSON.name;
                    let hex_coord = String(fac_JSON.x)+"_"+String(fac_JSON.y);
                    fac.hex = hexes[hex_coord];

                    if(fac.owned){
                        // owned facilities are first in the list, so prepend this one
                        hexes[hex_coord].facilities.unshift(fac);
                    }
                    else{
                        // facilities belonging to others are appended
                        hexes[hex_coord].facilities.push(fac);
                    }
                }
            }
        }

        // Precalculate neighbour keys
        hex_keys = Object.keys(hexes);
        for (let h = 0; h < hex_keys.length; h++) {
            let cur_hex = hexes[hex_keys[h]];
            let neighbour_dict = [];

            // N
            let next_key = String(cur_hex.x)+"_"+String(cur_hex.y-1);
            if(next_key in hexes){
                neighbour_dict["N"] = next_key;}

            // NE
            next_key = String(cur_hex.x+1)+"_"+String(cur_hex.y+(cur_hex.x%2==0 ? -1 : 0));
            if(next_key in hexes){
                neighbour_dict["NE"] = next_key;}

            // SE
            next_key = String(cur_hex.x+1)+"_"+String(cur_hex.y+(cur_hex.x%2==0 ? 0 : 1));
            if(next_key in hexes){
                neighbour_dict["SE"] = next_key;}

            // S
            next_key = String(cur_hex.x)+"_"+String(cur_hex.y+1);
            if(next_key in hexes){
                neighbour_dict["S"] = next_key;}

            // SW
            next_key = String(cur_hex.x-1)+"_"+String(cur_hex.y+(cur_hex.x%2==0 ? 0 : 1));
            if(next_key in hexes){
                neighbour_dict["SW"] = next_key;}

            // NW
            next_key = String(cur_hex.x-1)+"_"+String(cur_hex.y+(cur_hex.x%2==0 ? -1 : 0));
            if(next_key in hexes){
                neighbour_dict["NW"] = next_key;}
                
            hexes[hex_keys[h]].neighbour_dict = neighbour_dict;
        }



        map.hexes = hexes;
        map.ruleset = rules_JSON;

        update_units();    
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
