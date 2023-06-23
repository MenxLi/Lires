// Simple components that don't need their own file
// don't need scoped styles, or just inline styles

import { defineComponent, ref, computed, type SetupContext } from "vue";
import FloatingWindowVue from "./FloatingWindow.vue";

export const FileSelectButton = defineComponent({
    name: 'file-select-button',
    props: {
        asLink: {
            type: Boolean,
            default: false
        },
        text: {
            type: String,
            default: 'Upload'
        },
        action: {
            // callable that takes a file and returns void
            type: Function,
            required: true
        },
    },
    setup(props, context: SetupContext) {
        const inputButton = ref<HTMLInputElement | null>(null);
        const handleFile = (e: Event) => {
            const input = e.target as HTMLInputElement;
            if (input.files && input.files.length > 0) {
              const file = input.files[0];
              props.action(file);
            }
          }
        function click() { inputButton.value!.click() };
        context.expose({ click });
        return () => (
            <div class="upload-button">
                <input type="file" id="upload-file" onChange={handleFile}
                    ref={inputButton} style={{display: 'none'}} />
                {
                    props.asLink ?
                    <a class="btn upload-btn" rel="noopener noreferrer" onClick={() => inputButton.value!.click()}>{props.text}</a>
                    :
                    <button type="button" class="btn upload-btn" onClick={() => inputButton.value!.click()}>{props.text}</button>
                }
            </div>
        )
    }
})

export const TextInputWindow = defineComponent({
    name: 'text-input-window',
    props: {
        action: {
            // callable that takes a string and returns void
            type: Function,
            required: true
        },
        show: {
            type: Boolean,
            required: true
        },
        title: {
            type: String,
            default: 'Input'
        },
        text: {
            type: String,
            default: ''
        },
        placeholder: {
            type: String,
            default: ''
        },
        buttonText: {
            type: String,
            default: 'OK'
        },
    },
    emits: ["update:show"],
    setup(props, context: SetupContext) {
        const inputText = ref(props.text);
        const handleInput = (e: Event) => {
            const input = e.target as HTMLInputElement;
            inputText.value = input.value;
        }
        function submit() {
            props.action(inputText.value);
            showWindow.value = false;
        }
        const showWindow = computed({
            get() { return props.show },
            set(value: boolean) { console.log("Emit!"); context.emit('update:show', value) }
        })
        return () => (
            <FloatingWindowVue title={props.title} show={showWindow.value} onUpdate:show={()=>showWindow.value=false}>
                <div class="input-window" style={
                    {
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '1em',
                    }
                }>
                    {/* <input type="text" class="form-control" value={inputText.value} onInput={handleInput}
                        placeholder={props.placeholder} /> */}
                    <textarea class="form-control" value={inputText.value} onInput={handleInput} placeholder={props.placeholder} 
                        style={{
                            width: '100%',
                        }}/>
                    <button type="button" class="btn" onClick={submit}>{props.buttonText}</button>
                </div>
            </FloatingWindowVue>
        )
    }
})

export const EditableParagraph = defineComponent({
    name: 'editable-paragraph',
    props: {
        style: {
            type: Object,
            default: () => ({})
        }
    },
    emits: ["finish", "change"],
    // expose: ['setText', 'setEditable', 'contains', 'innerText'],
    setup(props, context: SetupContext) {
        const p = ref<HTMLParagraphElement | null>(null);
        const setText = (value: string) => {
            p.value!.innerText = value;
        };
        const setEditable = (value: boolean) => {
            p.value!.contentEditable = value.toString();
        };
        // Emulates native paragraph element properties
        const contains = (value: Node) => {
            return p.value!.contains(value);
        }
        const innerText = computed({
            get() { return p.value!.innerText },
            set(value: string) { p.value!.innerText = value }
        });

        context.expose({ setText, setEditable, contains, innerText });

        const handleInput = () => {
            context.emit('change', p.value!.innerText);
        }
        const handleBlur = () => {
            context.emit('finish', p.value!.innerText);
        }
        // checks if there is a default slot defined within the component's context (context.slots.default) and 
        // if so, it calls the slot function (context.slots.default()).
        return () => (
            <p class="editable-paragraph" contenteditable="true" ref={p}
                onInput={handleInput} onBlur={handleBlur} style={props.style}>
                {context.slots.default && context.slots.default()}
            </p>
        )
    }
})