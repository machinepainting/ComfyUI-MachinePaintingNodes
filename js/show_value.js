import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";

app.registerExtension({
	name: "MachinePaintingNodes.ShowValue",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeData.name === "ShowValue") {
			console.log("ShowValue extension loaded");
			
			function populate(text) {
				console.log("ShowValue populate called with:", text);
				
				if (this.widgets) {
					for (let i = 0; i < this.widgets.length; i++) {
						this.widgets[i].onRemove?.();
					}
					this.widgets.length = 0;
				}
				
				if (!text || text.length === 0) {
					text = ["No value"];
				}
				
				for (const t of text) {
					const w = ComfyWidgets["STRING"](this, "value", ["STRING", { multiline: true }], app).widget;
					w.inputEl.readOnly = true;
					w.inputEl.style.opacity = 0.6;
					w.value = String(t);
				}
				
				requestAnimationFrame(() => {
					const sz = this.computeSize();
					if (sz[0] < this.size[0]) sz[0] = this.size[0];
					if (sz[1] < this.size[1]) sz[1] = this.size[1];
					this.onResize?.(sz);
					app.graph.setDirtyCanvas(true, false);
				});
			}

			const onExecuted = nodeType.prototype.onExecuted;
			nodeType.prototype.onExecuted = function (message) {
				console.log("ShowValue onExecuted:", message);
				onExecuted?.apply(this, arguments);
				populate.call(this, message.text);
			};

			const onConfigure = nodeType.prototype.onConfigure;
			nodeType.prototype.onConfigure = function (info) {
				onConfigure?.apply(this, arguments);
				if (info?.widgets_values?.length) {
					requestAnimationFrame(() => {
						populate.call(this, info.widgets_values);
					});
				}
			};
		}
	},
});
