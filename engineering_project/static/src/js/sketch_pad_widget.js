/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, onWillUpdateProps, onWillUnmount, useRef, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class SketchPadWidget extends Component {
    static template = "engineering_project.SketchPadWidget";
    static props = {
        ...standardFieldProps,
        widget: { type: String, optional: true },
    };

    setup() {
        // FIX 1: Change to reference a container instead of the canvas directly
        this.canvasContainerRef = useRef("canvasContainer"); 
        
        this.colorRef = useRef("colorPicker");
        this.sizeRef = useRef("sizePicker");
        this.textInputRef = useRef("textInput");

        this.fabricCanvas = null;
        this.notification = useService("notification");
        this.currentMode = useState({ mode: 'pen' });

        this.loadedValue = null;

        onMounted(() => {
            requestAnimationFrame(() => this.initializeCanvas());
        });

        onWillUpdateProps((nextProps) => {
            const nextValue = nextProps.record.data[nextProps.name];
            if (nextValue && nextValue !== this.loadedValue && this.fabricCanvas) {
                this.loadImageFromValue(nextValue);
            }
        });

        onWillUnmount(() => {
            if (this.fabricCanvas) {
                this.fabricCanvas.dispose();
                this.fabricCanvas = null;
            }
        });
    }

    initializeCanvas() {
        const container = this.canvasContainerRef.el;
        if (!container) return;

        // FIX 2: Clear the container and dynamically create the canvas. 
        // This prevents OWL from tracking and destroying Fabric's elements.
        container.innerHTML = "";
        const canvasEl = document.createElement("canvas");
        container.appendChild(canvasEl);

        this.fabricCanvas = new window.fabric.Canvas(canvasEl, {
            isDrawingMode: false,
            backgroundColor: "#ffffff",
            width: container.clientWidth - 2, // Take width from container
            height: 500,
        });

        this.setPenMode();

        const initialValue = this.props.record.data[this.props.name];
        this.loadImageFromValue(initialValue);

        this.fabricCanvas.on('selection:created', (e) => this.handleSelection(e));
        this.fabricCanvas.on('selection:updated', (e) => this.handleSelection(e));
        this.fabricCanvas.on('selection:cleared', (e) => this.handleSelection(e));
    }

    handleSelection(e) {
        if (e.target && e.target.type === 'i-text') {
            this.currentMode.mode = 'text_edit';
        } else {
            if (this.currentMode.mode === 'text_edit') {
                this.setPenMode();
            }
        }
    }

    loadImageFromValue(value) {
        if (!this.fabricCanvas) return;

        this.fabricCanvas.clear();
        this.fabricCanvas.backgroundColor = "#ffffff";
        this.loadedValue = value;

        if (value) {
            window.fabric.Image.fromURL("data:image/png;base64," + value, (img) => {
                if (img.width > 0 && img.height > 0) {
                    this.fabricCanvas.setBackgroundImage(
                        img,
                        this.fabricCanvas.renderAll.bind(this.fabricCanvas),
                        {
                            originX: 'center',
                            originY: 'center',
                            left: this.fabricCanvas.width / 2,
                            top: this.fabricCanvas.height / 2,
                            scaleX: this.fabricCanvas.width / img.width,
                            scaleY: this.fabricCanvas.height / img.height,
                        }
                    );
                }
            }, { crossOrigin: 'anonymous' });
        }
        this.fabricCanvas.renderAll();
    }

    setPenMode() {
        if (!this.fabricCanvas) return;
        this.currentMode.mode = 'pen';
        this.fabricCanvas.isDrawingMode = true;
        this.fabricCanvas.freeDrawingBrush = new window.fabric.PencilBrush(this.fabricCanvas);
        this.fabricCanvas.selection = true;
        this.fabricCanvas.forEachObject(obj => obj.set({ selectable: true, evented: true }));
        
        const color = this.colorRef.el ? this.colorRef.el.value : "#000000";
        const size = this.sizeRef.el ? parseInt(this.sizeRef.el.value, 10) : 5;

        this.fabricCanvas.freeDrawingBrush.color = color;
        this.fabricCanvas.freeDrawingBrush.width = size;
        this.fabricCanvas.renderAll();
    }

    setEraserMode() {
        if (!this.fabricCanvas) return;
        this.currentMode.mode = 'eraser';
        this.fabricCanvas.isDrawingMode = true;
        this.fabricCanvas.selection = false;
        this.fabricCanvas.forEachObject(obj => obj.set({ selectable: false, evented: false }));
        
        this.fabricCanvas.freeDrawingBrush = new window.fabric.PencilBrush(this.fabricCanvas);
        this.fabricCanvas.freeDrawingBrush.color = "#ffffff";
        const size = this.sizeRef.el ? parseInt(this.sizeRef.el.value, 10) : 15;
        this.fabricCanvas.freeDrawingBrush.width = size + 10;
        this.fabricCanvas.renderAll();
    }

    setTextMode() {
        if (!this.fabricCanvas) return;
        this.currentMode.mode = 'text';
        this.fabricCanvas.isDrawingMode = false;
        this.fabricCanvas.selection = true;
        this.fabricCanvas.forEachObject(obj => obj.set({ selectable: true, evented: true }));

        this.fabricCanvas.off('mouse:down');
        this.fabricCanvas.on('mouse:down', this.addTextOnClick.bind(this));
        this.fabricCanvas.renderAll();
    }

    addTextOnClick(options) {
        if (this.currentMode.mode !== 'text' || !this.fabricCanvas || (options.target && options.target.selectable)) return;

        const pointer = this.fabricCanvas.getPointer(options.e);
        const textValue = this.textInputRef.el ? this.textInputRef.el.value : _t("Enter Text");
        const textColor = this.colorRef.el ? this.colorRef.el.value : "#000000";
        const textSize = this.sizeRef.el ? parseInt(this.sizeRef.el.value, 10) + 10 : 20;

        const iText = new window.fabric.IText(textValue, {
            left: pointer.x,
            top: pointer.y,
            fontFamily: 'arial',
            fill: textColor,
            fontSize: textSize,
            editable: true,
            selectable: true,
            evented: true,
        });
        this.fabricCanvas.add(iText);
        this.fabricCanvas.setActiveObject(iText);
        this.fabricCanvas.renderAll();
        
        this.currentMode.mode = 'text_edit';
        if (this.textInputRef.el) this.textInputRef.el.value = "";
    }

    changeColor(ev) {
        if (!this.fabricCanvas) return;
        if (this.currentMode.mode === 'pen' && this.fabricCanvas.isDrawingMode) {
            this.fabricCanvas.freeDrawingBrush.color = ev.target.value;
        } else {
            const activeObject = this.fabricCanvas.getActiveObject();
            if (activeObject && activeObject.type === 'i-text') {
                activeObject.set({ fill: ev.target.value });
                this.fabricCanvas.renderAll();
            }
        }
    }

    changeBrushSize(ev) {
        if (!this.fabricCanvas) return;
        const size = parseInt(ev.target.value, 10);
        if (this.currentMode.mode === 'pen' && this.fabricCanvas.isDrawingMode) {
            this.fabricCanvas.freeDrawingBrush.width = size;
        } else if (this.currentMode.mode === 'eraser' && this.fabricCanvas.isDrawingMode) {
            this.fabricCanvas.freeDrawingBrush.width = size + 10;
        } else {
            const activeObject = this.fabricCanvas.getActiveObject();
            if (activeObject && activeObject.type === 'i-text') {
                activeObject.set({ fontSize: size + 10 });
                this.fabricCanvas.renderAll();
            }
        }
    }

    clearCanvas() {
        if (!this.fabricCanvas) return;
        this.fabricCanvas.clear();
        this.fabricCanvas.backgroundColor = "#ffffff";
        this.fabricCanvas.renderAll();
        this.notification.add(_t("Canvas Cleared!"), { type: "info" });
    }

    async saveCanvas() {
        if (!this.fabricCanvas) return;
        if (this.fabricCanvas.getActiveObject() && this.fabricCanvas.getActiveObject().isEditing) {
            this.fabricCanvas.getActiveObject().exitEditing();
        }
        this.fabricCanvas.discardActiveObject();
        this.fabricCanvas.renderAll();

        const dataURL = this.fabricCanvas.toDataURL({ format: "png", multiplier: 1 });
        const base64Data = dataURL.replace(/^data:image\/(png|jpg);base64,/, "");

        this.loadedValue = base64Data;

        await this.props.record.update({ [this.props.name]: base64Data });
        this.notification.add(_t("Sketch Saved Successfully!"), { type: "success" });
    }

    downloadCanvas() {
        if (!this.fabricCanvas) return;
        if (this.fabricCanvas.getActiveObject() && this.fabricCanvas.getActiveObject().isEditing) {
            this.fabricCanvas.getActiveObject().exitEditing();
        }
        this.fabricCanvas.discardActiveObject();
        this.fabricCanvas.renderAll();

        const link = document.createElement("a");
        link.download = `${this.props.record.data.name || "sketch"}.png`;
        link.href = this.fabricCanvas.toDataURL({ format: "png", multiplier: 2 });
        link.click();
    }
}

export const sketchPadField = {
    component: SketchPadWidget,
    supportedTypes: ["binary"],
};

registry.category("fields").add("sketch_pad_editor", sketchPadField);