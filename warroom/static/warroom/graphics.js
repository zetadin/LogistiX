var imgDict = {};

// from https://stackoverflow.com/questions/37128451/random-number-generator-with-x-y-coordinates-as-seed/37221804#37221804
// cash stands for chaos hash :D
function cash(x,y,seed){
    var h = seed + x*374761393 + y*668265263; //all constants are prime
    h = (h^(h >> 13))*1274126177;
    return h^(h >> 16);
}


function scaleIMG(input_key, width, height, resolve){
    let rs_canvas = document.createElement("canvas");
    let rs_ctx = rs_canvas.getContext("2d");
    // rs_ctx.imageSmoothingEnabled = false;
    let input_img = imgDict[input_key];

    rs_ctx.drawImage(input_img, 0, 0, width, height);
    let data_url = rs_canvas.toDataURL("image/png");
    let out_img = new Image();
    out_img.onload=function(){
            imgDict[input_key+"__"+width+"_"+height] = out_img;
            resolve();
        };
    out_img.src = data_url;
}


function colorizeIMG(input_key, new_color, resolve){
    if(new_color=="none"){
        imgDict[input_key+"_"+new_color] = imgDict[input_key];
        resolve();
        return;
    }

    let rc_canvas = document.createElement("canvas");
    let rc_ctx = rc_canvas.getContext("2d");
    let input_img = imgDict[input_key];

    rc_ctx.drawImage(input_img, 0, 0);
    
    // recolor logic:
    imgData = rc_ctx.getImageData(0, 0, rc_canvas.width, rc_canvas.height);
    rawData = imgData.data;
    let nc = new RGBColor(new_color); //new color
    nc.r = Math.floor((nc.r+2*255)/3)
    nc.g = Math.floor((nc.g+2*255)/3)
    nc.b = Math.floor((nc.b+2*255)/3)
    for (let i = 0; i < rawData.length; i += 4) {
        let r = rawData[i];
        let g = rawData[i+1];
        let b = rawData[i+2];

        let luma = 0.2126*r + 0.7152*g + 0.0722*b; // luminescence
        // black (luma=0) should stay black
        // white (luma=255) should change to pale version of new_color
        let luma_frac = luma/255.0;
        rawData[i] = luma_frac*nc.r + (1-luma_frac)*r;
        rawData[i+1] = luma_frac*nc.g + (1-luma_frac)*g;
        rawData[i+2] = luma_frac*nc.b + (1-luma_frac)*b;
    }
    imgData.data = rawData;
    rc_ctx.putImageData(imgData, 0, 0);


    let data_url = rc_canvas.toDataURL("image/png");
    let out_img = new Image();
    out_img.onload=function(){
            imgDict[input_key+"_"+new_color] = out_img;
            resolve();
        };
    out_img.src = data_url;
}


function drawPNG(ctx, iconUrl, x, y, width, height, recolor="none"){
    w = Math.floor(width);
    h = Math.floor(height);
    
    // use iconUrl as key for the original image
    let img_scaled_subkey = iconUrl+"__"+w+"_"+h;
    let colorless_key = img_scaled_subkey+"_none"; // key for scaled image with no recolor
    let img_key = img_scaled_subkey+"_"+recolor;   // key for scaled image with recolor

    // if image is ready
    if(img_key in imgDict && (imgDict[img_key]!="loading")){
        ctx.drawImage(imgDict[img_key], x, y);
    }
    // don't draw if it is still loading

    // launch scaling and coloring if not ready but base image is ready
    else if(!(img_key in imgDict) && (iconUrl in imgDict) && (imgDict[iconUrl]!="loading")){
        // if scaled image is ready, just recolor
        if(recolor!="none" && (colorless_key in imgDict) && (imgDict[colorless_key]!="loading")){
            imgDict[img_key] = "loading";
            new Promise((resolve) => {
                colorizeIMG(img_scaled_subkey, recolor, resolve);
            });
        }
        // if no scaled image, scale and recolor
        else if(!(colorless_key in imgDict)){
            imgDict[colorless_key] = "loading";
            imgDict[img_key] = "loading";
            new Promise((resolve) => {
                scaleIMG(iconUrl, w, h, resolve);
            }).then(() => {
                return new Promise((resolve2) => {
                    colorizeIMG(img_scaled_subkey, recolor, resolve2);
                });
            });
        }
        // if scaled image is not ready, wait and don't do anything
        
    }

    
    // if we don't yet have the base image, fetch it and cache it
    else if(!(iconUrl in imgDict)){
        imgDict[iconUrl] = "loading" // don't resend fetch next frame if the processing still isn't done
        console.log("fetching "+iconUrl);

        // addImageProcess(iconUrl)
        let url=iconUrl;
        // if(url.slice(-3) == "svg"){
        //     console.log( "svg images not supported, replacing with a png one." );
        //     url=url.slice(0,-3)+"png";
        // }

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
