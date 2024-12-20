
class Map {
    constructor(width, height, init=true) {
      this.height = height;
      this.width = width;
      this.hexes = [];
      this.units = []; // units we will draw
      if(init){ this.init(); }
    }

    init() {
        for (let x = 0; x < this.width; x++) {
            for (let y = 0; y < this.height; y++) {
                var hex = new Hex(x,y);
                hex.color = `#${(Math.floor(Math.random()*16777215).toString(16))}`;
                this.hexes.push(hex);

                // console.log(`Hex at ${hex.x},${hex.y} color: ${hex.color}`)
              } 
          } 
    }

    draw(ctx, view) {
        ctx.save()
        // this.hexes.forEach((h,i) => {
        Object.entries(this.hexes).forEach(([key, h]) => {
            h.draw(ctx, view);
        });
        ctx.restore()

        ctx.save()
        // this.hexes.forEach((h,i) => {
        Object.entries(this.hexes).forEach(([key, h]) => {
            h.draw_rivers(ctx, view);
        });
        ctx.restore()

        ctx.save()
        this.units.forEach((u,i) => {
          u.draw(ctx, view);
        });
        ctx.restore()
    }
}


const sqrtthree = Math.sqrt(3.0);
const hextheta = 2 * Math.PI / 6;

class Hex {
    constructor(x,y) {
      this.x = x;
      this.y = y;
      this.color = "#FAFAFA"
      this.border_w = 1
      this.border_color = "#000000" //"#A0A0A0"
      this.iconURL = "/static/graphics/absent.svg";
      this.debug_text = ""
      this.river_dir = -1 // no river
      this.terrain = ""
      this.control = [0.0, 0.0];
      this.controller = -1; // neutral
      // this.neighbour_dict = [];
      this.facilities = [];
    }

