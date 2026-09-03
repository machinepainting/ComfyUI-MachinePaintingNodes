import { app } from "/scripts/app.js";

// Rotation controls shared by Transform & Rotate Pro and Remove Background Pro:
//   - the "fixed" method snaps the angle slider to 45 degree increments
//   - Remove Background Pro hides its rotation widgets until the toggle is on
// Python snaps the angle too, so the result is correct even if the frontend
// widget options change shape in a future ComfyUI release.

const SNAP_DEGREES = 45;

const TARGETS = {
    MP_ImageTransform: {
        toggle: null,
        controlled: [],
    },
    RemoveBackgroundPro: {
        toggle: "enable_rotation",
        controlled: ["rotation_method", "rotation_angle", "zoom", "offset_x", "offset_y"],
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

// Hide via the boolean `hidden` flag. That is what the frontend actually
// checks: isWidgetVisible() and getLayoutWidgets() both key off it, and a
// hidden widget is dropped from the layout pass entirely.
//
// Do NOT hide by setting `type = "hidden"` - there is no such widget type.
// The widget stays "visible" to the layout pass, gets laid out at zero
// height, and draws on top of the widgets below it, which pushes the node's
// preview image up over the sliders.
function toggleWidget(widget, show) {
    if (!widget) return;
    widget.hidden = !show;
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
                // doesn't undo a manually resized node. expandToFitContent is
                // litegraph's own helper: it grows the node to clear the newly
                // shown widgets and never shrinks it, so the preview image
                // keeps the room it already had.
                if (resize) this.expandToFitContent?.();
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
