/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, onWillUpdateProps, onWillUnmount, useRef } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

// لا تقم بعمل import لـ fabric، لأنه متاح في الـ window بفضل الـ manifest

export class SketchPadWidget extends Component {
    static template = "engineering_project.SketchPadWidget";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.canvasRef = useRef("canvas");
        this.colorRef = useRef("colorPicker");
        this.sizeRef = useRef("sizePicker");

        this.fabricCanvas = null;
        this.notification = useService("notification");

        onMounted(() => {
            requestAnimationFrame(() => this.initializeCanvas());
        });

        onWillUpdateProps((nextProps) => {
            // طريقة Odoo 17 للحصول على قيمة الحقل
            const currentValue = this.props.record.data[this.props.name];
            const nextValue = nextProps.record.data[nextProps.name];

            if (nextValue && nextValue !== currentValue && this.fabricCanvas) {
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
        if (!this.canvasRef.el || !this.canvasRef.el.parentElement) return;

        // استخدام window.fabric
        this.fabricCanvas = new window.fabric.Canvas(this.canvasRef.el, {
            isDrawingMode: true,
            backgroundColor: "#ffffff",
            width: this.canvasRef.el.parentElement.clientWidth - 2,
            height: 500,
        });

        this.setPenMode();
        
        // جلب القيمة الأولية للحقل
        const initialValue = this.props.record.data[this.props.name];
        this.loadImageFromValue(initialValue);
    }

    loadImageFromValue(value) {
        if (!this.fabricCanvas) return;

        this.fabricCanvas.clear();
        this.fabricCanvas.backgroundColor = "#ffffff";

        if (value) {
            window.fabric.Image.fromURL("data:image/png;base64," + value, (img) => {
                if (img.width > 0 && img.height > 0) {
                    const canvasWidth = this.fabricCanvas.width;
                    const canvasHeight = this.fabricCanvas.height;

                    const scale = Math.min(
                        canvasWidth / img.width,
                        canvasHeight / img.height
                    );

                    img.scale(scale);

                    this.fabricCanvas.setBackgroundImage(
                        img,
                        this.fabricCanvas.renderAll.bind(this.fabricCanvas)
                    );
                }
            });
        }

        this.fabricCanvas.renderAll();
    }

    setPenMode() {
        if (!this.fabricCanvas) return;

        this.fabricCanvas.isDrawingMode = true;
        this.fabricCanvas.freeDrawingBrush = new window.fabric.PencilBrush(this.fabricCanvas);

        const color = this.colorRef.el ? this.colorRef.el.value : "#000000";
        const size = this.sizeRef.el ? parseInt(this.sizeRef.el.value, 10) : 5;

        this.fabricCanvas.freeDrawingBrush.color = color;
        this.fabricCanvas.freeDrawingBrush.width = size;
    }

    setEraserMode() {
        if (!this.fabricCanvas) return;

        this.fabricCanvas.isDrawingMode = true;
        
        // المسّاحة في Fabric عبارة عن فرشاة عادية بلون أبيض
        this.fabricCanvas.freeDrawingBrush = new window.fabric.PencilBrush(this.fabricCanvas);
        this.fabricCanvas.freeDrawingBrush.color = "#ffffff";

        const size = this.sizeRef.el ? parseInt(this.sizeRef.el.value, 10) : 5;
        this.fabricCanvas.freeDrawingBrush.width = size + 10;
    }

    changeColor(ev) {
        if (!this.fabricCanvas || !this.fabricCanvas.isDrawingMode) return;
        this.fabricCanvas.freeDrawingBrush.color = ev.target.value;
    }

    changeBrushSize(ev) {
        if (!this.fabricCanvas || !this.fabricCanvas.isDrawingMode) return;
        this.fabricCanvas.freeDrawingBrush.width = parseInt(ev.target.value, 10);
    }

    clearCanvas() {
        if (!this.fabricCanvas) return;

        this.fabricCanvas.clear();
        this.fabricCanvas.backgroundColor = "#ffffff";
        this.fabricCanvas.renderAll();
    }

    async saveCanvas() {
        if (!this.fabricCanvas) return;

        const dataURL = this.fabricCanvas.toDataURL({ format: "png" });
        const base64Data = dataURL.replace(/^data:image\/(png|jpg);base64,/, "");

        // الطريقة الصحيحة لحفظ قيمة الحقل في Odoo 17
        await this.props.record.update({ [this.props.name]: base64Data });

        this.notification.add(_t("Sketch Saved Successfully!"), { type: "success" });
    }

    downloadCanvas() {
        if (!this.fabricCanvas) return;

        const link = document.createElement("a");
        link.download = `${this.props.record.data.display_name || "sketch"}.png`;
        link.href = this.fabricCanvas.toDataURL({ format: "png" });
        link.click();
    }
}

// الطريقة الصحيحة لتسجيل Widget في Odoo 17
export const sketchPadField = {
    component: SketchPadWidget,
    supportedTypes: ["binary"],
};

registry.category("fields").add("sketch_pad", sketchPadField);