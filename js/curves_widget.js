import { app } from "../../scripts/app.js";

// Curves Adjust Pro - Interactive curve editor widget
app.registerExtension({
    name: "MachinePainting.CurvesAdjustPro",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "CurvesAdjustPro") return;
        
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function() {
            onNodeCreated?.apply(this, arguments);
            
            // Initialize curve data with 2 points per channel (diagonal line)
            this.curveData = {
                channel: "rgb",
                points: {
                    rgb: [[0, 0], [1, 1]],
                    red: [[0, 0], [1, 1]],
                    green: [[0, 0], [1, 1]],
                    blue: [[0, 0], [1, 1]]
                }
            };
            this.draggingPoint = null;
            
            // Set initial node size
            this.size[0] = Math.max(this.size[0], 300);
            this.size[1] = Math.max(this.size[1], 500);
            
            // Find curve_data widget and hide it
            const curveDataWidget = this.widgets?.find(w => w.name === "curve_data");
            if (curveDataWidget) {
                curveDataWidget.computeSize = () => [0, -4];
                curveDataWidget.type = "converted-widget";
                
                // Load initial data from widget if valid
                try {
                    const data = JSON.parse(curveDataWidget.value);
                    if (data.rgb && data.rgb.length >= 2) {
                        this.curveData.points = data;
                    }
                } catch(e) {}
            }
            
            // Sync initial state to widget
            this.syncToWidget();
            
            // Hook preset widget
            const presetWidget = this.widgets?.find(w => w.name === "preset");
            if (presetWidget) {
                const origCallback = presetWidget.callback;
                presetWidget.callback = (value) => {
                    if (origCallback) origCallback.call(presetWidget, value);
                    this.applyPreset(value);
                    this.setDirtyCanvas(true, true);
                };
            }
        };
        
        // Preset definitions - all have endpoint anchors
        nodeType.prototype.PRESETS = {
            "none": { rgb: [[0,0],[1,1]], red: [[0,0],[1,1]], green: [[0,0],[1,1]], blue: [[0,0],[1,1]] },
            "auto_enhance": { rgb: [[0,0],[0.25,0.22],[0.5,0.5],[0.75,0.78],[1,1]], red: [[0,0],[1,1]], green: [[0,0],[1,1]], blue: [[0,0],[1,1]] },
            "high_contrast": { rgb: [[0,0],[0.25,0.15],[0.5,0.5],[0.75,0.85],[1,1]], red: [[0,0],[1,1]], green: [[0,0],[1,1]], blue: [[0,0],[1,1]] },
            "low_contrast": { rgb: [[0,0.1],[0.5,0.5],[1,0.9]], red: [[0,0],[1,1]], green: [[0,0],[1,1]], blue: [[0,0],[1,1]] },
            "warm_tones": { rgb: [[0,0],[1,1]], red: [[0,0],[0.5,0.55],[1,1]], green: [[0,0],[1,1]], blue: [[0,0],[0.5,0.45],[1,1]] },
            "cool_tones": { rgb: [[0,0],[1,1]], red: [[0,0],[0.5,0.45],[1,1]], green: [[0,0],[1,1]], blue: [[0,0],[0.5,0.55],[1,1]] },
            "vintage_fade": { rgb: [[0,0.05],[1,0.95]], red: [[0,0.02],[0.5,0.52],[1,1]], green: [[0,0],[0.5,0.48],[1,0.95]], blue: [[0,0.05],[0.5,0.45],[1,0.9]] },
            "cinematic": { rgb: [[0,0.03],[0.5,0.5],[1,0.97]], red: [[0,0],[0.5,0.48],[1,1]], green: [[0,0],[0.5,0.5],[1,0.98]], blue: [[0,0.05],[0.5,0.52],[1,1]] },
            "matte_look": { rgb: [[0,0.08],[0.25,0.28],[0.75,0.75],[1,0.92]], red: [[0,0],[1,1]], green: [[0,0],[1,1]], blue: [[0,0],[1,1]] },
            "cross_process": { rgb: [[0,0],[1,1]], red: [[0,0.05],[0.5,0.45],[1,1]], green: [[0,0],[0.5,0.55],[1,0.95]], blue: [[0,0.1],[0.5,0.4],[1,0.9]] },
            "sepia_tone": { rgb: [[0,0],[0.5,0.5],[1,0.95]], red: [[0,0],[0.5,0.55],[1,1]], green: [[0,0],[0.5,0.48],[1,0.9]], blue: [[0,0],[0.5,0.35],[1,0.8]] },
            "bleach_bypass": { rgb: [[0,0],[0.2,0.12],[0.5,0.5],[0.8,0.88],[1,1]], red: [[0,0],[1,1]], green: [[0,0],[1,1]], blue: [[0,0],[0.5,0.45],[1,1]] },
            "golden_hour": { rgb: [[0,0],[0.5,0.52],[1,1]], red: [[0,0],[0.5,0.55],[1,1]], green: [[0,0],[0.5,0.52],[1,0.98]], blue: [[0,0],[0.5,0.4],[1,0.85]] },
            "moonlight": { rgb: [[0,0],[0.5,0.48],[1,0.95]], red: [[0,0],[0.5,0.45],[1,0.9]], green: [[0,0],[0.5,0.5],[1,0.95]], blue: [[0,0.05],[0.5,0.55],[1,1]] },
            "vibrant_pop": { rgb: [[0,0],[0.2,0.15],[0.5,0.5],[0.8,0.85],[1,1]], red: [[0,0],[0.5,0.52],[1,1]], green: [[0,0],[0.5,0.52],[1,1]], blue: [[0,0],[0.5,0.52],[1,1]] },
            "noir": { rgb: [[0,0],[0.15,0.05],[0.5,0.5],[0.85,0.95],[1,1]], red: [[0,0],[0.5,0.48],[1,1]], green: [[0,0],[0.5,0.48],[1,1]], blue: [[0,0],[0.5,0.48],[1,1]] },
            "sunset_glow": { rgb: [[0,0],[1,1]], red: [[0,0],[0.5,0.58],[1,1]], green: [[0,0],[0.5,0.48],[1,0.95]], blue: [[0,0],[0.5,0.38],[1,0.8]] },
            "forest_green": { rgb: [[0,0.02],[0.5,0.5],[1,0.98]], red: [[0,0],[0.5,0.45],[1,0.95]], green: [[0,0],[0.5,0.55],[1,1]], blue: [[0,0],[0.5,0.45],[1,0.9]] }
        };
        
        nodeType.prototype.applyPreset = function(presetName) {
            const preset = this.PRESETS[presetName];
            if (preset) {
                this.curveData.points = {
                    rgb: preset.rgb.map(p => [...p]),
                    red: preset.red.map(p => [...p]),
                    green: preset.green.map(p => [...p]),
                    blue: preset.blue.map(p => [...p])
                };
                this.syncToWidget();
            }
        };
        
        nodeType.prototype.syncToWidget = function() {
            const curveDataWidget = this.widgets?.find(w => w.name === "curve_data");
            if (curveDataWidget) {
                curveDataWidget.value = JSON.stringify(this.curveData.points);
            }
        };
        
        const onSerialize = nodeType.prototype.onSerialize;
        nodeType.prototype.onSerialize = function(o) {
            onSerialize?.apply(this, arguments);
            if (this.curveData) o.curveData = JSON.stringify(this.curveData);
        };
        
        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function(o) {
            onConfigure?.apply(this, arguments);
            if (o.curveData) {
                try {
                    this.curveData = JSON.parse(o.curveData);
                    this.syncToWidget();
                } catch(e) {}
            }
        };
        
        const onResize = nodeType.prototype.onResize;
        nodeType.prototype.onResize = function(size) {
            size[0] = Math.max(280, Math.min(1024, size[0]));
            size[1] = Math.max(450, size[1]);
            onResize?.apply(this, arguments);
        };
        
        // Draw curve editor AFTER widgets using onDrawBackground
        const onDrawBackground = nodeType.prototype.onDrawBackground;
        nodeType.prototype.onDrawBackground = function(ctx) {
            onDrawBackground?.apply(this, arguments);
            
            if (!this.curveData || !this.flags.collapsed) return;
        };
        
        const onDrawForeground = nodeType.prototype.onDrawForeground;
        nodeType.prototype.onDrawForeground = function(ctx) {
            onDrawForeground?.apply(this, arguments);
            
            if (!this.curveData) return;
            if (this.flags.collapsed) return;
            
            const nodeWidth = this.size[0];
            const nodeHeight = this.size[1];
            const margin = 15;
            
            // Calculate top offset - position after all visible widgets
            let topOffset = 30; // Start after title
            if (this.widgets) {
                for (const w of this.widgets) {
                    if (w.type === "converted-widget") continue;
                    if (w.computeSize) {
                        const ws = w.computeSize(nodeWidth);
                        if (ws[1] > 0) topOffset += ws[1] + 4;
                    } else {
                        topOffset += 22;
                    }
                }
            }
            topOffset += 25; // Extra padding after widgets (more space below invert_mask)
            
            // Calculate curve size
            const availableWidth = nodeWidth - margin * 2;
            const availableHeight = nodeHeight - topOffset - 95;
            const size = Math.max(120, Math.min(availableWidth, availableHeight, 500));
            
            const x = (nodeWidth - size) / 2;
            const y = topOffset;
            
            this.curveBounds = { x, y, size };
            
            // Background
            ctx.fillStyle = "#1a1a1a";
            ctx.fillRect(x, y, size, size);
            ctx.strokeStyle = "#444";
            ctx.lineWidth = 1;
            ctx.strokeRect(x, y, size, size);
            
            // Grid
            ctx.strokeStyle = "#2a2a2a";
            for (let i = 1; i < 4; i++) {
                const pos = (size / 4) * i;
                ctx.beginPath();
                ctx.moveTo(x + pos, y);
                ctx.lineTo(x + pos, y + size);
                ctx.stroke();
                ctx.beginPath();
                ctx.moveTo(x, y + pos);
                ctx.lineTo(x + size, y + pos);
                ctx.stroke();
            }
            
            // Diagonal reference
            ctx.strokeStyle = "#383838";
            ctx.setLineDash([4, 4]);
            ctx.beginPath();
            ctx.moveTo(x, y + size);
            ctx.lineTo(x + size, y);
            ctx.stroke();
            ctx.setLineDash([]);
            
            // Get channel data
            const channel = this.curveData.channel;
            const points = this.curveData.points[channel] || [[0, 0], [1, 1]];
            const colors = { rgb: "#fff", red: "#f55", green: "#5f5", blue: "#58f" };
            
            // Helper function to draw a curve
            const drawCurve = (pts, color, lineWidth, drawPoints = false) => {
                if (!pts || pts.length < 2) return;
                const sorted = [...pts].sort((a, b) => a[0] - b[0]);
                const curvePoints = this.interpolateCurve(sorted, 80);
                
                ctx.strokeStyle = color;
                ctx.lineWidth = lineWidth;
                ctx.beginPath();
                ctx.moveTo(x + curvePoints[0][0] * size, y + size - curvePoints[0][1] * size);
                for (let i = 1; i < curvePoints.length; i++) {
                    ctx.lineTo(x + curvePoints[i][0] * size, y + size - curvePoints[i][1] * size);
                }
                ctx.stroke();
                
                // Draw control points if requested
                if (drawPoints) {
                    for (const pt of sorted) {
                        const px = x + pt[0] * size;
                        const py = y + size - pt[1] * size;
                        ctx.fillStyle = color;
                        ctx.beginPath();
                        ctx.arc(px, py, 5, 0, Math.PI * 2);
                        ctx.fill();
                        ctx.fillStyle = "#000";
                        ctx.beginPath();
                        ctx.arc(px, py, 2, 0, Math.PI * 2);
                        ctx.fill();
                    }
                }
            };
            
            // In RGB mode, draw R/G/B curves as thin background lines
            if (channel === "rgb") {
                // Draw individual channel curves as thin 1px lines (background)
                drawCurve(this.curveData.points.red, "#f55", 1, false);
                drawCurve(this.curveData.points.green, "#5f5", 1, false);
                drawCurve(this.curveData.points.blue, "#58f", 1, false);
                // Draw RGB curve (white) as main thick line with points
                drawCurve(points, "#fff", 2, true);
            } else {
                // Draw the selected channel curve with full thickness and points
                drawCurve(points, colors[channel], 2, true);
            }
            
            // Info row
            const infoY = y + size + 10;
            ctx.font = "10px Arial";
            ctx.textAlign = "left";
            ctx.fillStyle = "#888";
            ctx.fillText(`RGB:${this.curveData.points.rgb.length}`, x, infoY);
            ctx.fillStyle = "#f66";
            ctx.fillText(`R:${this.curveData.points.red.length}`, x + 48, infoY);
            ctx.fillStyle = "#6f6";
            ctx.fillText(`G:${this.curveData.points.green.length}`, x + 82, infoY);
            ctx.fillStyle = "#68f";
            ctx.fillText(`B:${this.curveData.points.blue.length}`, x + 116, infoY);
            
            ctx.fillStyle = "#555";
            ctx.textAlign = "right";
            ctx.fillText("Click:add | Drag:move | Shift:remove", x + size, infoY);
            
            // Channel buttons
            const btnY = infoY + 14;
            const btnH = 22;
            const btnGap = 3;
            const btnW = (size - btnGap * 3) / 4;
            const channels = ["rgb", "red", "green", "blue"];
            const btnColors = { rgb: "#666", red: "#a44", green: "#4a4", blue: "#46a" };
            
            this.channelButtons = [];
            for (let i = 0; i < 4; i++) {
                const btnX = x + i * (btnW + btnGap);
                const isActive = channel === channels[i];
                const hasPoints = (this.curveData.points[channels[i]]?.length || 0) > 2;
                this.channelButtons.push({ x: btnX, y: btnY, w: btnW, h: btnH, channel: channels[i] });
                
                ctx.fillStyle = isActive ? btnColors[channels[i]] : "#3a3a3a";
                ctx.beginPath();
                ctx.roundRect(btnX, btnY, btnW, btnH, 3);
                ctx.fill();
                ctx.strokeStyle = "#4a4a4a";
                ctx.lineWidth = 1;
                ctx.stroke();
                
                if (hasPoints && !isActive) {
                    ctx.fillStyle = "#aaa";
                    ctx.beginPath();
                    ctx.arc(btnX + btnW - 7, btnY + 7, 3, 0, Math.PI * 2);
                    ctx.fill();
                }
                
                ctx.fillStyle = isActive ? "#fff" : "#999";
                ctx.font = "bold 10px Arial";
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText(channels[i].toUpperCase(), btnX + btnW / 2, btnY + btnH / 2);
            }
            
            // Action buttons
            const actionY = btnY + btnH + 6;
            const actionBtnW = (size - btnGap * 2) / 3;
            const actionBtnH = 20;
            
            this.autoAdjustBtn = { x: x, y: actionY, w: actionBtnW, h: actionBtnH };
            this.clearChannelBtn = { x: x + actionBtnW + btnGap, y: actionY, w: actionBtnW, h: actionBtnH };
            this.clearAllBtn = { x: x + (actionBtnW + btnGap) * 2, y: actionY, w: actionBtnW, h: actionBtnH };
            
            const drawBtn = (btn, label) => {
                ctx.fillStyle = "#3a3a3a";
                ctx.beginPath();
                ctx.roundRect(btn.x, btn.y, btn.w, btn.h, 3);
                ctx.fill();
                ctx.strokeStyle = "#4a4a4a";
                ctx.stroke();
                ctx.fillStyle = "#aaa";
                ctx.font = "10px Arial";
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText(label, btn.x + btn.w / 2, btn.y + btn.h / 2);
            };
            
            drawBtn(this.autoAdjustBtn, "Auto");
            drawBtn(this.clearChannelBtn, "Clear");
            drawBtn(this.clearAllBtn, "Reset All");
        };
        
        // Interpolation
        nodeType.prototype.interpolateCurve = function(points, num) {
            if (points.length < 2) return [[0, 0], [1, 1]];
            const result = [];
            for (let i = 0; i <= num; i++) {
                const t = i / num;
                result.push([t, Math.max(0, Math.min(1, this.catmullRom(points, t)))]);
            }
            return result;
        };
        
        nodeType.prototype.catmullRom = function(pts, x) {
            const n = pts.length - 1;
            let seg = 0;
            for (let j = 0; j < n; j++) {
                if (x >= pts[j][0] && x <= pts[j + 1][0]) { seg = j; break; }
                if (j === n - 1) seg = j;
            }
            const p0 = pts[Math.max(0, seg - 1)][1];
            const p1 = pts[seg][1];
            const p2 = pts[Math.min(n, seg + 1)][1];
            const p3 = pts[Math.min(n, seg + 2)][1];
            const x0 = pts[seg][0], x1 = pts[Math.min(n, seg + 1)][0];
            const t = x1 - x0 > 0.0001 ? (x - x0) / (x1 - x0) : 0;
            const t2 = t * t, t3 = t2 * t;
            return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3);
        };
        
        // Mouse handling
        const onMouseDown = nodeType.prototype.onMouseDown;
        nodeType.prototype.onMouseDown = function(e, pos, canvas) {
            if (!this.curveBounds || !this.curveData) return onMouseDown?.apply(this, arguments);
            
            const { x, y, size } = this.curveBounds;
            const mx = pos[0], my = pos[1];
            
            // Auto button
            if (this.autoAdjustBtn) {
                const btn = this.autoAdjustBtn;
                if (mx >= btn.x && mx <= btn.x + btn.w && my >= btn.y && my <= btn.y + btn.h) {
                    const ch = this.curveData.channel;
                    this.curveData.points[ch] = ch === "rgb" 
                        ? [[0, 0], [0.25, 0.22], [0.5, 0.5], [0.75, 0.78], [1, 1]]
                        : [[0, 0], [0.25, 0.22], [0.5, 0.52], [0.75, 0.78], [1, 1]];
                    this.syncToWidget();
                    this.setDirtyCanvas(true, true);
                    return true;
                }
            }
            
            // Clear button
            if (this.clearChannelBtn) {
                const btn = this.clearChannelBtn;
                if (mx >= btn.x && mx <= btn.x + btn.w && my >= btn.y && my <= btn.y + btn.h) {
                    this.curveData.points[this.curveData.channel] = [[0, 0], [1, 1]];
                    this.syncToWidget();
                    this.setDirtyCanvas(true, true);
                    return true;
                }
            }
            
            // Reset All button
            if (this.clearAllBtn) {
                const btn = this.clearAllBtn;
                if (mx >= btn.x && mx <= btn.x + btn.w && my >= btn.y && my <= btn.y + btn.h) {
                    this.curveData.points = { rgb: [[0,0],[1,1]], red: [[0,0],[1,1]], green: [[0,0],[1,1]], blue: [[0,0],[1,1]] };
                    this.syncToWidget();
                    const presetWidget = this.widgets?.find(w => w.name === "preset");
                    if (presetWidget) presetWidget.value = "none";
                    this.setDirtyCanvas(true, true);
                    return true;
                }
            }
            
            // Channel buttons
            if (this.channelButtons) {
                for (const btn of this.channelButtons) {
                    if (mx >= btn.x && mx <= btn.x + btn.w && my >= btn.y && my <= btn.y + btn.h) {
                        this.curveData.channel = btn.channel;
                        this.setDirtyCanvas(true, true);
                        return true;
                    }
                }
            }
            
            // Curve area
            if (mx >= x && mx <= x + size && my >= y && my <= y + size) {
                const normX = Math.max(0, Math.min(1, (mx - x) / size));
                const normY = Math.max(0, Math.min(1, 1 - (my - y) / size));
                const points = this.curveData.points[this.curveData.channel];
                
                let foundPoint = -1;
                for (let i = 0; i < points.length; i++) {
                    const px = x + points[i][0] * size;
                    const py = y + size - points[i][1] * size;
                    if (Math.sqrt((mx - px) ** 2 + (my - py) ** 2) < 10) {
                        foundPoint = i;
                        break;
                    }
                }
                
                if (e.shiftKey && foundPoint >= 0 && points.length > 2) {
                    points.splice(foundPoint, 1);
                    this.syncToWidget();
                    this.setDirtyCanvas(true, true);
                    return true;
                } else if (foundPoint >= 0) {
                    this.draggingPoint = foundPoint;
                    return true;
                } else {
                    points.push([normX, normY]);
                    points.sort((a, b) => a[0] - b[0]);
                    for (let i = 0; i < points.length; i++) {
                        if (Math.abs(points[i][0] - normX) < 0.01 && Math.abs(points[i][1] - normY) < 0.01) {
                            this.draggingPoint = i;
                            break;
                        }
                    }
                    this.syncToWidget();
                    this.setDirtyCanvas(true, true);
                    return true;
                }
            }
            
            return onMouseDown?.apply(this, arguments);
        };
        
        const onMouseMove = nodeType.prototype.onMouseMove;
        nodeType.prototype.onMouseMove = function(e, pos, canvas) {
            if (this.draggingPoint !== null && this.curveBounds && this.curveData) {
                const { x, y, size } = this.curveBounds;
                const normX = Math.max(0, Math.min(1, (pos[0] - x) / size));
                const normY = Math.max(0, Math.min(1, 1 - (pos[1] - y) / size));
                const points = this.curveData.points[this.curveData.channel];
                
                if (this.draggingPoint >= 0 && this.draggingPoint < points.length) {
                    points[this.draggingPoint] = [normX, normY];
                    points.sort((a, b) => a[0] - b[0]);
                    for (let i = 0; i < points.length; i++) {
                        if (Math.abs(points[i][0] - normX) < 0.001 && Math.abs(points[i][1] - normY) < 0.001) {
                            this.draggingPoint = i;
                            break;
                        }
                    }
                    this.syncToWidget();
                    this.setDirtyCanvas(true, true);
                }
                return true;
            }
            return onMouseMove?.apply(this, arguments);
        };
        
        const onMouseUp = nodeType.prototype.onMouseUp;
        nodeType.prototype.onMouseUp = function(e, pos, canvas) {
            if (this.draggingPoint !== null) {
                this.draggingPoint = null;
                return true;
            }
            return onMouseUp?.apply(this, arguments);
        };
    }
});