    draw(ctx, view) {
        if(this.x>=view.x_min && this.x<=view.x_max && this.y>=view.y_min && this.y<=view.y_max){
            const r = view.hex_scale;
            const s_x = 1.5 * r * (this.x - view.x_start_map);
            const s_y = sqrtthree*r * (this.y - view.y_start_map + (this.x%2==1 ? 0.5 : 0.0));

            ctx.beginPath();
            ctx.strokeStyle = this.border_color;
            ctx.lineWidth = this.border_w;
            for (var i = 0; i < 6; i++) {
                ctx.lineTo(s_x + r * Math.cos(hextheta * i), s_y + r * Math.sin(hextheta * i));
            }
            ctx.closePath();
            ctx.fillStyle = this.color;
            ctx.fill();
            if(r>20){   // draw border
              ctx.stroke();
            }
            
            // // draw center point
            // ctx.fillStyle = this.border_color;
            // ctx.fillRect(s_x-2,s_y-2,5,5);

            if(this.facilities.length==0){ // empty hex
              // draw terrain icon
              if(r>50 && cash(this.x,this.y,7574533)%2==0){ // if zoomed in, show terrain icons, but not for every hex (slow)
                let w = 1.2*r;
                // drawSVG(ctx, this.iconURL, s_x-0.5*w, s_y-0.5*w, w, w);
                drawPNG(ctx, this.iconURL, s_x-0.5*w, s_y-0.5*w, w, w);
              }
            }
            else{ // faclities are here
              for (let i = 0; i < this.facilities.length; i++) {
                this.facilities[i].drawInHex(ctx, view, s_x, s_y, r, i, this.facilities.length);
              }
            }

            if(r>30){ // hide coordinates when zoomed out
              ctx.fillStyle = "#000000";
              ctx.textAlign = "center";
              ctx.font = "12px sans";
              ctx.fillText(`${this.x},${this.y}`, s_x, s_y+view.hex_scale*0.75);
            }

            // debug
            if(this.debug_text){
              ctx.fillStyle = "#000000";
              ctx.textAlign = "center";
              ctx.font = "16px sans";
              ctx.fillText(`${this.debug_text}`, s_x, s_y+view.hex_scale*0.25);
            }

            // DEBUG: control as pie charts, but only on land
            if(r>30 && this.terrain!="Sea"){
              let end_angle = -0.5*Math.PI;
              let ctrl_pie_x = s_x-0.3*r;
              let ctrl_pie_y = s_y-0.55*r;
              let ctrl_pie_r = 0.2*r;
              for (var c = 0; c < 2; c++) {
                if(this.control[c]>0){
                  ctx.fillStyle = factionColors[c];
                  ctx.textAlign = "center";
                  ctx.font = "12px sans";
                  let start_angle = end_angle;
                  end_angle += this.control[c]*2*Math.PI;
                  ctx.fillStyle = `${factionColors[c]}`+"80"; // semi-transparent
                  ctx.strokeStyle = "#20202080"; // semi-transparent dark gray
                  ctx.beginPath();
                  if(this.control[c]>=1.0){ // full control -> circle without sectors
                    ctx.arc(ctrl_pie_x, ctrl_pie_y, ctrl_pie_r, start_angle, end_angle);
                  }
                  else{
                    ctx.moveTo(ctrl_pie_x, ctrl_pie_y);
                    ctx.arc(ctrl_pie_x, ctrl_pie_y, ctrl_pie_r, start_angle, end_angle);
                    ctx.lineTo(ctrl_pie_x, ctrl_pie_y);
                  }
                  ctx.closePath();
                  ctx.fill();
                  ctx.stroke();
                }
              }
            }


            // control borders
            // dont' draw boder for grey zones or water hexes
            if(this.controller >=0 && this.terrain!="Sea"){
              const dirs = ["SE", "S", "SW", "NW", "N", "NE"];
              const frontline_w = 8;
              const frontline_r = Math.max(r-this.border_w-frontline_w*0.5, 0.7*r);
              
              for (let dn = 0; dn < dirs.length; dn++) {
                let neigbour_key = this.neighbour_dict[dirs[dn]];
                if(neigbour_key in map.hexes){ // only valid neighbours
                  // draw line if that neighbour is owned by different side and is not Sea
                  if(map.hexes[neigbour_key].controller != this.controller &&
                     map.hexes[neigbour_key].terrain!="Sea"){

                    ctx.strokeStyle = `${factionColors[this.controller]}`+"80";

                    // const gradient = ctx.createLinearGradient(
                    //   s_x + frontline_r * Math.cos(hextheta * (dn+0.5)),
                    //   s_y + frontline_r * Math.sin(hextheta * (dn+0.5)),
                    //   s_x + (frontline_r-frontline_w) * Math.cos(hextheta * (dn+0.5)),
                    //   s_y + (frontline_r-frontline_w) * Math.sin(hextheta * (dn+0.5)),
                    // );
                    // gradient.addColorStop(0, `${factionColors[this.controller]}`+"80");
                    // gradient.addColorStop(1, `${factionColors[this.controller]}`+"00");
                    // ctx.strokeStyle = gradient;


                    ctx.lineWidth = frontline_w;
                    ctx.beginPath();
                    ctx.lineTo(s_x + frontline_r * Math.cos(hextheta * dn),
                              s_y + frontline_r * Math.sin(hextheta * dn));
                    ctx.lineTo(s_x + frontline_r * Math.cos(hextheta * (dn+1)),
                              s_y + frontline_r * Math.sin(hextheta * (dn+1)));
                    ctx.closePath();
                    ctx.stroke();
                  }
                }
              }
            }
            
        }
    }


