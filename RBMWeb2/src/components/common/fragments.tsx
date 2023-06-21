import { defineComponent, ref } from "vue";

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
    setup(props, {}) {
        const inputButton = ref<HTMLInputElement | null>(null);
        const handleFile = (e: Event) => {
            const input = e.target as HTMLInputElement;
            if (input.files && input.files.length > 0) {
              const file = input.files[0];
              props.action(file);
            }
          }
        return () => (
            <div class="upload-button">
                <input type="file" id="upload-file" onChange={handleFile}
                    ref={inputButton} style={{display: 'none'}} />
                {
                    props.asLink ?
                    <a rel="noopener noreferrer" onClick={() => inputButton.value!.click()}>{props.text}</a>
                    :
                    <button type="button" class="btn btn-primary" onClick={() => inputButton.value!.click()}>{props.text}</button>
                }
            </div>
        )
    }
})