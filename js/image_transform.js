import { app } from "/scripts/app.js";

// Rotation controls shared by Image Rotate and Remove Background Pro:
//   - the "fixed" method snaps the angle slider to 45 degree increments
//   - Remove Background Pro hides its rotation widgets until the toggle is on
// Python snaps the angle too, so the result is correct even if the frontend
// widget options change shape in a future ComfyUI release.

const SNAP_DEGREES = 45;

const TARGETS = {
    ImageRotate: {
        toggle: null,
        controlled: [],
    },
    RemoveBackgroundPro: {
        toggle: "enable_rotation",
        controlled: ["rotation_method", "rotation_angle", "offset_x", "offset_y"],
    },
};

function setAngleStep(widget, fixed) {
    if (!widget || !widget.options) return;

    if (fixed) {
        // Newer frontends read step2; older ones use step / 10
        widget.options.step2 = SNAP_DEGREES;
        widget.options.step = SNAP_DEGREES * 10;
        widget.options.round = SNAP_DEGREES;
        widget.value = Math.round(widget.value / SNAP_DEGREES) * SNAP_DEGREES;
    } else {
        widget.options.step2 = 0.1;
        widget.options.step = 1;
        widget.options.round = 0.1;
    }
}

function toggleWidget(widget, show) {
    if (!widget) return;

    if (show) {
        if (widget._mpHidden) {
            widget.type = widget._mpType;
            delete widget.computeSize;
            delete widget._mpType;
            delete widget._mpHidden;
        }
    } else if (!widget._mpHidden) {
        widget._mpType = widget.type;
        widget._mpHidden = true;
        widget.type = "hidden";
        widget.computeSize = () => [0, -4];
    }
}

app.registerExtension({
    name: "MachinePainting.ImageTransform",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        const config = TARGETS[nodeData.name];
        if (!config) return;

        nodeType.prototype.mpSyncTransform = function (resize) {
            const find = (n) => this.widgets?.find((w) => w.name === n);

            const method = find("rotation_method");
            setAngleStep(find("rotation_angle"), method?.value === "fixed");

            if (config.toggle) {
                const enabled = find(config.toggle)?.value === true;
                for (const name of config.controlled) {
                    toggleWidget(find(name), enabled);
                }
                // Only reflow on an actual user toggle, so loading a workflow
                // doesn't undo a manually resized node.
                if (resize) {
                    this.setSize([this.size[0], this.computeSize()[1]]);
                }
            }

            this.setDirtyCanvas(true, true);
        };

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            onNodeCreated?.apply(this, arguments);

            const hook = (name) => {
                const w = this.widgets?.find((x) => x.name === name);
                if (!w) return;
                const original = w.callback;
                const node = this;
                w.callback = function () {
                    const r = original?.apply(this, arguments);
                    node.mpSyncTransform(true);
                    return r;
                };
            };

            hook("rotation_method");
            if (config.toggle) hook(config.toggle);

            this.mpSyncTransform(false);
        };

        // Re-apply after a saved workflow restores widget values
        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            onConfigure?.apply(this, arguments);
            this.mpSyncTransform?.(false);
        };
    },
});
