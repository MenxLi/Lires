import { defineComponent, ref, type SetupContext } from "vue";

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