import { app } from "../../../scripts/app.js";

// Mega Slider per-slider properties support
app.registerExtension({
    name: "MachinePaintingNodes.MegaSlider",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (["MegaSliderX1", "MegaSliderX3", "MegaSliderX6", "MegaSliderX12"].includes(nodeData.name)) {
            
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                onNodeCreated?.apply(this, arguments);
                
                const sliderCount = nodeData.name === "MegaSliderX1" ? 1 :
                                   nodeData.name === "MegaSliderX3" ? 3 : 
                                   nodeData.name === "MegaSliderX6" ? 6 : 12;
                
                // Add properties for individual slider overrides
                this.properties = this.properties || {};
                for (let i = 1; i <= sliderCount; i++) {
                    if (this.properties[`slider_${i}_min`] === undefined) {
                        this.properties[`slider_${i}_min`] = null;
                    }
                    if (this.properties[`slider_${i}_max`] === undefined) {
                        this.properties[`slider_${i}_max`] = null;
                    }
                    if (this.properties[`slider_${i}_step`] === undefined) {
                        this.properties[`slider_${i}_step`] = null;
                    }
                }
            };
        }
    },
    
    async nodeCreated(node) {
        if (["MegaSliderX1", "MegaSliderX3", "MegaSliderX6", "MegaSliderX12"].includes(node.comfyClass)) {
            
            const getSliderSettings = (num) => {
                const propMin = node.properties?.[`slider_${num}_min`];
                const propMax = node.properties?.[`slider_${num}_max`];
                const propStep = node.properties?.[`slider_${num}_step`];
                
                return {
                    min: (propMin !== null && propMin !== undefined) ? propMin : -10000,
                    max: (propMax !== null && propMax !== undefined) ? propMax : 10000,
                    step: (propStep !== null && propStep !== undefined) ? propStep : 0.01,
                };
            };
            
            const updateSliders = () => {
                node.widgets?.forEach(widget => {
                    if (widget.name?.startsWith("slider_")) {
                        const num = widget.name.split("_")[1];
                        const settings = getSliderSettings(num);
                        
                        widget.options = widget.options || {};
                        widget.options.min = settings.min;
                        widget.options.max = settings.max;
                        widget.options.step = settings.step;
                        
                        // Clamp and snap current value
                        let val = widget.value;
                        val = Math.round(val / settings.step) * settings.step;
                        val = Math.max(settings.min, Math.min(settings.max, val));
                        val = Math.round(val * 100000) / 100000;
                        widget.value = val;
                    }
                });
                
                node.setDirtyCanvas?.(true);
            };
            
            // Add callback to each slider to enforce snapping on change
            const setupSliderCallbacks = () => {
                node.widgets?.forEach(widget => {
                    if (widget.name?.startsWith("slider_")) {
                        const num = widget.name.split("_")[1];
                        const origCallback = widget.callback;
                        
                        widget.callback = function(v) {
                            const settings = getSliderSettings(num);
                            
                            v = Math.round(v / settings.step) * settings.step;
                            v = Math.max(settings.min, Math.min(settings.max, v));
                            v = Math.round(v * 100000) / 100000;
                            
                            widget.value = v;
                            origCallback?.call(this, v);
                        };
                    }
                });
            };
            
            // Watch for property changes
            const onPropertyChanged = node.onPropertyChanged;
            node.onPropertyChanged = function(name, value) {
                onPropertyChanged?.apply(this, arguments);
                if (name.includes("slider_") && (name.includes("_min") || name.includes("_max") || name.includes("_step"))) {
                    updateSliders();
                }
            };
            
            setTimeout(() => {
                setupSliderCallbacks();
                updateSliders();
            }, 100);
        }
    }
});
