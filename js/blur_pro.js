import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "MachinePainting.BlurPro",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "BlurPro") return;

        // Which parameter widgets are visible per blur type
        const VISIBLE_FOR = {
            gaussian: ["radius"],
            surface:  ["radius", "threshold"],
            box:      ["radius", "iterations"],
            median:   ["radius"],
            motion:   ["angle", "distance"],
        };

        // All parameter widgets that get toggled (excludes strength/mask opts which always show)
        const TOGGLEABLE = new Set(["radius", "threshold", "angle", "distance", "iterations"]);

        function updateVisibility(node) {
            const typeWidget = node.widgets?.find(w => w.name === "blur_type");
            if (!typeWidget) return;

            const visible = new Set(VISIBLE_FOR[typeWidget.value] || VISIBLE_FOR["gaussian"]);

            for (const w of node.widgets) {
                if (!TOGGLEABLE.has(w.name)) continue;

                // Save original type once on first encounter
                if (w._mpOrigType === undefined) {
                    w._mpOrigType = w.type;
                }

                if (visible.has(w.name)) {
                    // Show
                    w.type = w._mpOrigType;
                    w.computeSize = undefined;  // let litegraph compute normally
                } else {
                    // Hide
                    w.type = "hidden";
                    w.computeSize = () => [0, -4];
                }
            }

            // Recalculate node size
            const sz = node.computeSize();
            sz[0] = Math.max(sz[0], node.size[0]);  // don't shrink width
            node.setSize(sz);
            node.setDirtyCanvas(true, true);
        }

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            onNodeCreated?.apply(this, arguments);

            const self = this;

            // Wait for widgets to be fully initialized
            setTimeout(() => {
                const typeWidget = self.widgets?.find(w => w.name === "blur_type");
                if (typeWidget) {
                    const origCallback = typeWidget.callback;
                    typeWidget.callback = function (value) {
                        origCallback?.call(this, value);
                        updateVisibility(self);
                    };
                }
                updateVisibility(self);
            }, 50);
        };

        // Restore correct visibility when loading a saved workflow
        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function (o) {
            onConfigure?.apply(this, arguments);
            const self = this;
            setTimeout(() => updateVisibility(self), 50);
        };
    }
});
