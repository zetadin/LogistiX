
var imgDict = {};


// async handler for image loading
// resolves only after the image is loaded
// from https://stackoverflow.com/questions/46399223/async-await-in-image-loading
async function addImageProcess(svg_data){
    // return new Promise((resolve, reject) => {
    //   var img = new Image() // can't be block scoped
    // //   img.onload = () => resolve(img)
    //   var blob = new Blob([svg_data], {type: 'image/svg+xml'});
    //   var url = URL.createObjectURL(blob);
    //   img.onerror = reject(blob)
    //   reject(blob)
    //   img.src = url
    // })

    var img = new Image() // can't be block scoped
    var blob = new Blob([svg_data], {type: 'image/svg+xml'});
    var url = URL.createObjectURL(blob);
    img.src = url
    await img.decode();
    return(img);
  }

function drawSVG(ctx, iconUrl, x, y, width, height, strokeColor="black", fillColor="none"){

    // if we don't already have the image, fetch it and cache it
    if(!(iconUrl in imgDict)){
        // var svg_data;
        
        // fetch svg, convert responce to text, and save into svg_data variable
        fetch(iconUrl)
            .then( response => response.text() )       // after resolve of fetch ask for text of responce
            .catch ( error =>{
                console.log("Could not fetch"+iconUrl+": "+error);
                // so put a ? in a square instead
                return(`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" height="100" width="100">

                <g style="fill: #f0f0f0; stroke:#000000; stroke-width:3">
               <path d="M1 1 L99 1 L99 99 L1 99 Z"/>
                </g>
               
                <g style="font: bold 100px sans-serif; fill:none; stroke:#000000; stroke-width:1">
               <text x="50%" y="58%" dominant-baseline="middle" text-anchor="middle">?</text>
                </g>
               
               </svg>`);
                })
            .then(svg_data => {
                // TODO: colorize the image with strokeColor and fillColor

                imgDict[iconUrl] = svg_data;

                // load svg as an Image
                // var img = addImageProcess(svg_data);
                // imgDict[iconUrl] = img;
                // return(img);
            }) // resolve responce to text conversion
            // .finally(img=>{
            //     console.log("image is:", img)
            // })
            
            // .then( img => { 
            //                 imgDict[iconUrl]=img; 
            //             }, //  add the Image to the dict
            //         blob => {
            //                 console.log("could not convert svg to image ", iconUrl, ": ", blob); return;
            //             }, // reject
            // ); // final resolve
    }

    // here image already exists, just need to draw it
    // ctx.drawImage(imgDict[iconUrl], x, y, width, height);
    // ctx.drawImage(imgDict[iconUrl], x, y);
    ctx.drawSvg(imgDict[iconUrl], x, y);
}