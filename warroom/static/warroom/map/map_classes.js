
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
        this.hexes.forEach((h,i) => {
            h.draw(ctx, view);
        });
        ctx.restore()

        ctx.save()
        this.hexes.forEach((h,i) => {
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

            if(r>50 && cash(this.x,this.y,7574533)%8==0){ // if zoomed in, show terrain icons, but not for every hex (slow)
              let w = 1.2*r;
              drawSVG(ctx, this.iconURL, s_x-0.5*w, s_y-0.5*w, w, w);
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

        }
    }


    draw_rivers(ctx, view) {
      const r = view.hex_scale;
      const s_x = 1.5 * r * (this.x - view.x_start_map);
      const s_y = sqrtthree*r * (this.y - view.y_start_map + (this.x%2==1 ? 0.5 : 0.0));
      
      let headlen = r*0.2;

      // rivers
      if(this.river_dir>=0){ // draw a river
        // console.log("drawing river to ", this.river_dir)
        ctx.beginPath();
        ctx.strokeStyle = "#38AFCD";
        ctx.lineWidth = Math.min(5, 0.1*r);
        ctx.moveTo(s_x, s_y );

        let to_x;
        let to_y;
        if(this.river_dir == 0){  // N
          to_x = s_x;
          to_y = s_y - r*sqrtthree;
        }
        else if(this.river_dir == 1){  // NE
          to_x = s_x + r*1.5;
          to_y = s_y - r*0.5*sqrtthree;
        }
        else if(this.river_dir == 2){  // SE
          to_x = s_x + r*1.5;
          to_y = s_y + r*0.5*sqrtthree;
        }
        else if(this.river_dir == 3){  // S
          to_x = s_x;
          to_y = s_y + r*sqrtthree;
        }
        else if(this.river_dir == 4){  // SW
          to_x = s_x - r*1.5;
          to_y = s_y + r*0.5*sqrtthree;
        }
        else {                         // NW
          to_x = s_x - r*1.5;
          to_y = s_y - r*0.5*sqrtthree;
        }

        ctx.lineTo(to_x, to_y);
        ctx.stroke();

        //starting a new path from the head of the arrow to one of the sides of the point
        ctx.beginPath();
        let angle = Math.atan2(to_y-s_y,to_x-s_x);
        // console.log("arrow angle:", angle, "rad or", angle*180./Math.PI, "deg")
        ctx.moveTo(to_x, to_y);
        ctx.lineTo(to_x-headlen*Math.cos(angle-Math.PI/7),
                   to_y-headlen*Math.sin(angle-Math.PI/7));
    
        //path from the side point of the arrow, to the other side point
        ctx.lineTo(to_x-headlen*Math.cos(angle+Math.PI/7),
                   to_y-headlen*Math.sin(angle+Math.PI/7));
    
        //path from the side point back to the tip of the arrow, and then
        //again to the opposite side point
        ctx.lineTo(to_x, to_y);
        ctx.lineTo(to_x-headlen*Math.cos(angle-Math.PI/7),
                   to_y-headlen*Math.sin(angle-Math.PI/7));
    
        ctx.stroke();
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
        console.log("grid pos of cursor:", this.x_start, this.y_start);
        console.log("map pos of cursor:", this.grid_to_map(this.x_start, this.y_start));

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
        console.log("grid pos of cursor:", this.x_start, this.y_start);
        console.log("map pos of cursor:", this.grid_to_map(this.x_start, this.y_start));

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