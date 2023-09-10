
var imgDict = {};


// async handler for image fetching/decoding
async function addImageProcess(iconUrl){
    // fetch svg, convert responce to text, and save into svg_data variable
    fetch(iconUrl)
    .then( response => {
        // throw new Error('catch test');
        return response.text();
    })       // after resolve of fetch ask for text of responce
    .catch ( error =>{
        console.log("Could not fetch"+iconUrl+": "+error);
        // so put a ? in a square instead
        return new Promise((resolve,reject) => {
            resolve(`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" height="100" width="100">
            <g style="fill:none; stroke:#000000; stroke-width:3">
                <path d="M1 1 L99 1 L99 99 L1 99 Z"/>
            </g>
            <g style="font: bold 100px sans-serif; fill:none; stroke:#000000; stroke-width:1">
                <text x="80" y="85" text-anchor="middle">?</text>
            </g>
            </svg>`);
            });
        })
    .then(svg_data => {
        // TODO: colorize the image with strokeColor and fillColor

        imgDict[iconUrl] = svg_data;
    }) // resolve responce to text conversion
}

function drawSVG(ctx, iconUrl, x, y, width, height, strokeColor="black", fillColor="none"){

    // if we don't already have the image, fetch it and cache it
    if(!(iconUrl in imgDict)){
        imgDict[iconUrl] = "loading" // don't resend fetch next frame if the processing still isn't done
        addImageProcess(iconUrl)
    }

    // above happend asyncroniously, so need to check if it completed before trying to draw
    if((iconUrl in imgDict) && (imgDict[iconUrl]!="loading")){
        console.log("drawing at:",x, y, width, height);
        ctx.drawSvg(imgDict[iconUrl], x, y, width, height);
    }
}