    draw_rivers(ctx, view) {
     
      // rivers
      if(this.river_dir>=0){ // draw a river
        const r = view.hex_scale;
        // shift rivers to not be at the center of the hex by f*2*r
        const f = 0.1;
        const shift_x = f*r/sqrtthree;
        const shift_y = f*r;
        const h = r*0.5*sqrtthree;
        let s_x = 1.5 * r * (this.x - view.x_start_map) + shift_x;
        let s_y = sqrtthree*r * (this.y - view.y_start_map + (this.x%2==1 ? 0.5 : 0.0)) - shift_y;
               
        // Find which hex we are flowing to
        let next_key;
        if(this.river_dir == 0){  // N
          // next_key = String(this.x)+"_"+String(this.y-1)
          next_key = this.neighbour_dict["N"]
        }
        else if(this.river_dir == 1){  // NE
          // next_key = String(this.x+1)+"_"+String(this.y+(this.x%2==0 ? -1 : 0))
          next_key = this.neighbour_dict["NE"]
        }
        else if(this.river_dir == 2){  // SE
          // next_key = String(this.x+1)+"_"+String(this.y+(this.x%2==0 ? 0 : 1))
          next_key = this.neighbour_dict["SE"]
        }
        else if(this.river_dir == 3){  // S
          // next_key = String(this.x)+"_"+String(this.y+1)
          next_key = this.neighbour_dict["S"]
        }
        else if(this.river_dir == 4){  // SW
          // next_key = String(this.x-1)+"_"+String(this.y+(this.x%2==0 ? 0 : 1))
          next_key = this.neighbour_dict["SW"]
        }
        else {                         // NW
          // next_key = String(this.x-1)+"_"+String(this.y+(this.x%2==0 ? -1 : 0))
          next_key = this.neighbour_dict["NW"]
        }

        let to_x;
        let to_y;

        // Flowing into a body of water should stop at border
        if(map.hexes[next_key].terrain == "Sea" || map.hexes[next_key].terrain == "Lake"){
          // to_x = s_x + (to_x - s_x)*0.5
          // to_y = s_y + (to_y - s_y)*0.5

          // assuming shift_y is upwards
          if(this.river_dir == 0){  // N
            to_x = s_x;
            to_y = s_y - h + shift_y;
          }
          else if(this.river_dir == 1){  // NE
            let s = (0.5*sqrtthree)*(r-shift_x-shift_y/sqrtthree)
            to_x = s_x + 0.5*sqrtthree*s;
            to_y = s_y - 0.5*s;
          }
          else if(this.river_dir == 2){  // SE
            let s = 0.5*(shift_y + sqrtthree*(r-shift_x))
            to_x = s_x + 0.5*sqrtthree*s;
            to_y = s_y + 0.5*s;
          }
          else if(this.river_dir == 3){  // S
            to_x = s_x;
            to_y = s_y + h + shift_y;
          }
          else if(this.river_dir == 4){  // SW
            let s = 2*h - (0.5*sqrtthree)*(r-shift_x-shift_y/sqrtthree)
            to_x = s_x - 0.5*sqrtthree*s;
            to_y = s_y + 0.5*s;
          }
          else{                          // NW
            let s = 2*h - 0.5*(shift_y + sqrtthree*(r-shift_x))
            to_x = s_x - 0.5*sqrtthree*s;
            to_y = s_y - 0.5*s;
          }
          
        }
        // Flowing to land should stop at 
        else{
          if(this.river_dir == 0){  // N
            to_x = s_x;
            to_y = s_y - r*sqrtthree;
          }
          else if(this.river_dir == 1){  // NE
            to_x = s_x + r*1.5;
            to_y = s_y - h;
          }
          else if(this.river_dir == 2){  // SE
            to_x = s_x + r*1.5;
            to_y = s_y + h;
          }
          else if(this.river_dir == 3){  // S
            to_x = s_x;
            to_y = s_y + r*sqrtthree;
          }
          else if(this.river_dir == 4){  // SW
            to_x = s_x - r*1.5;
            to_y = s_y + h;
          }
          else{                          // NW
            to_x = s_x - r*1.5;
            to_y = s_y - h;
          }
        }

        // if flowing from a lake
        if(this.terrain == "Lake"){
          // return;
          // flowing between bodies of water should not be drawn
          if(map.hexes[next_key].terrain == "Sea" || map.hexes[next_key].terrain == "Lake"){
            return;
          }
          else{
            // flowing from a lake should start at border
            if(this.river_dir == 0){  // N
              // s_x = s_x;
              s_y = s_y - h + shift_y;
            }
            else if(this.river_dir == 1){  // NE
              let s = (0.5*sqrtthree)*(r-shift_x-shift_y/sqrtthree)
              s_x = s_x + 0.5*sqrtthree*s;
              s_y = s_y - 0.5*s;
            }
            else if(this.river_dir == 2){  // SE
              let s = 0.5*(shift_y + sqrtthree*(r-shift_x))
              s_x = s_x + 0.5*sqrtthree*s;
              s_y = s_y + 0.5*s;
            }
            else if(this.river_dir == 3){  // S
              // s_x = s_x;
              s_y = s_y + h + shift_y;
            }
            else if(this.river_dir == 4){  // SW
              let s = 2*h - (0.5*sqrtthree)*(r-shift_x-shift_y/sqrtthree)
              s_x = s_x - 0.5*sqrtthree*s;
              s_y = s_y + 0.5*s;
            }
            else{                          // NW
              let s = 2*h - 0.5*(shift_y + sqrtthree*(r-shift_x))
              s_x = s_x - 0.5*sqrtthree*s;
              s_y = s_y - 0.5*s;
            }
          }
        }

        // Draw the river as a line
        ctx.beginPath();
        ctx.strokeStyle = "#38AFCD";
        ctx.lineWidth = Math.min(5, 0.1*r);
        ctx.moveTo(s_x, s_y );
        ctx.lineTo(to_x, to_y);
        ctx.stroke();

        // //starting a new path from the head of the arrow to one of the sides of the point
        // let headlen = r*0.2;
        // ctx.beginPath();
        // let angle = Math.atan2(to_y-s_y,to_x-s_x);
        // // console.log("arrow angle:", angle, "rad or", angle*180./Math.PI, "deg")
        // ctx.moveTo(to_x, to_y);
        // ctx.lineTo(to_x-headlen*Math.cos(angle-Math.PI/7),
        //            to_y-headlen*Math.sin(angle-Math.PI/7));
    
        // //path from the side point of the arrow, to the other side point
        // ctx.lineTo(to_x-headlen*Math.cos(angle+Math.PI/7),
        //            to_y-headlen*Math.sin(angle+Math.PI/7));
    
        // //path from the side point back to the tip of the arrow, and then
        // //again to the opposite side point
        // ctx.lineTo(to_x, to_y);
        // ctx.lineTo(to_x-headlen*Math.cos(angle-Math.PI/7),
        //            to_y-headlen*Math.sin(angle-Math.PI/7));
    
        // ctx.stroke();
      }

    }
}


