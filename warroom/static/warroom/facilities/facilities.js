
class Facility {
    constructor(x,y) {
        this.x = x;
        this.y = y;
        this.iconURL = "/static/graphics/absent.svg";
        this.debug_text = ""
        this.owned = false; // is this owned by the current player?
        this.type = "";
        this.name = "";
        this.hex = null;
    }
  
    draw(ctx, view) {
        // draw facility from scratch
        if(this.x>=view.x_min && this.x<=view.x_max && this.y>=view.y_min && this.y<=view.y_max){
            const r = view.hex_scale;
            const s_x = 1.5 * r * (this.x - view.x_start_map);
            const s_y = sqrtthree*r * (this.y - view.y_start_map + (this.x%2==1 ? 0.5 : 0.0));

            // debug
            if(this.debug_text){
            ctx.fillStyle = "#000000";
            ctx.textAlign = "center";
            ctx.font = "16px sans";
            ctx.fillText(`${this.debug_text}`, s_x, s_y+view.hex_scale*0.25);
            }

            // draw the facility icon
            let w = 1.2*r;
            drawPNG(ctx, this.iconURL, s_x-0.5*w, s_y-0.5*w, w, w);
        }
    }

    drawInHex(ctx, s_x, s_y, r, cur_fac, num_fac) {
        // draw the facility from precomputed hex info, supports multiple facilities per hex
        let f_x, f_y, w;
        let draw_icon = true;
        let icon_color = (this.owned) ? factionColors[100] : factionColors[this.hex.controller];

        if(num_fac==1){
            w = 1.2*r;
            f_x = s_x-0.5*w;
            f_y = s_y-0.5*w;
        }
        else if(num_fac==2){
            let pad = 0.2;
            w = 0.5*r;
            f_x = s_x + (-pad-1 + cur_fac*(1+2*pad))*w;
            f_y = s_y - 0.5*w;
        }
        else{
            let pad = 0.2;
            w = 0.4*r;

            // two at top
            if(cur_fac<2){
                f_x = s_x + (-pad-1 + cur_fac*(1+2*pad))*w;
                f_y = s_y - pad - w;
            }
            // bottom one
            else{
                f_x = s_x - 0.5*w;
                f_y = s_y + pad;

                // if more than 3 facilities on a single hex
                // third symbol should be a plus sign with the number of facilities
                if(num_fac>3){
                    draw_icon = false; // don't draw the icon
                    ctx.fillStyle = icon_color;
                    ctx.textAlign = "center";
                    ctx.font = `bold ${int(w)}px sans`;
                    ctx.fillText(`+${num_fac-2}`, s_x, f_y+pad+0.5*w);
                }
            }
        }

        // draw the icon, now that whe know where to do so
        if(draw_icon){
            // console.log(`drawing facility ${this.name} at hex ${this.x},${this.y}:\t ${f_x},${f_y} & w=${w}, icon: ${this.iconURL}`);
            drawPNG(ctx, this.iconURL, f_x, f_y, w, w, icon_color);
        }

    }
}
