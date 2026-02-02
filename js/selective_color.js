import { app } from "../../scripts/app.js";

// Selective Color Pro - Reset button
app.registerExtension({
    name: "MachinePainting.SelectiveColorPro",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "SelectiveColorPro") return;
        
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function() {
            onNodeCreated?.apply(this, arguments);
            
            // Set initial node size
            this.size[0] = Math.max(this.size[0], 280);
            this.size[1] = Math.max(this.size[1], 280);
        };
        
        const onDrawForeground = nodeType.prototype.onDrawForeground;
        nodeType.prototype.onDrawForeground = function(ctx) {
            onDrawForeground?.apply(this, arguments);
            
            if (this.flags.collapsed) return;
            
            const nodeWidth = this.size[0];
            const nodeHeight = this.size[1];
            
            // Calculate position after widgets
            let widgetsEnd = 30;
            if (this.widgets) {
                for (const w of this.widgets) {
                    if (w.type === "converted-widget") continue;
                    widgetsEnd += 24;
                }
            }
            
            // Reset button
            const btnW = 80;
            const btnH = 20;
            const btnX = (nodeWidth - btnW) / 2;
            const btnY = widgetsEnd + 5;
            
            this.resetBtn = { x: btnX, y: btnY, w: btnW, h: btnH };
            
            ctx.fillStyle = "#3a3a3a";
            ctx.beginPath();
            ctx.roundRect(btnX, btnY, btnW, btnH, 3);
            ctx.fill();
            ctx.strokeStyle = "#4a4a4a";
            ctx.lineWidth = 1;
            ctx.stroke();
            
            ctx.fillStyle = "#aaa";
            ctx.font = "11px Arial";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText("Reset All", btnX + btnW / 2, btnY + btnH / 2);
        };
        
        const onMouseDown = nodeType.prototype.onMouseDown;
        nodeType.prototype.onMouseDown = function(e, pos, canvas) {
            if (this.resetBtn) {
                const btn = this.resetBtn;
                const mx = pos[0], my = pos[1];
                
                if (mx >= btn.x && mx <= btn.x + btn.w && my >= btn.y && my <= btn.y + btn.h) {
                    // Reset all sliders to 0
                    if (this.widgets) {
                        for (const w of this.widgets) {
                            if (["cyan", "magenta", "yellow", "black"].includes(w.name)) {
                                w.value = 0;
                            }
                        }
                    }
                    this.setDirtyCanvas(true, true);
                    return true;
                }
            }
            
            return onMouseDown?.apply(this, arguments);
        };
    }
});
