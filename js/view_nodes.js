import { app } from "../../scripts/app.js";

// Auto-scale view nodes based on node width
app.registerExtension({
    name: "MachinePainting.ViewNodes",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        const viewNodes = ["HistogramView", "ColorWheelView"];
        
        if (!viewNodes.includes(nodeData.name)) return;
        
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function() {
            onNodeCreated?.apply(this, arguments);
            
            // Set minimum size
            this.size[0] = Math.max(this.size[0], 280);
            this.size[1] = Math.max(this.size[1], 200);
            
            // Find and update width widget
            this.updateWidthWidget();
        };
        
        nodeType.prototype.updateWidthWidget = function() {
            const widthWidget = this.widgets?.find(w => w.name === "width" || w.name === "size");
            if (widthWidget) {
                const nodeWidth = Math.max(256, Math.min(1024, this.size[0] - 20));
                widthWidget.value = nodeWidth;
            }
        };
        
        const onResize = nodeType.prototype.onResize;
        nodeType.prototype.onResize = function(size) {
            // Clamp size
            size[0] = Math.max(280, Math.min(1050, size[0]));
            size[1] = Math.max(200, size[1]);
            
            onResize?.apply(this, arguments);
            
            // Update width widget when node is resized
            this.updateWidthWidget();
        };
        
        // Hide the width/size widget since it's auto-controlled
        const onDrawForeground = nodeType.prototype.onDrawForeground;
        nodeType.prototype.onDrawForeground = function(ctx) {
            onDrawForeground?.apply(this, arguments);
            
            // Hide width widget
            const widthWidget = this.widgets?.find(w => w.name === "width" || w.name === "size");
            if (widthWidget && widthWidget.computeSize) {
                widthWidget.computeSize = () => [0, -4];
            }
        };
    }
});
