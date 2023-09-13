var imgDict = {};

//space for recoloring pngs
var recolorCanvas = document.createElement('canvas');
recolorCanvas.width = 500;
recolorCanvas.height = 500;
var recolor_ctx = recolorCanvas.getContext('2d');

// from https://stackoverflow.com/questions/37128451/random-number-generator-with-x-y-coordinates-as-seed/37221804#37221804
// cash stands for chaos hash :D
function cash(x,y,seed){
    var h = seed + x*374761393 + y*668265263; //all constants are prime
    h = (h^(h >> 13))*1274126177;
    return h^(h >> 16);
}

function drawPNG(ctx, iconUrl, x, y, width, height, recolor="none"){

    // if we don't already have the image, fetch it and cache it
    if(!(iconUrl in imgDict)){
        imgDict[iconUrl] = "loading" // don't resend fetch next frame if the processing still isn't done
        // addImageProcess(iconUrl)
        let url=iconUrl;
        if(url.slice(-3) == "svg"){
            console.log( "svg images not supported, replacing with a png one." );
            url=url.slice(0,-3)+"png";
        }

        var img = new Image();
        img.onload=function(){
            imgDict[iconUrl] = img;
        };
        img.onerror = function() {
            //failsafe onlo a default image
            console.log("failed to make an Image from: " + url +" Replacing with a default one.");
            var img2 = new Image();
            img2.onload=function(){
                imgDict[iconUrl] = img2;
            };
            img2.src = "/static/graphics/absent.png";
        }
        img.src = url;
    }

    // if(recolor!="none"){

    // }

    // above happend asyncroniously, so need to check if it completed before trying to draw
    if((iconUrl in imgDict) && (imgDict[iconUrl]!="loading")){        
        ctx.drawImage(imgDict[iconUrl], x, y, width, height);
    }
}





// async handler for svg fetching/decoding
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
            resolve(`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" height="512" width="512">
            <g style="fill:none; stroke:#000000; stroke-width:12">
                <path d="M3 3 L509 3 L509 509 L3 509 Z"/>
            </g>
            <g style="font: bold 512px sans-serif; fill:none; stroke:#000000; stroke-width:12">
                <text x="410" y="435" text-anchor="middle">?</text>
            </g>
            </svg>`);
            });
        })
    .then(svg_data => {
        imgDict[iconUrl] = svg_data;
    }) // resolve responce to text conversion
}


function drawSVG(ctx, iconUrl, x, y, width, height, color="#000000"){

    // if we don't already have the image, fetch it and cache it
    if(!(iconUrl in imgDict)){
        imgDict[iconUrl] = "loading" // don't resend fetch next frame if the processing still isn't done
        addImageProcess(iconUrl)
    }

    // above happend asyncroniously, so need to check if it completed before trying to draw
    if((iconUrl in imgDict) && (imgDict[iconUrl]!="loading")){
        // console.log("drawing at:",x, y, width, height);
        data = imgDict[iconUrl]

        // TODO: colorize the image
        if(color!="#000000"){
            data=data.replaceAll("#000000", color);
        }
        
        ctx.drawSvg(data, x, y, width, height);
    }
}