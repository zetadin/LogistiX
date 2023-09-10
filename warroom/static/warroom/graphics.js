
var imgDict = {};


// async handler for image loading
// resolves only after the image is loaded
// from https://stackoverflow.com/questions/46399223/async-await-in-image-loading
function addImageProcess(src){
    return new Promise((resolve, reject) => {
      let img = new Image()
      img.onload = () => resolve(img)
      img.onerror = reject
      img.src = src
    })
  }

function drawSVG(ctx, iconUrl, x, y, width, height, strokeColor="black", fillColor="none"){

    // if we don't already have the image, fetch it and cache it
    if(!(iconUrl in imgDict)){
        var svg_data;
        
        // fetch svg, convert responce to text, and save into svg_data variable
        fetch(iconUrl)
            .then(  response => response.text(),        // resolve fetch
                    reject =>{
                        console.log("Could not fetch"+iconUrl+": "+error);
                        // so put a ? in a square instead
                        svg_data=`<svg viewBox="0 0 100 100" role="img">
                                    <g fill="none" stroke="black">
                                        <style>.tempsvg{font: bold 100px sans-serif;}</style>
                                        <path stroke d="M1 1 L99 1 L99 99 L1 99 Z" />
                                        <text x="50%" y="58%" dominant-baseline="middle" text-anchor="middle" class=tempsvg>?</text>
                                    </g>
                                    </svg>`;
                        },                              // reject fetch
            ).then(d => {svg_data = d;});               // resolve responce to text conversion
        
        // TODO: colorize the image with strokeColor and fillColor

        // load svg as an image and add it to the dict
        addImageProcess(svg_data).then(
                                    img => { imgDict[iconUrl]=img; }, // resolve
                                    reject => { console.log("could not convert svg to image ", iconUrl, ": ", reject); return; }, // reject
                                    );
    }

    // here image already exists, just need to draw it
    ctx.drawImage(imgDict[iconUrl], x, y, width, height);
}