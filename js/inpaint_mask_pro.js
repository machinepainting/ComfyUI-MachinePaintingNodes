import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "MachinePainting.InpaintMaskPro",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "InpaintMaskPro") return;

        // Toggle -> widgets it controls
        const TOGGLE_MAP = {
            "use_mask":    new Set(["mask_blur", "mask_expand", "show_mask", "mask_color", "mask_opacity"]),
            "use_segs":    new Set(["segs_combine", "show_segs", "segs_color", "segs_opacity"]),
            "show_in_mask": new Set(["in_mask_color", "in_mask_opacity"]),
        };

        // Nested toggles: show_mask/show_segs only matter when parent is on,
        // but their child widgets are already gated by the parent toggle above.
        // We handle show_mask and show_segs display settings separately:
        const DISPLAY_TOGGLE_MAP = {
            "show_mask": new Set(["mask_color", "mask_opacity"]),
            "show_segs": new Set(["segs_color", "segs_opacity"]),
        };

        // All widgets that can be toggled
        const ALL_TOGGLEABLE = new Set();
        for (const s of Object.values(TOGGLE_MAP)) s.forEach(v => ALL_TOGGLEABLE.add(v));

        function updateVisibility(node) {
            const getValue = (name) => {
                const w = node.widgets?.find(w => w.name === name);
                return w ? w.value : false;
            };

            const useMask = getValue("use_mask");
            const useSegs = getValue("use_segs");
            const showInMask = getValue("show_in_mask");
            const showMask = getValue("show_mask");
            const showSegs = getValue("show_segs");

            for (const w of node.widgets) {
                if (!ALL_TOGGLEABLE.has(w.name)) continue;

                if (w._mpOrigType === undefined) {
                    w._mpOrigType = w.type;
                }

                let shouldShow = false;

                // Parent toggle gates
                if (TOGGLE_MAP["use_mask"].has(w.name)) shouldShow = useMask;
                if (TOGGLE_MAP["use_segs"].has(w.name)) shouldShow = useSegs;
                if (TOGGLE_MAP["show_in_mask"].has(w.name)) shouldShow = showInMask;

                // Nested: mask_color/mask_opacity need BOTH use_mask AND show_mask
                if (DISPLAY_TOGGLE_MAP["show_mask"]?.has(w.name)) {
                    shouldShow = useMask && showMask;
                }
                // Nested: segs_color/segs_opacity need BOTH use_segs AND show_segs
                if (DISPLAY_TOGGLE_MAP["show_segs"]?.has(w.name)) {
                    shouldShow = useSegs && showSegs;
                }

                if (shouldShow) {
                    w.type = w._mpOrigType;
                    w.computeSize = undefined;
                } else {
                    w.type = "hidden";
                    w.computeSize = () => [0, -4];
                }
            }

            const sz = node.computeSize();
            sz[0] = Math.max(sz[0], node.size[0]);
            node.setSize(sz);
            node.setDirtyCanvas(true, true);
        }

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            onNodeCreated?.apply(this, arguments);

            const self = this;
            setTimeout(() => {
                // Hook all toggle widgets
                const toggles = ["use_mask", "use_segs", "show_in_mask", "show_mask", "show_segs"];
                for (const name of toggles) {
                    const w = self.widgets?.find(w => w.name === name);
                    if (w) {
                        const orig = w.callback;
                        w.callback = function (value) {
                            orig?.call(this, value);
                            updateVisibility(self);
                        };
                    }
                }
                updateVisibility(self);
            }, 50);
        };

        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function (o) {
            onConfigure?.apply(this, arguments);
            const self = this;
            setTimeout(() => updateVisibility(self), 50);
        };
    }
});
