import { app } from "../../../scripts/app.js";

// Mega Slider per-slider properties and master input support
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
            
            // Get master settings from connected node
            const getMasterSettings = () => {
                const masterInput = node.inputs?.find(i => i.name === "master");
                if (masterInput && masterInput.link !== null) {
                    const linkInfo = app.graph.links[masterInput.link];
                    if (linkInfo) {
                        const masterNode = app.graph.getNodeById(linkInfo.origin_id);
                        if (masterNode && masterNode.comfyClass === "MegaSliderMasterValue") {
                            const minWidget = masterNode.widgets?.find(w => w.name === "min_value");
                            const maxWidget = masterNode.widgets?.find(w => w.name === "max_value");
                            const stepWidget = masterNode.widgets?.find(w => w.name === "step");
                            return {
                                min: minWidget?.value ?? 0,
                                max: maxWidget?.value ?? 1,
                                step: stepWidget?.value ?? 0.01,
                                connected: true
                            };
                        }
                    }
                }
                return { min: -10000, max: 10000, step: 0.01, connected: false };
            };
            
            const getSliderSettings = (num) => {
                const master = getMasterSettings();
                
                // Check for per-slider property overrides
                const propMin = node.properties?.[`slider_${num}_min`];
                const propMax = node.properties?.[`slider_${num}_max`];
                const propStep = node.properties?.[`slider_${num}_step`];
                
                return {
                    min: (propMin !== null && propMin !== undefined) ? propMin : master.min,
                    max: (propMax !== null && propMax !== undefined) ? propMax : master.max,
                    step: (propStep !== null && propStep !== undefined) ? propStep : master.step,
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
            
            // Store updateSliders on node for external access
            node.updateMegaSliders = updateSliders;
            
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
            
            // Watch for connection changes
            const onConnectionsChange = node.onConnectionsChange;
            node.onConnectionsChange = function(type, index, connected, link_info) {
                onConnectionsChange?.apply(this, arguments);
                updateSliders();
            };
            
            setTimeout(() => {
                setupSliderCallbacks();
                updateSliders();
            }, 100);
        }
        
        // Watch for changes on MegaSliderMasterValue to update connected nodes
        if (node.comfyClass === "MegaSliderMasterValue") {
            const updateConnectedSliders = () => {
                // Find all nodes connected to this master's output
                const outputLinks = node.outputs?.[0]?.links || [];
                for (const linkId of outputLinks) {
                    const linkInfo = app.graph.links[linkId];
                    if (linkInfo) {
                        const targetNode = app.graph.getNodeById(linkInfo.target_id);
                        if (targetNode && ["MegaSliderX1", "MegaSliderX3", "MegaSliderX6", "MegaSliderX12"].includes(targetNode.comfyClass)) {
                            targetNode.updateMegaSliders?.();
                        }
                    }
                }
            };
            
            // Add callbacks to master widgets
            setTimeout(() => {
                node.widgets?.forEach(widget => {
                    const origCallback = widget.callback;
                    widget.callback = function(v) {
                        origCallback?.call(this, v);
                        updateConnectedSliders();
                    };
                });
            }, 100);
        }
    }
});
