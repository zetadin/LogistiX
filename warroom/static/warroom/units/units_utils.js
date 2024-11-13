//fetch units (platoons & companies) data from the server
async function fetch_JSON(url) {
    var JSON;
    try{
        const map_response = await fetch(url);
        JSON = await map_response.json();
    }
    catch(error){
        console.log("Could not fetch or JSON data: "+error);
    }
    return(JSON);
}

//update units based on JSON
function update_units() {
    units = []
    fetch_JSON(platoons_url).then((result)=>{
        const platoons_JSON=result;
        // console.log(platoons_JSON);

        for(var h = 0; h<platoons_JSON.length; h++) {
            const p_JSON = platoons_JSON[h];
            var P = new Platoon(p_JSON.x, p_JSON.y);
            P.color = factionColors[p_JSON.faction];
            P.iconURL = map.ruleset.units[p_JSON.type].IconURL;
            units.push(P);
            console.log(P);
        }
    
    //TODO: do the same for companies


    map.units = units

    });
}