class View {
    // grid coordinates are square, 1 hex length on the side
    // map coordinates are discrete indeces of individual hexes in a map. 
    
    constructor(canvas) {
        this.x_start = 0;     // grid coords of top left corner (px/scale)
        this.y_start = 0;     // grid coords of top left corner (px/scale)
        this.x_start_map = 0; // map coords (continuous) of top left corner
        this.y_start_map = 0; // map coords (continuous) of top left corner,
                              //     need shift down by 0.5 for odd x_start_map
        this.m_width = canvas.width;   // px
        this.m_height = canvas.height; // px
        this.hex_scale = 30; //px per horizontal side
        this.x_max = 0; //map coords limit to render in hexes
        this.y_max = 0; //map coords limit to render in hexes
        this.x_min = 0; //map coords limit to render in hexes
        this.y_min = 0; //map coords limit to render in hexes
        this.calc_limits();
      }

      resize(canvas){
        this.m_width = canvas.width; // px
        this.m_height = canvas.height;
        this.calc_limits();
      }

      zoom_in(cX, cY){ //cX, cY in onscreen pixels
        //move start to map pos of cursor
        this.x_start += cX/this.hex_scale;
        this.y_start += cY/this.hex_scale;
        // console.log("grid pos of cursor:", this.x_start, this.y_start);
        // console.log("map pos of cursor:", this.grid_to_map(this.x_start, this.y_start));

        this.hex_scale*=1.5; //change scale
        if(this.hex_scale>100){this.hex_scale=100};

        //move start to new top left corner
        this.x_start -= cX/this.hex_scale;
        this.y_start -= cY/this.hex_scale;

        this.calc_limits();
      }

      zoom_out(cX, cY){ //cX, cY in onscreen pixels
        //move start to map pos of cursor
        this.x_start += cX/this.hex_scale;
        this.y_start += cY/this.hex_scale;
        // console.log("grid pos of cursor:", this.x_start, this.y_start);
        // console.log("map pos of cursor:", this.grid_to_map(this.x_start, this.y_start));

        this.hex_scale/=1.5; //change scale
        if(this.hex_scale<12){this.hex_scale=12};

        //move start to new top left corner
        this.x_start -= cX/this.hex_scale;
        this.y_start -= cY/this.hex_scale;

        this.calc_limits();
      }

      move(dxpx, dypx){
        this.x_start+=dxpx/this.hex_scale;
        this.y_start+=dypx/this.hex_scale;
        this.calc_limits();
      }

      calc_limits(){
        this.x_start_map = this.x_start / 1.5;          // in map coords
        this.y_start_map = this.y_start / sqrtthree;    // in map coords

        var map_width = this.m_width / (this.hex_scale * 1.5);          // in hexes
        var map_height = this.m_height / (this.hex_scale * sqrtthree);  // in hexes

        this.x_max = Math.ceil(this.x_start_map + map_width + 0.5);  // in map coords
        this.x_min = Math.floor(this.x_start_map - 0.5);             // in map coords
        this.y_max = Math.ceil(this.y_start_map + map_height + 0.5); // in map coords
        this.y_min = Math.floor(this.y_start_map - 0.5);             // in map coords

        // this.debug();
      }

      grid_to_map(x_grid, y_grid){ //convert grid coordinates to descrete map ones
        var x_map = Math.floor(x_grid/1.5);
        var y_map = Math.floor(y_grid/sqrtthree) + ((x_map%2==0)?0:-1);
        return([x_map, y_map])
      }

      debug(){
        console.log(`min: ${this.x_min}, ${this.y_min}\tmax: ${this.x_max}, ${this.y_max}`);
      }

}